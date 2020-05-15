import configparser
import os


class ConfigurationComponent:
    def __init__(self):
        config = configparser.ConfigParser()
        directory = os.path.abspath(os.path.join(os.path.realpath(__file__), os.pardir, os.pardir, os.pardir))
        app_configuration = os.environ.get("app_configuration")
        if not app_configuration:
            config_name = "app.ini"
            init_file = os.path.join(directory, config_name)
            config.read(init_file)
            self.owlvey_url = config["OWLVEY"]["url"]
            self.owlvey_identity = config["OWLVEY"]["identity"]
            self.owlvey_client = config["OWLVEY"]["client"]
            self.owlvey_secret = config["OWLVEY"]["secret"]
        else:
            self.owlvey_url = os.environ["owlvey_url"]
            self.owlvey_identity = os.environ["owlvey_identity"]
            self.owlvey_client = os.environ["owlvey_client"]
            self.owlvey_secret = os.environ["owlvey_secret"]
