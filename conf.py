import yaml
from pathlib import Path


def get_secrets():
    full_file_path = Path(__file__).parent.joinpath('secrets.yaml')
    with open(full_file_path) as settings:
        settings_data = yaml.load(settings, Loader=yaml.Loader)
    return settings_data
