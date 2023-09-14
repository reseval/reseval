import contextlib
import csv
import os

import mysql.connector

import reseval


###############################################################################
# Constants
###############################################################################


# MySQL database schema
SCHEMA = [
    # Evaluation conditions. For example, for an AB test, these are the
    # names of the conditions corresponding to the "A" and "B" choices.
    #
    # Condition - The name of the condition
    'CREATE TABLE `conditions` ('
    '  `Condition` varchar(255) UNIQUE,'
    '  PRIMARY KEY (`Condition`)'
    ')',

    # Tables of files to be evaluated, split into stem and extension.
    # Exact file paths depend on the test being performed. See README for
    # details.
    #
    # Stem - The file stem
    # Extension - The file extension
    # Uses - The number of times this stem has been selected for evaluation
    'CREATE TABLE `files` ('
    '  `Stem` varchar(255) UNIQUE,'
    '  `Extension` varchar(16) NOT NULL,'
    '  `Uses` int DEFAULT 0,'
    '  PRIMARY KEY (`Stem`)'
    ')',

    # Participant information
    # This assumes each participant only takes the survey once.
    # Prescreening questions from the configuration file are included
    # as well. These questions are formatted as
    # f' `{name}` varchar({length}) NOT NULL,', where "name" is the
    # name given to the question in the configuration file, and "length"
    # is automatically computed from the longest allowed answer.
    #
    # ID - The participant ID
    # CompletionCode - The random code the participant recieves upon completion
    # DateTaken - The time at which the participant took the survey
    'CREATE TABLE `participants` ('
    '  `ID` char(32) UNIQUE,'
    '{}'
    '  `CompletionCode` char(10) DEFAULT \'INCOMPLETE\','
    '  `DateTaken` timestamp DEFAULT CURRENT_TIMESTAMP,'
    '  PRIMARY KEY (`ID`)'
    ')',

    # Participant's responses
    # The format of the response depends on the test being taken. For example,
    # an ABX test has as responses a character A, B, or X, and an MOS test has
    # as responses numbers 1-5.
    #
    # Stem - The file stem
    # Participant - The participant ID
    # OrderAsked - The chronological ordering of the survey
    # Response - The response given by the participant
    'CREATE TABLE `responses` ('
    '  `Stem` varchar(255),'
    '  `Participant` char(32),'
    '  `OrderAsked` int,'
    '  `Response` {},'
    '  FOREIGN KEY (`Stem`) REFERENCES `files`(`Stem`),'
    '  FOREIGN KEY (`Participant`) REFERENCES `participants`(`ID`)'
    ')']

# Names of tables in the database
TABLES = ['conditions', 'files', 'participants', 'responses']


###############################################################################
# Database management
###############################################################################


def create(config, test, local=False):
    """Write database environment variable file and initialize the database"""
    print('Creating database...')

    # Create new database and retrieve credentials
    credentials = module(config, local).create(config['name'])

    # Save environment variables
    for key, value in credentials.items():
        os.environ[key] = value

    # Connect to MySQL database
    with connect() as (_, cursor):

        # Create database tables
        for table, command in zip(TABLES, SCHEMA):

            # Add prescreen questions from configuration file
            if table == 'participants':
                questions = ''

                all_questions = []
                if 'prescreen_questions' in config:
                    all_questions += config['prescreen_questions']
                if 'followup_questions' in config:
                    all_questions += config['followup_questions']
                for question in all_questions:
                    name = question['name']

                    # Get maximum answer length
                    question_type = question['type']
                    if question_type == 'free-response':
                        max_length = 1024
                    elif question_type == 'multiple-choice':
                        answers = question['answers']
                        max_length = max([len(answer) for answer in answers])
                    else:
                        raise ValueError(
                            f'Question type {question_type} is not recognized')

                    # Add database row
                    questions += f'  `{name}` varchar({max_length}),'

                # Update MySQL command with prescreen questions
                command = command.format(questions)

            # Response type is unique to the test
            if table == 'responses':
                command = command.format(test.response_type())

            # Communicate with database
            cursor.execute(command)

    # Upload conditions and filenames
    upload_test(test)

    # Upload any previous results from this evaluation
    upload_previous(config['name'])

    # Write credentials to environment file
    environment_file = (
        reseval.EVALUATION_DIRECTORY /
        config['name'] /
        'credentials' /
        '.env')
    environment_file.parent.mkdir(exist_ok=True, parents=True)
    with open(environment_file, 'w') as file:
        for key, value in credentials.items():
            file.write(f'{key}={value}\n')

    return credentials


def destroy(name):
    """Destroy a database"""
    # Load database credentials
    try:
        reseval.load.environment_variables_by_name(name)
    except FileNotFoundError:
        return

    # Destroy database
    local = reseval.is_local(name)
    config = reseval.load.config_by_name(name)
    module(config, local).destroy(name)

    # Cleanup credentials
    (
        reseval.EVALUATION_DIRECTORY /
        name /
        'credentials' /
        '.env'
    ).unlink(missing_ok=True)


def download(name, directory, tables=TABLES):
    """Download the contents of the MySQL database"""
    # Load database credentials
    reseval.load.environment_variables_by_name(name)

    # Create directory to store results
    directory.mkdir(exist_ok=True, parents=True)

    with connect() as (_, cursor):

        # Download each table to a csv file
        for name in tables:

            # Download table
            cursor.execute('SELECT * FROM ' + name)
            table = cursor.fetchall()

            # Get table header
            cursor.execute(f'SHOW COLUMNS FROM {name}')
            header = [column[0] for column in cursor.fetchall()]

            # Write table to CSV
            with open(directory / f'{name}.csv', 'w') as file:
                file = csv.writer(file)
                file.writerow(header)
                file.writerows(table)


###############################################################################
# Utilities
###############################################################################


@contextlib.contextmanager
def connect():
    """Connect to a MySQL database"""
    try:

        # Connect to the database
        connection = mysql.connector.connect(
            database=os.environ['MYSQL_DBNAME'],
            host=os.environ['MYSQL_HOST'],
            user=os.environ['MYSQL_USER'],
            password=os.environ['MYSQL_PASS'])

        # Create cursor to execute commands
        cursor = connection.cursor()

        # Execute user code
        yield connection, cursor

    finally:

        # Close database connection
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()


def upload_previous(name):
    """Upload previous results from this evaluation to database"""
    # Check if we have previous results to upload
    tables = ['participants', 'responses']
    directory = reseval.EVALUATION_DIRECTORY / name / 'tables'
    if not all((directory / f'{table}.csv').exists() for table in tables):
        return

    # Connect to MySQL database
    with connect() as (connection, cursor):

        # Upload previous results
        for table in tables:

            # Read CSV
            with open(directory / f'{table}.csv') as file:
                rows = [row for row in csv.DictReader(file)]

            # Skip if table is empty
            if len(rows) == 0:
                return

            # Format MySQL command
            keys = list(rows[0].keys())
            columns, values, update = '', '', ''
            for i, key in enumerate(keys):
                columns += f'`{key}`'
                values += '%s'
                update += f'`{key}`=`{key}`'
                if i != len(keys) - 1:
                    columns += ', '
                    values += ', '
                    update += ', '
            command = (
                f'INSERT INTO {table} ({columns}) VALUES ({values}) '
                f'ON DUPLICATE KEY UPDATE {update}')

            # Specify data order
            items = [tuple(row[key] for key in keys) for row in rows]

            # Execute insertions
            cursor.executemany(command, items)

        # Communicate with database
        connection.commit()


def upload_test(test):
    """Upload test information to database"""
    # Connect to MySQL database
    with connect() as (connection, cursor):

        # Add conditions to the database
        command = (
            'INSERT INTO conditions (`Condition`) VALUES (%s) '
            'ON DUPLICATE KEY UPDATE `Condition`=`Condition`')
        cursor.executemany(command, [(c,) for c in test.conditions])

        # Add filenames and extensions to database
        command = (
            'INSERT INTO files (Stem, Extension) VALUES (%s, %s) ' +
            'ON DUPLICATE KEY UPDATE Stem=Stem, Extension=Extension')

        stems_and_extensions = test.stems_and_extensions()
        cursor.executemany(command, stems_and_extensions)
        connection.commit()


def module(config, local=False):
    """Get the database module to use"""
    if local:
        return reseval.database.localhost
    database = config['database']
    if database == 'aws':
        return reseval.database.aws
    if database == 'heroku':
        return reseval.database.heroku
    raise ValueError(f'Database service {database} is not recognized')
