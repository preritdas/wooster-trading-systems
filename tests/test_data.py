import data
import datetime as dt


def test_finnhub_aggregation():
    data._incremental_aggregation(
        "AAPL",
        "1m",
        dt.date(2019, 1, 5),
        dt.date(2020, 1, 1),
        filter_eod = True
    )
