import datetime
import itertools
import json
import os
import re
from hashlib import md5
from pathlib import Path
import time

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
    return status(config, credentials) not in ['Reviewing', 'Reviewable']


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
        Reward=str(cfg['payment']['base']),
        MaxAssignments=config['participants'],
        LifetimeInSeconds=cfg['duration']['total'],
        AssignmentDurationInSeconds=cfg['duration']['assignment'],
        AutoApprovalDelayInSeconds=cfg['duration']['autoapprove'],
        QualificationRequirements=qualifications(config),
        Question=question)

    # Log HIT
    hit_id = hit['HIT']['HITId']
    url_key = 'production' if production else 'development'
    preview_url = PREVIEW_URL[url_key].format(hit['HIT']['HITGroupId'])
    print(f'Created HIT {hit_id}. You can view your HIT at {preview_url}')

    # Return crowdsource credentials
    return {'HIT_ID': hit_id, 'PRODUCTION': production}


def destroy(config, credentials):
    """Delete a HIT"""
    if credentials['HIT_ID'] in list_hits(credentials):
        # Connect to MTurk
        mturk = connect(credentials['PRODUCTION'])

        # Stop HIT
        mturk.update_expiration_for_hit(
            HITId=credentials['HIT_ID'],
            ExpireAt=datetime.datetime(2000, 1, 1).timestamp())

        # The HIT can only be deleted once the status is one of 'Reviewing' or
        # 'Reviewable'. Otherwise, an error will be thrown. Sometimes, it takes
        # a couple of seconds after the update call above for the status to
        # change to 'Reviewable'. This loop is a time buffer that gives MTurk
        # 90 seconds to update the status. If the status doesn't change, the
        # most likely explanation is that someone is still taking the
        # evaluation.
        start = datetime.datetime.now()
        while (datetime.datetime.now() - start).total_seconds() < 90:
            if not active(config, credentials):
                break
            time.sleep(5)

        # Delete HIT
        mturk.delete_hit(HITId=credentials['HIT_ID'])


def extend(credentials, participants, name):
    """Extend a HIT with additional assignments"""
    # Connect to MTurk
    mturk = connect(credentials['PRODUCTION'])

    # Location to save unique response token
    token_file = Path(reseval.EVALUATION_DIRECTORY / name / 'tokens.json')

    try:

        # Last response was bad. Retry using same token.
        with open(token_file) as json_file:
            unique_token = json.load(json_file)['extend_token']

    except FileNotFoundError:

        # Create and save a new unique token
        unique_token = str(uuid.uuid4())
        data = {'extend_token': unique_token}
        with open(token_file, 'w') as json_file:
            json.dump(data, json_file)

    try:

        # Extend HIT
        mturk.create_additional_assignments_for_hit(
            HITId=credentials['HIT_ID'],
            UniqueRequestToken=unique_token,
            NumberOfAdditionalAssignments=participants)

    except Exception as exception:

        # If the token is in the exception args, we assume the token has been
        # used and delete the token
        if re.search(re.escape(unique_token), exception.args[0]) is not None:
            token_file.unlink(True)

        else:
            raise exception


def exists(config, credentials):
    """Returns true if the evaluation exists"""
    return credentials['HIT_ID'] in list_hits(credentials)


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
                {'responses': list(filter(
                    lambda x: x['Participant'] == pid,
                    responses))})

    # Iterate over participants
    for result in mturk_results:

        # Find matching completion code
        match = None
        for pid in participant_responses:
            participant_code = participant_responses[pid]['CompletionCode']
            completion_code = result['completion_code']
            if participant_code == completion_code:
                match = pid

        # Only process payment if the participant has not already been paid
        if result['status'] == 'Submitted':

            # Reject work if the completion codes do not match
            if match is None and result['status'] == 'Submitted':
                reject(
                    credentials,
                    result['assignment_id'],
                    'Survey completion code does not match')
                block(
                    config,
                    credentials,
                    result['worker_id'],
                    'Survey completion code does not match')
                continue

            # Approve work
            approve(credentials, result['assignment_id'])

            # Block workers who do not complete evaluations
            if (
                len(participant_responses[match]['responses']) !=
                config['samples_per_participant']
            ):
                block(
                    config,
                    credentials,
                    result['worker_id'],
                    'Incomplete evaluation')

            # If they passed prescreening and completed evaluation, give
            # the participant a bonus
            else:
                bonus(config, credentials, result['assignment_id'])


def progress(credentials):
    """Retrieve the number of participants that have taken the evaluation"""
    return len(assignments(credentials))


###############################################################################
# Utilities
###############################################################################


def approve(credentials, assignment_id):
    """Approve an assignment"""
    # Connect to MTurk
    mturk = connect(credentials['PRODUCTION'])

    # Skip if already processed
    assignment = mturk.get_assignment(AssignmentId=assignment_id)
    if assignment['Assignment']['AssignmentStatus'] == 'Submitted':
        # Approve assignment
        mturk.approve_assignment(AssignmentId=assignment_id)


def assignments(credentials, statuses=None):
    """Retrieve a list of all assignments for a HIT"""
    # Default to all statuses
    statuses = (
        ['Submitted', 'Approved', 'Rejected']
        if statuses is None else statuses)

    # Connect to MTurk
    mturk = connect(credentials['PRODUCTION'])

    # Download results
    paginator = mturk.get_paginator('list_assignments_for_hit')
    iterator = paginator.paginate(
        HITId=credentials['HIT_ID'],
        AssignmentStatuses=statuses)

    # Get assignments
    return list(itertools.chain.from_iterable(
        page['Assignments'] for page in iterator))


def block(config, credentials, worker_id, reason):
    """Block a worker"""
    # Connect to MTurk
    mturk = connect(credentials['PRODUCTION'])

    # Block worker
    mturk.create_worker_block(WorkerId=worker_id, Reason=reason)


def bonus(config, credentials, assignment_id):
    """Give a participant a bonus"""
    # We only send one bonus per assignment, so we use the assignment ID to
    # generate the unique token
    unique_token = md5(assignment_id.encode('utf-8')).hexdigest()

    # Connect to MTurk
    mturk = connect(credentials['PRODUCTION'])

    # Get worker ID
    assignment = mturk.get_assignment(AssignmentId=assignment_id)
    worker_id = assignment['Assignment']['WorkerId']

    try:

        # Approve assignment
        mturk.send_bonus(
            WorkerId=worker_id,
            BonusAmount=str(config['crowdsource']['payment']['completion']),
            AssignmentId=assignment_id,
            UniqueRequestToken=unique_token,
            Reason='Passed prescreening and completed evaluation. Thank you!')

    except Exception as exception:

        # If the token is in the exception args, we assume the worker has
        # already been given a bonus
        if re.search(re.escape(unique_token), exception.args[0]) is None:
            raise exception


def connect(production=False):
    """Connect to MTurk"""
    # Load API keys
    reseval.load.api_keys()

    # Connect to MTurk
    return boto3.Session(
        aws_access_key_id=os.environ['AWSAccessKeyId'],
        aws_secret_access_key=os.environ['AWSSecretKey']
    ).client(
        'mturk',
        region_name='us-east-1',
        endpoint_url=URL['production' if production else 'development'])


def list_hits(credentials):
    """List the IDs of all HITs on MTurk"""
    # Connect to S3
    mturk = connect(credentials['PRODUCTION'])

    # Get list of HITs
    iterator = mturk.get_paginator('list_hits').paginate()
    responses = list(iterator)

    # Extract HIT Ids
    if responses:
        return list(itertools.chain.from_iterable([
            [hit['HITId'] for hit in response['HITs']]
            for response in responses]))

    return []


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
    if 'approved_tasks' in cfg and cfg['approved_tasks'] > 0:
        qualifications.append({
            'QualificationTypeId': '00000000000000000040',
            'Comparator': 'GreaterThan',
            'IntegerValues': [cfg['approved_tasks']],
            'RequiredToPreview': True})

    # Approval rating
    if 'approval_rating' in cfg and cfg['approval_rating'] > 0:
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

    # Skip if already processed
    assignment = mturk.get_assignment(AssignmentId=assignment_id)
    if assignment['Assignment']['AssignmentStatus'] == 'Submitted':
        # Reject assignment
        mturk.reject_assignment(
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


def status(config, credentials):
    """Get the status of the current HIT"""
    # Connect to MTurk
    mturk = connect(credentials['PRODUCTION'])

    # Get HIT status
    return mturk.get_hit(HITId=credentials['HIT_ID'])['HIT']['HITStatus']
