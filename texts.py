import nexmo
import configparser
import os


current_dir = os.path.dirname(
    os.path.realpath(__file__)
)


keys = configparser.RawConfigParser()
keys.read(os.path.join(current_dir, "keys.ini"))


def keys_given() -> bool:
    """
    Determines whether or not all keys have been given for Nexmo.
    """
    nexmo_keys = keys["Nexmo"]
    fields = "api_key", "api_secret", "sender", "receiver"

    for field in fields:
        try: 
            if not nexmo_keys[field]: return False
        except KeyError: 
            return False

    return True


if keys_given():
    client = nexmo.Client(keys["Nexmo"]["api_key"], keys["Nexmo"]["api_secret"])
    sms = nexmo.Sms(client)

    def text_me(message: str) -> None:
        sms.send_message(
            {
                "from": keys["Nexmo"]["sender"],
                "to": keys["Nexmo"]["receiver"],
                "text": str(message)
            }
        )
