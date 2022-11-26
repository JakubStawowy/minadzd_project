import yaml
from pathlib import Path
from pymongo import MongoClient

from consts import LOCAL_PORT, LOCAL_DB_USER_KEY, LOCAL_DB_PASSWD_KEY, LOCAL_DB_NAME, CLOUD_DB_NAME


def get_secrets():
    full_file_path = Path(__file__).parent.joinpath('secrets.yaml')
    with open(full_file_path) as settings:
        settings_data = yaml.load(settings, Loader=yaml.Loader)
    return settings_data


def get_local_connection():
    secrets = get_secrets()
    return MongoClient(
        'localhost',
        LOCAL_PORT,
        username=secrets[LOCAL_DB_USER_KEY],
        password=secrets[LOCAL_DB_PASSWD_KEY],
        authMechanism='SCRAM-SHA-256'
    )


def get_cloud_connection():
    secrets = get_secrets()
    return MongoClient(f'mongodb+srv://'
                       f'{secrets["cloud_db_user"]}:{secrets["cloud_db_passwd"]}@projectminadzd.5zghkdq.mongodb.net/'
                       '?retryWrites=true&w=majority')


def get_local_db():
    client = get_local_connection()
    return client, client.get_database(LOCAL_DB_NAME)


def get_cloud_db():
    client = get_cloud_connection()
    return client, client.get_database(CLOUD_DB_NAME)
