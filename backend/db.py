import configparser
import os
import sys

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


# def load_db_config():
#     script_dir = os.path.dirname(os.path.realpath(__file__))
    
#     env = os.getenv('MW_ENV', 'dev')  # default to dev
#     filename = f'config.{env}.ini'    # e.g. config.dev.ini or config.prod.ini

#     config_path = os.path.join(script_dir, filename)
    
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
    
    env = os.getenv('MW_ENV', 'dev')  # defaults to 'dev' if not set
    filename = f'config.{env}.ini'
    config_path = os.path.join(script_dir, filename)

    print(f"[INFO] Loading DB config for environment: {env}")
    print(f"[INFO] Looking for config file at: {config_path}")

    if not os.path.exists(config_path):
        print(f"[ERROR] Config file not found: {config_path}")
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(config_path)

    if 'postgres' not in config:
        print(f"[ERROR] Missing [postgres] section in {config_path}")
        sys.exit(1)

    try:
        db_config = {
            'host': config['postgres']['host'],
            'port': config['postgres']['port'],
            'user': config['postgres']['user'],
            'password': config['postgres']['password'],
            'database': config['postgres']['database']
        }
        print(f"[INFO] DB Config Loaded: {db_config}")
        return db_config
    except KeyError as e:
        print(f"[ERROR] Missing required key in config: {e}")
        sys.exit(1)