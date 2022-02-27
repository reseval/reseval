import datetime
import itertools
import json
import re
from hashlib import md5
from pathlib import Path

import boto3
import xmltodict as xmltodict
import uuid

import reseval

###############################################################################
# Constants
###############################################################################


# HIT preview URL
PREVIEW_URL = {
    'development': 'https://workersandbox.mturk.com/mturk/preview?groupId={}',
    'production': 'https://worker.mturk.com/mturk/preview?groupId={}'}

# HIT creation URL
URL = {
    'development': 'https://mturk-requester-sandbox.us-east-1.amazonaws.com',
    'production': 'https://mturk-requester.us-east-1.amazonaws.com'}

# Survey XML
XML_FILE = reseval.ASSETS_DIR / 'survey.xml'


###############################################################################
# Amazon Mechanical Turk crowdsourcing interface
###############################################################################


def active(config, credentials):
    """Returns True if the evaluation is still running"""
    return progress(credentials) < config['participants']


def create(config, url, production=False):
    """Create a HIT"""
    # Connect to MTurk
    mturk = connect(production)

    # Get survey XML and link to our external survey
    with open(reseval.ASSETS_DIR / 'survey.xml') as file:
        question = file.read().format(url)

    # Create HIT
    cfg = config['crowdsource']
    hit = mturk.create_hit(
        Title=cfg['title'],
        Description=cfg['description'],
        Keywords=cfg['keywords'],
        Reward=cfg['payment']['base'],
        MaxAssignments=config['participants'],
        LifetimeInSeconds=cfg['duration']['total'],
        AssignmentDurationInSeconds=cfg['duration']['assignment'],
        AutoApprovalDelayInSeconds=cfg['duration']['autoapprove'],
        QualificationRequirements=qualifications(config),
        Question=question)

    # Log HIT
    hit_id = hit['HIT']['HITId']
    url_key = 'production' if production else 'development'
    preview_url = PREVIEW_URL[url_key].format(hit['HIT']['GroupId'])
    print(f'Created HIT {hit_id}. You can preview your HIT at {preview_url}.')

    # Return crowdsource credentials
    return {'HIT_ID': hit_id, 'PRODUCTION': production}


def destroy(credentials):
    """Delete a HIT"""
    # first check if hit exists
    if credentials['HIT_ID'] not in list_all_hit(credentials):
        print('Warning: the hit you are trying to destroy no longer exist, skipping...')
    else:
        # Connect to MTurk
        mturk = connect(credentials['PRODUCTION'])

        # Delete HIT
        response = mturk.delete_hit(HITId=credentials['HIT_ID'])


def extend(credentials, participants, name):
    """Extend a HIT with additional assignments"""
    # Connect to MTurk
    mturk = connect(credentials['PRODUCTION'])

    token_file = Path(reseval.EVALUATION_DIRECTORY + f'/{name}/tokens.json')

    if token_file.exists():
        # last response was bad, retry using same token
        with open(token_file) as json_file:
            unique_token = json.load(json_file)['extend_token']
    else:
        # create a new unique token and write it to token.json
        unique_token = str(uuid.uuid4())
        data = {'extend_token': unique_token}
        with open(token_file, 'w') as json_file:
            json.dump(data, json_file)

    # Extend HIT
    try:
        response = mturk.create_additional_assignments_for_hit(
            HITId=credentials['HIT_ID'],
            UniqueRequestToken=unique_token,
            NumberOfAdditionalAssignments=participants)
    except Exception as e:
        # if unique_token is in the exception args, we assume it is because the token is already used.
        if re.search(re.escape(unique_token), e.args[0]) is not None:
            # delete the token
            token_file.unlink(True)
        else:
            raise e


def paid(credentials):
    """Returns True if all participants have been paid"""
    return not assignments(credentials, ['Submitted'])


def pay(config, credentials):
    """Evaluate and pay participants"""
    # Get assignment IDs and completion codes
    mturk_results = results(credentials)

    # Get participants and responses from database
    reseval.database.download(
        config['name'],
        reseval.EVALUATION_DIRECTORY / config['name'] / 'tables',
        ['participants', 'responses'])
    participants = reseval.load.participants(config['name'])
    responses = reseval.load.responses(config['name'])

    # Match participants with responses
    participant_responses = {}
    for participant in participants:
        pid = participant['ID']
        participant_responses[pid] = (
                participant |
                {'responses': filter(responses, lambda x: x['ID'] == pid)})

    # Iterate over participants
    for result in mturk_results:

        # Find matching completion code
        match = None
        for pid in participant_responses:
            if (participant_responses[pid]['completion_code'] ==
                    result['completion_code']):
                match = pid

        # Only process payment if the participant has not already been paid
        if result['status'] == 'Submitted':

            # Reject work if the completion codes do not match
            if match is None and result['status'] == 'Submitted':
                reject(
                    credentials,
                    result['assignment_id'],
                    'Survey completion code does not match')
                continue

            # Approve work
            approve(credentials, result['assignment_id'])

            # If they passed prescreening and completed evaluation, give
            # the participant a bonus
            if (len(participant_responses[pid]['responses']) ==
                    config['samples_per_participant']):
                bonus(config, credentials, result['assignment_id'])


def progress(credentials):
    """Retrieve the number of participants that have taken the evaluation"""
    return assignments(credentials)['NumResults']


def resume(config, credentials):
    """Resume a subjective evaluation"""
    # Connect to MTurk
    mturk = connect(credentials['PRODUCTION'])

    # Resume HIT
    timedelta = datetime.timedelta(
        0,
        config['crowdsource']['duration']['total'])
    response = mturk.update_expiration_for_hit(
        HITId=credentials['HIT_ID'],
        ExpireAt=datetime.datetime.now() + timedelta)


def stop(credentials):
    """Stop an active HIT"""
    # Connect to MTurk
    mturk = connect(credentials['PRODUCTION'])

    # Stop HIT
    response = mturk.update_expiration_for_hit(
        HITId=credentials['HIT_ID'],
        ExpireAt=datetime.datetime.now())


###############################################################################
# Utilities
###############################################################################

# return all hit_id of requester in an string list. e.g.: ['1234566', '56819382']
def list_all_hit(credentials):
    mturk = connect(credentials['PRODUCTION'])
    res = mturk.list_hits()
    result = []
    if res['HITs']:
        result = res['HITs']
        result = map(lambda x: x['HITId'], result)
    return list(result)


def approve(credentials, assignment_id):
    """Approve an assignment"""
    # Connect to MTurk
    mturk = connect(credentials['PRODUCTION'])

    if mturk.get_assignment(AssignmentId=assignment_id)['Assignment']['AssignmentStatus'] == 'Approved':
        pass
    else:
        # Approve assignment
        response = mturk.approve_assignment(AssignmentId=assignment_id)


def assignments(credentials, statuses=None):
    """Retrieve a list of all assignments for a HIT"""
    # Default to all statuses
    statuses = (
        ['Submitted' | 'Approved' | 'Rejected']
        if statuses is None else statuses)

    # Connect to MTurk
    mturk = connect(credentials['PRODUCTION'])

    # Download results
    iterator = mturk.Paginator.ListAssignmentsForHIT.paginate(
        HITId=credentials['HIT_ID'],
        AssignmentStatuses=statuses)

    # Get all assignments
    return itertools.chain.from_iterable(iterator)


def bonus(config, credentials, assignment_id, worker_id):
    # use md5(assignment_id) as Unique token, because we would send_bonus only once per assignment
    unique_token = md5(assignment_id.encode('utf-8')).hexdigest()
    """Give a participant a bonus"""
    # Connect to MTurk
    mturk = connect(credentials['PRODUCTION'])
    try:
        # Approve assignment
        response = mturk.send_bonus(
            WorkerId=worker_id,
            BonusAmount=config['crowdsource']['payment']['completion'],
            AssignmentId=assignment_id,
            UniqueRequestToken=unique_token,
            Reason='Passed prescreening and completed evaluation. Thank you!')

    except Exception as e:
        # if exception args contain md5(assignment_id), we assume this assignment has bonus already.
        if re.search(re.escape(unique_token), e.args[0]) is not None:
            pass
        else:
            raise e


def connect(production=False):
    """Connect to MTurk"""
    return boto3.client(
        'mturk',
        region_name='us-east-1',
        endpoint_url=URL['production' if production else 'development'])


def qualifications(config):
    """Format participant qualificiations"""
    qualifications = []

    # Country of origin
    cfg = config['crowdsource']['filter']
    if 'countries' in cfg:
        locales = [{'Country': country} for country in cfg['countries']]
        qualifications.append({
            'QualificationTypeId': '00000000000000000071',
            'Comparator': 'In',
            'LocaleValues': locales,
            'RequiredToPreview': True})

    # Number of approved tasks
    if 'approved_tasks' in cfg:
        qualifications.append({
            'QualificationTypeId': '00000000000000000040',
            'Comparator': 'GreaterThan',
            'IntegerValues': [cfg['approved_tasks']],
            'RequiredToPreview': True})

    # Approval rating
    if 'approval_rating' in cfg:
        qualifications.append({
            'QualificationTypeId': '000000000000000000L0',
            'Comparator': 'GreaterThanOrEqualTo',
            'IntegerValues': [cfg['approval_rating']],
            'RequiredToPreview': True})

    return qualifications


def reject(credentials, assignment_id, reason):
    """Reject assignment by ID"""
    # Connect to MTurk
    mturk = connect(credentials['PRODUCTION'])
    # skip if already rejected
    if mturk.get_assignment(AssignmentId=assignment_id)['Assignment']['AssignmentStatus'] == 'Rejected':
        pass
    else:
        # Reject assignment
        response = mturk.reject_assignment(
            AssignmentId=assignment_id,
            RequesterFeedback=reason)


def results(credentials):
    """Get a list of all assignment IDs and completion codes"""
    result = []
    for assignment in assignments(credentials):
        # Parse XML
        xml_doc = xmltodict.parse(assignment['Answer'])

        # Get completion code
        completion_code = xml_doc['QuestionFormAnswers']['Answer']['FreeText']

        # Format result
        result.append({
            'assignment_id': assignment['AssignmentId'],
            'completion_code': completion_code,
            'status': assignment['AssignmentStatus'],
            'worker_id': assignment['WorkerId']})

    return result
