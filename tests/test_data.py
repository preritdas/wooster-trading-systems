"""
Test data aggregation and caching.
"""
import data
import datetime as dt
import pandas as pd  # type checking


def test_finnhub_aggregation():
    data._incremental_aggregation(
        "AAPL",
        "1m",
        dt.date(2019, 1, 5),
        dt.date(2020, 1, 1),
        filter_eod = True
    )


def test_data_cache():
    # Test init
    n_bars = data.init_cache("MSFT", "1m", 1)
    assert isinstance(n_bars, int)

    # Test fetch
    cache_registry = data._fetch_cache()
    assert isinstance(cache_registry, pd.DataFrame)

    # Test load
    start = dt.date.today() - dt.timedelta(days=20)
    end = dt.date.today() - dt.timedelta(days=2)
    data_loaded = data.load_cache("MSFT", "1m", start, end)
    assert not data_loaded.empty
