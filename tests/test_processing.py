import processing
import data
import systems


# Initialize AAPL cache data to speed up tests
data.cache_walkforward_data(
    walkforward = systems.systems[1][1].Params.walkforward,
    symbol = systems.systems[1][1].Params.symbol,
    interval = systems.systems[1][1].Params.timeframe,
    filter_eod = systems.systems[1][1].Params.filter_eod,  
    force = False
)


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
