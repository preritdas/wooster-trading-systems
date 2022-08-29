import utils


def test_idx_to_name():
    assert utils.idx_to_name(2) == "Wooster Two"
    assert utils.idx_to_name(24) == "Wooster TwentyFour"
    assert utils.idx_to_name(3, lower=True) == "wooster three"
    assert utils.idx_to_name(142) == "Wooster OneHundredFortyTwo"
