"""
Test data aggregation and caching.
"""
import pytest
import pandas as pd  # type checking
import finnhub
import datetime as dt
import time

import data


def test_finnhub_aggregation():
    data_res: pd.DataFrame = data._incremental_aggregation(
        "NFLX",
        "1m",
        dt.date(2019, 1, 29),
        dt.date(2019, 4, 2),
        filter_eod = True
    )

    assert isinstance(data_res, pd.DataFrame)
    assert not data_res.empty
    assert all(
        [
            True for col in {"Open", "High", "Low", "Close"} if \
                col in list(data_res.columns)
        ]
    )
    assert len(data_res) > 5  # if weird non-data json returned by Finnhub

    # Filter EOD check
    for idx, _ in data_res.iterrows():
        assert dt.time(13, 30) <= \
            dt.time(idx.hour, idx.minute, idx.second) <= \
            dt.time(20)



def test_data_cache():
    # Test init
    n_bars = data.init_cache("MSFT", "1m", 0.2, force=False)
    assert isinstance(n_bars, int)

    # Test fetch
    cache_registry = data._fetch_cache()
    assert isinstance(cache_registry, pd.DataFrame)

    # Test load
    start = dt.date.today() - dt.timedelta(days=20)
    end = dt.date.today() - dt.timedelta(days=2)
    data_loaded = data.load_cache("MSFT", "1m", start, end)
    assert not data_loaded.empty

    # Test listing
    assert data.list_cache()

    # Test deletion
    assert data.delete_cache("MSFT", "1m")


def test_rate_limit_handling():
    def nohandle_spam_requests():
        try:
            for _ in range(1000):
                data.finnhub_client.price_target("GOOG")
        except finnhub.FinnhubAPIException:
            return
        else:
            pytest.fail("When not rate handling, no API exception was raised.")

    @data.handle_rate_limit
    def handle_spam_requests():
        """Run right after busting the rate limit."""
        for _ in range(2):
            data.finnhub_client.last_bid_ask("GOOG")

    with pytest.raises(finnhub.FinnhubAPIException):
    nohandle_spam_requests()

    # Test no handling first as an exception will be raised anyways
    handle_spam_requests()


def test_unix_conversion():
    date = dt.date(2020, 1, 1)
    assert data.dt_to_unix(date) == int(time.mktime(date.timetuple()))

    # Check for failure handling
    with pytest.raises(ValueError):
        data.dt_to_unix("Jan 1, 2020")


def test_yahoo_finance():
    """Just make sure it's in order."""
    res = data.data_yf(
        symbol = "NFLX",
        interval = "5m",
        walkforward = {
            "train": (dt.date.today() - dt.timedelta(15), dt.date.today() - dt.timedelta(1))
        }
    )

    assert res
    assert isinstance(res, dict)
    assert all(isinstance(val, pd.DataFrame) for val in res.values())
    assert not any(df.empty for df in res.values())
