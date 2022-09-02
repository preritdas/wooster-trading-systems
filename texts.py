"""
Send text alerts. Implemented in CLI process command to optionally alert the completion
of a processing/optimization operation. Keys do not have to be provided. If they
are not, the text_me function simply does nothing, without returning any errors,
thereby preventing a program crash.
"""
# External imports
import nexmo

# Interal imports
import warnings

# Project modules
import keys


def _keys_given() -> bool:
    """
    Determines whether or not all keys have been given for Nexmo.
    """
    if keys.Nexmo.nexmo_keys is None: 
        return False

    return True


def _auth_nexmo() -> tuple[nexmo.Client, nexmo.Sms]:
    """
    Only call this if _keys_given returns True.
    """
    client = nexmo.Client(keys.Nexmo.api_key, keys.Nexmo.api_secret)
    return client, nexmo.Sms(client)


def text_me(message: str) -> bool:
    """
    Return False if no text is sent due to no keys, True if text was sent.
    """
    # Silently return if no keys given to prevent crash
    if not _keys_given(): 
        warnings.warn(
            "texts.text_me was called but no Nexmo keys were given in keys.ini."
        )
        return False

    # Assuming keys are given
    client, sms = _auth_nexmo()

    sms.send_message(
        {
            "from": keys["Nexmo"]["sender"],
            "to": keys["Nexmo"]["receiver"],
            "text": str(message)
        }
    )

    return True
