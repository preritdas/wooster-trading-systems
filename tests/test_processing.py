import processing


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


def test_process_no_progress():
    result = processing.process_system_idx(
        1, 
        optimize = True, 
        optimizer = "SQN",
        method = "grid",
        progress = False
    )

    assert result
