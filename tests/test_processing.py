import processing
import data
import systems


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
        processing.process_system_idx(index=system_idx, optimize=False)
