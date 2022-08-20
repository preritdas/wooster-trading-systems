"""
Market data operations. To activate a provider, rename its main data function 
to `data` as opposed to `data_yf` for yfinance, etc.
"""
import yfinance as yf
import finnhub
import pandas as pd

import datetime as dt 
import time
import configparser
import os

import utils  # console data status
import config  # datetime formats


# ---- Tools and keys ----

current_dir = os.path.dirname(os.path.realpath(__file__))
keys_path = os.path.join(current_dir, "keys.ini")
keys = configparser.ConfigParser()
keys.read(keys_path)

def dt_to_unix(dt_date: dt.datetime) -> int:
    """
    Convert Datetime object to UNIX, traditionally designed for Finnhub's
    market candles architecture.
    """
    if not isinstance(dt_date, dt.datetime):
        raise ValueError("Must provide a datetime object.")
    
    return int(time.mktime(dt_date.timetuple()))


# ---- Yahoo Finance ---- 

def _fetch_data_yf(
    symbol: str, 
    interval: str, 
    start: dt.datetime,
    end: dt.datetime
) -> pd.DataFrame:
    """
    Download data from yfinance. Does not work with period, must take start
    and end as datetime type, where end is at least one day prior. 
    This is because if you run the system while the market is open, plotting breaks.
    """
    return yf.download(
        tickers = symbol,
        interval = interval,
        start = start,
        end = end,
        progress = False,
        show_errors = True
    )


def data_yf(
    symbol: str, 
    interval: str,
    walkforward: dict[str, tuple[dt.datetime]]
) -> dict[str, pd.DataFrame]:
    """
    `walkforward` must be a dict containing walkforward labels, ex. train, up, down...
    The values with each of these must be a tuple with two, Datetime objects, the first
    being the start date and the end being the end date.
    """
    return_data = {}
    for label, start_end in walkforward.items():
        return_data[label] = _fetch_data_yf(symbol, interval, start_end[0], start_end[1])

    return return_data


# ---- Finnhub ----

finnhub_client = finnhub.Client(keys["Finnhub"]["api_key"])

finnhub_available_timeframes = {"1", "5", "15", "30", "60", "D", "W", "M"}


def finnhub_tf(tf: str) -> str:
    """
    Raises ValueError if conversion was not possible.
    """
    conversions = {
        "1m": "1",
        "5m": "5",
        "15m": "15",
        "30m": "30",
        "60m": "60",
        "1d": "D",
        "1w": "W"
    }

    if not tf in finnhub_available_timeframes:
        if tf in conversions: tf = conversions[tf]
        if not tf in finnhub_available_timeframes:
            raise ValueError(
                f"{tf} not supported by Finnhub, or in the wrong format."
            )

    return tf


def _fetch_data_finnhub(
    symbol: str, 
    interval: str, 
    start: dt.datetime, 
    end: dt.datetime
) -> pd.DataFrame:
    """
    Download data from Finnhub. Does not work with period, must take start
    and end as datetime type, where end is at least one day prior. 
    This is because if you run the system while the market is open, plotting breaks.
    """
    interval = finnhub_tf(interval)

    data = finnhub_client.stock_candles(
        symbol.upper(),
        interval,
        dt_to_unix(start),
        dt_to_unix(end)
    )

    data_df = pd.DataFrame(data)
    data_df['Date'] = pd.to_datetime(data_df['t'], unit="s")
    data_df.set_index('Date', inplace=True)
    data_df.drop(['s', 't'], axis=1, inplace=True)
    data_df.rename(
        columns = {
            "c": "Close",
            "h": "High",
            "l": "Low",
            "o": "Open",
            "v": "Volume"
        },
        inplace = True
    )

    return data_df


def _incremental_aggregation(
    symbol: str, 
    interval: str, 
    start: dt.datetime, 
    end: dt.datetime
) -> pd.DataFrame:
    """
    Incremement through Finnhub data (if intraday) due to data access limitations.
    """
    # If not getting intraday data, Finnhub iteration unnecessary
    if interval in {"D", "W"}:
        return _fetch_data_finnhub(
            symbol,
            interval,
            start,
            end
        )

    datas = []
    current_pointer = start
    while current_pointer < end:
        if (look_forward := (current_pointer + dt.timedelta(days=29))) > end:
            look_forward = end

        datas.append(
            _fetch_data_finnhub(
                symbol, 
                interval, 
                current_pointer, 
                look_forward
            )
        )
        current_pointer += dt.timedelta(days=29)
        time.sleep(0.4)  # finnhub rate limit

    return pd.concat(datas)


def data(
    symbol: str, 
    interval: str, 
    walkforward: dict[str, tuple[dt.datetime]]
) -> dict[str, pd.DataFrame]:
    """
    Collect properly split walkforward data.
    """
    with utils.console.status("Aggregating market data from Finnhub..."):
        return {
            label: _incremental_aggregation(
                symbol, 
                interval, 
                start_end[0], 
                start_end[1]
            ) for label, start_end in walkforward.items()
        }


def init_cache(symbol: str, interval: str, lookback_yrs: int, force: bool) -> bool | int:
    """
    Initialize data cache. Returns the number of bars collected, 
    for no practical purpose.
    """
    interval = finnhub_tf(interval)

    today = dt.datetime.today()
    lookback = today - dt.timedelta(weeks=52*lookback_yrs)

    def dt_format(date: dt.datetime) -> str:
        return date.strftime(config.Datetime.date_format)

    cache_path = os.path.join(
        current_dir, 
        "data-cache", 
        f"{symbol.upper()}===={dt_format(lookback)}==={dt_format(today)}.csv"
    )

    # Specify through CLI if cached data should be re-written
    if os.path.exists(cache_path) and not force:
        return False

    data = _incremental_aggregation(symbol, interval, lookback, today)
    data.to_csv(cache_path)

    return len(data)
