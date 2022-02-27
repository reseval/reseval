import datetime
import itertools

import boto3
import xmltodict as xmltodict

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
    # Connect to MTurk
    mturk = connect(credentials['PRODUCTION'])

    # Delete HIT
    response = mturk.delete_hit(HITId=credentials['HIT_ID'])

    # TODO - check response


def extend(credentials, participants):
    """Extend a HIT with additional assignments"""
    # Connect to MTurk
    mturk = connect(credentials['PRODUCTION'])

    # Extend HIT
    # TODO - handle unique request token
    response = mturk.create_additional_assignments_for_hit(
        HITId=credentials['HIT_ID'],
        NumberOfAdditionalAssignments=participants)

    # TODO - check response


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

    # TODO - check response


def stop(credentials):
    """Stop an active HIT"""
    # Connect to MTurk
    mturk = connect(credentials['PRODUCTION'])

    # Stop HIT
    response = mturk.update_expiration_for_hit(
        HITId=credentials['HIT_ID'],
        ExpireAt=datetime.datetime.now())

    # TODO - check response


###############################################################################
# Utilities
###############################################################################


def approve(credentials, assignment_id):
    """Approve an assignment"""
    # Connect to MTurk
    mturk = connect(credentials['PRODUCTION'])

    # Approve assignment
    response = mturk.approve_assignment(AssignmentId=assignment_id)

    # TODO - check response
    pass


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
    """Give a participant a bonus"""
    # Connect to MTurk
    mturk = connect(credentials['PRODUCTION'])

    # Approve assignment
    # TODO - handle unique request token
    response = mturk.send_bonus(
        WorkerId=worker_id,
        BonusAmount=config['crowdsource']['payment']['completion'],
        AssignmentId=assignment_id,
        # use assignment_id as Unique token, because we would send_bonus only once per assignment
        UniqueRequestToken=assignment_id,
        Reason='Passed prescreening and completed evaluation. Thank you!')

    # TODO - check response
    pass


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

    # Reject assignment
    response = mturk.reject_assignment(
        AssignmentId=assignment_id,
        RequesterFeedback=reason)

    # TODO - check response


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
