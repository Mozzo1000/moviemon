import configparser
import os

CONFIG_PATH = os.path.expanduser('~/.movielst/')
CONFIG_FILE = os.path.expanduser('config.ini')


def create_config():
    if not os.path.exists(CONFIG_PATH):
        os.makedirs(CONFIG_PATH)

        config = configparser.ConfigParser()

        config.add_section('Index')
        config.add_section('API')

        config.set('Index', 'location', CONFIG_PATH + 'movies.json')
        config.set('API', 'OMDb_API_key', '37835d63')

        with open(CONFIG_PATH + CONFIG_FILE, 'w') as config_file:
            config.write(config_file)


def get_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH + CONFIG_FILE)
    return config


def get_setting(section, setting):
    config = get_config()
    return config.get(section, setting)


def update_config(section, setting, value):
    config = get_config()
    config.set(section, setting, value)
    with open(CONFIG_PATH + CONFIG_FILE, 'w') as config_file:
        config.write(config_file)