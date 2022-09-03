"""
Ensure all Params classes conform to the necessary structure.
"""
import pytest
import datetime as dt


def test_params():
    """
    Call the enforceparams method.
    """
    import systems
    

@pytest.fixture(scope="module")
def params_missing_attr():
    class ParamsNoTimeframe:
        symbol = "AAPL"
        filter_eod = True

        walkforward = {
            "train": (dt.date(2014, 7, 1), dt.date(2014, 8, 30)),
            "up": (dt.date(2021, 7, 1), dt.date(2021, 8, 1)),
            "down": (dt.date(2018, 9, 1), dt.date(2018, 10, 1)),
            "chop": (dt.date(2020, 9, 1), dt.date(2020, 10, 20))
        }

        optimizers = {
            "rsi_period": range(4, 20),
            "constraint": lambda params: params.rsi_period > 2  # handled by above
        }
    
    return ParamsNoTimeframe


@pytest.fixture(scope="module")
def params_bad_attr():
    class ParamsBadTimeframe:
        symbol = "AAPL"
        timeframe = 50
        filter_eod = True

        walkforward = {
            "train": (dt.date(2014, 7, 1), dt.date(2014, 8, 30)),
            "up": (dt.date(2021, 7, 1), dt.date(2021, 8, 1)),
            "down": (dt.date(2018, 9, 1), dt.date(2018, 10, 1)),
            "chop": (dt.date(2020, 9, 1), dt.date(2020, 10, 20))
        }

        optimizers = {
            "rsi_period": range(4, 20),
            "constraint": lambda params: params.rsi_period > 2  # handled by above
        }
    
    return ParamsBadTimeframe


def test_enforcement_missing(params_missing_attr, params_bad_attr):
    import systems

    with pytest.raises(SystemExit):
        systems.enforceparams.check_system(params_missing_attr, 1)

    with pytest.raises(SystemExit):
        systems.enforceparams.check_system(params_bad_attr, 1)
