import contextlib
import os

import dotenv
import mysql.connector

import reseval


def create(name):
    """Create a local MySQL database"""
    # Get unique identifier
    unique = reseval.load.credentials_by_name(name, 'unique')['unique']

    # Load environment variables
    dotenv.load_dotenv(reseval.ENVIRONMENT_FILE)

    # Create connection
    with connect() as (_, cursor):

        # Create database
        cursor.execute(f'CREATE DATABASE `{unique}`')

        # Return credentials
        return {
            'MYSQL_DBNAME': unique,
            'MYSQL_HOST': os.environ['MYSQL_HOST'],
            'MYSQL_USER': os.environ['MYSQL_USER'],
            'MYSQL_PASS': os.environ['MYSQL_PASS']}


def destroy(name):
    """Destroy a local MySQL database"""
    # Get unique identifier
    unique = reseval.load.credentials_by_name(name, 'unique')['unique']

    # Create connection
    with connect() as (_, cursor):

        # Destroy database
        try:
            cursor.execute(f'DROP DATABASE `{unique}`')
        except mysql.connector.errors.DatabaseError:

            # Database doesn't exist
            pass


###############################################################################
# Constants
###############################################################################


@contextlib.contextmanager
def connect():
    """Connect to a local MySQL database"""
    try:

        # Connect to the database
        connection = mysql.connector.connect(
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
