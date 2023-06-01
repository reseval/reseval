import boto3


###############################################################################
# AWS RDS database management
###############################################################################


def create(config):
    """Create a MySQL database on AWS"""
    # Connect to AWS RDS
    client = boto3.client('rds')

    # Create database
    response = client.create_db_instance(
        DBName=config['name'],
        DBInstanceIdentifier=config['name'],
        DBInstanceClass='db.t2.micro',
        Engine='mysql',
        MasterUsername='root',
        MasterUserPassword='password',
        AllocatedStorage=64)['DBInstance']

    # Get credentials
    credentials = {
        'MYSQL_DBNAME': config['name'],
        'MYSQL_HOST': response['Endpoint']['Address'],
        'MYSQL_USER': 'root',
        'MYSQL_PASS': 'password'}

    return credentials


def destroy(config):
    """Destroy a MySQL database on AWS"""
    # Connect to AWS RDS
    client = boto3.client('rds')

    # Delete database
    client.delete_db_instance(
        DBInstanceIdentifier=config['name'],
        SkipFinalSnapshot=True,
        DeleteAutomatedBackups=True)
