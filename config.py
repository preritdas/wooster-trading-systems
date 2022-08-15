"""
Read config.ini and parse.
"""
import configparser
import os


current_dir = os.path.dirname(
    os.path.realpath(__file__)
)

if not os.path.exists(config_path := os.path.join(current_dir, "config.ini")):
    raise FileNotFoundError("You must have a provided config.ini file.")


config = configparser.RawConfigParser()
config.read(config_path)


class Optimization:
    """
    Optimization parameters and defaults.
    """
    optimization_config = config["Optimization"]
    default_optimizer = optimization_config["default_optimizer"]