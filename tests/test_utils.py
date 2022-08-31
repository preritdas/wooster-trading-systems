"""
Tests for the utils module.
"""
import os

import utils


def test_idx_to_name():
    """
    Wooster One, etc.
    """
    assert utils.idx_to_name(2) == "Wooster Two"
    assert utils.idx_to_name(24) == "Wooster TwentyFour"
    assert utils.idx_to_name(3, lower=True) == "wooster three"
    assert utils.idx_to_name(142) == "Wooster OneHundredFortyTwo"


def test_full_label_name():
    """
    Result labels for chart HTML titles.
    In-Sample Training Results, Out-of-Sample Uptrend Results, etc.
    """
    tests = {
        "train": "In-Sample Training Results",
        "up": "Out-of-Sample Uptrend Results",
        "down": "Out-of-Sample Downtrend Results",
        "chop": "Out-of-Sample Chop Results"
    }

    for key, val in tests.items():
        assert utils.full_label_name(key) == val


def test_plot_path():
    """
    Wooster Two is locked away, so check that the plot path for Wooster One
    results in a file that already exists.
    """
    for label in utils.LABELS:
        assert os.path.exists(utils.plot_path(2, label))


def test_stats_path():
    """
    Wooster Two is locked away, so check that the plot path for Wooster One
    results in a file that already exists.
    """
    assert os.path.exists(utils.stats_path(2))


def test_read_results():
    """
    CLI results command.
    """
    assert utils.load_results(1)


def test_read_optimizers():
    """
    CLI optimizers command.
    """
    assert utils.read_params(system_idx=1)


def test_system_existence():
    assert utils.system_exists(1)
