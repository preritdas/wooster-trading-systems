"""
Read keys.ini file.
"""
import configparser
import os


current_dir = os.path.dirname(os.path.realpath(__file__))
keys = configparser.RawConfigParser()
keys.read(os.path.join(current_dir, "keys.ini"))


class Finnhub:
    """
    Market data.
    """
    api_key = keys["Finnhub"]["api_key"]


class Nexmo:
    """
    Sending text alerts. Optional.
    """
    try:
        nexmo_keys = keys["Nexmo"]
    except KeyError:
        nexmo_keys = None

    if nexmo_keys is None:
        api_key = None
        api_secret = None
        sender = None
        receiver = None
    else:
        api_key = nexmo_keys["api_key"]
        api_secret = nexmo_keys["api_secret"]
        sender = nexmo_keys["sender"]
        receiver = nexmo_keys["receiver"]
