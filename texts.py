"""
Send text alerts. Implemented in CLI process command to optionally alert the completion
of a processing/optimization operation. Keys do not have to be provided. If they
are not, the text_me function simply does nothing, without returning any errors,
thereby preventing a program crash.
"""
import nexmo

import configparser
import os
import warnings


current_dir = os.path.dirname(
    os.path.realpath(__file__)
)


keys = configparser.RawConfigParser()
keys.read(os.path.join(current_dir, "keys.ini"))


def _keys_given() -> bool:
    """
    Determines whether or not all keys have been given for Nexmo.
    """
    fields = "api_key", "api_secret", "sender", "receiver"

    try:
        nexmo_keys = keys["Nexmo"]
    except KeyError:
        return False

    for field in fields:
        try: 
            if not nexmo_keys[field]: return False
        except KeyError: 
            return False

    return True


def _auth_nexmo() -> tuple[nexmo.Client, nexmo.Sms]:
    client = nexmo.Client(keys["Nexmo"]["api_key"], keys["Nexmo"]["api_secret"])
    return client, nexmo.Sms(client)


def text_me(message: str) -> None:
    # Silently return if no keys given to prevent crash
    if not _keys_given(): 
        warnings.warn(
            "texts.text_me was called but no Nexmo keys were given in keys.ini."
        )
        return

    # Assuming keys are given
    client, sms = _auth_nexmo()

    sms.send_message(
        {
            "from": keys["Nexmo"]["sender"],
            "to": keys["Nexmo"]["receiver"],
            "text": str(message)
        }
    )
