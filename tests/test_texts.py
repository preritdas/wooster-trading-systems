import pytest


def test_keys():
    import texts

    keys_given = texts._keys_given()
    assert isinstance(keys_given, bool)
    
    # Test API credentials if they're provided
    if keys_given:
        client, sms = texts._auth_nexmo()
        client.get_account_numbers()
        

def test_handle_no_keys(mocker):
    mocker.patch('keys.Nexmo.nexmo_keys', None)
    import texts

    assert not texts._keys_given()

    with pytest.warns(UserWarning):
        assert not texts.text_me("This should not send.")
    