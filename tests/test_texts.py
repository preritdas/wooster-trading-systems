import texts
import nexmo


def test_keys():
    keys_given = texts._keys_given()
    assert isinstance(keys_given, bool)
    
    # Test API credentials if they're provided
    if keys_given:
        client, sms = texts._auth_nexmo()
        client.get_account_numbers()
        