import configparser
import os

# def load_db_config():
#     script_dir = os.path.dirname(os.path.realpath(__file__))
#     config_path = os.path.join(script_dir, 'config.ini')

#     config = configparser.ConfigParser()
#     config.read(config_path)

#     return {
#         'host': config['postgres']['host'],
#         'port': config['postgres']['port'],
#         'user': config['postgres']['user'],
#         'password': config['postgres']['password'],
#         'database': config['postgres']['database']
#     }


def load_db_config():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    
    env = os.getenv('MW_ENV', 'dev')  # default to dev
    filename = f'config.{env}.ini'    # e.g. config.dev.ini or config.prod.ini

    config_path = os.path.join(script_dir, filename)
    
    config = configparser.ConfigParser()
    config.read(config_path)

    return {
        'host': config['postgres']['host'],
        'port': config['postgres']['port'],
        'user': config['postgres']['user'],
        'password': config['postgres']['password'],
        'database': config['postgres']['database']
    }