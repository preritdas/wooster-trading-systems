import processing
import data
import systems
import pytest


# Initialize AAPL cache data to speed up tests
data.cache_all_walkforwards()


def test_process_grid():
    result = processing.process_system_idx(
        1, 
        optimize = True, 
        optimizer = "SQN",
        method = "grid",
        progress = True
    )

    assert result


def test_process_skopt():
    result = processing.process_system_idx(
        1, 
        optimize = True, 
        optimizer = "SQN",
        method = "skopt",
        progress = True
    )

    assert result


def test_all_backtests():
    for system_idx in systems.systems:
        processing.process_system_idx(index=system_idx, optimize=False, train_only=True)


def test_raises():
    with pytest.raises(ValueError):
        processing.process_system_idx(
            "notanint", 
            optimize = True, 
            optimizer = "SQN",
            method = "grid",
            progress = True
        )

    with pytest.raises(ValueError):
        # Asked for optimization, gave no optimizer
        processing.process_system_idx(
            "notanint", 
            optimize = True, 
            method = "grid",
            progress = True
        )
  