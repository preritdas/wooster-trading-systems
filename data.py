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
import systems


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
    if not isinstance(dt_date, dt.datetime) and not isinstance(dt_date, dt.date):
        raise ValueError("Must provide a date or datetime object.")
    
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


def handle_rate_limit(function):
    """
    Decorator. Try the underlying function, and if a Finnhub rate limit error 
    is caught, sleep for a second and keep trying the endpoint until 
    a valid result is obtained.
    """
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except finnhub.FinnhubAPIException as e:
            if "API limit reached" in str(e):
                time.sleep(1)
                return wrapper(*args, **kwargs)

    return wrapper
                

def finnhub_tf(tf: str, backwards: bool = False) -> str:
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

    if backwards:
        backwards_conversion = {val: key for key, val in conversions.items()}
        if not tf in backwards_conversion: return tf
        return backwards_conversion[tf]

    if tf not in finnhub_available_timeframes:
        if tf in conversions: tf = conversions[tf]
        if not tf in finnhub_available_timeframes:
            raise ValueError(
                f"{tf} not supported by Finnhub, or in the wrong format."
            )

    return tf


@handle_rate_limit
def _fetch_data_finnhub(
    symbol: str, 
    interval: str, 
    start: dt.datetime, 
    end: dt.datetime,
    from_aggregation: bool = False 
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

    if from_aggregation and data == {'s': 'no_data'}:
        return pd.DataFrame()

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


def _filter_eod(data: pd.DataFrame, timezone: str = "utc") -> pd.DataFrame:
    """
    Removes any data not between standard market hours, 9:30am to 4pm EST.
    """
    if timezone.lower() != "utc":
        raise ValueError("Only UTC supported currently.")

    if data.empty: return data  # if empty from an incremental agg window
    return data.between_time(dt.time(13, 30), dt.time(20))


def _incremental_aggregation(
    symbol: str, 
    interval: str, 
    start: dt.datetime, 
    end: dt.datetime,
    filter_eod: bool
) -> pd.DataFrame:
    """
    Incremement through Finnhub data (if intraday) due to data access limitations.
    """
    # Convert interval format
    old_interval = interval
    interval = finnhub_tf(old_interval)

    start_str = dt.datetime.strftime(start, format=config.Datetime.date_format)
    end_str = dt.datetime.strftime(end, format=config.Datetime.date_format)

    # Try to get data from cache
    _cache_res = load_cache(symbol, interval, start, end)
    if not _cache_res.empty: 
        utils.console.log(
            f"Utilizing cached {symbol.upper()} data from {start_str} to {end_str}."
        )
        return _cache_res if not filter_eod else _filter_eod(_cache_res)

    # If not getting intraday data, Finnhub iteration unnecessary
    if interval in {"D", "W"}:
        finnhub_res = _fetch_data_finnhub(symbol, interval, start, end)
        return finnhub_res if not filter_eod else _filter_eod(finnhub_res)

    datas = []
    current_pointer = start
    while current_pointer < end:
        if (look_forward := (current_pointer + dt.timedelta(days=29))) > end:
            look_forward = end

        finnhub_res = _fetch_data_finnhub(
            symbol, 
            interval, 
            current_pointer, 
            look_forward,
            from_aggregation=True
        )

        # Optional EOD filtering
        finnhub_res = finnhub_res if not filter_eod else _filter_eod(finnhub_res)
        datas.append(finnhub_res)

        current_pointer += dt.timedelta(days=29)

    return pd.concat(datas)


def data(
    symbol: str, 
    interval: str, 
    walkforward: dict[str, tuple[dt.datetime]],
    filter_eod: bool = False
) -> dict[str, pd.DataFrame]:
    """
    Collect properly split walkforward data.
    """
    with utils.console.status("Aggregating market data..."):
        return {
            label: _incremental_aggregation(
                symbol, 
                interval, 
                start_end[0], 
                start_end[1],
                filter_eod = filter_eod
            ) for label, start_end in walkforward.items()
        }


# ---- Cache ----


def _store_cache(
    symbol: str, 
    interval: str, 
    start: dt.date, 
    end: dt.date, 
    filter_eod: bool, 
    force: bool
) -> bool | int:
    """
    Internal storer of cache data. 
    """
    def dt_format(date: dt.datetime) -> str:
        return date.strftime(config.Datetime.date_format)

    # Create cache folder if nonexistent
    if not os.path.exists(cache_dir := os.path.join(current_dir, "data-cache")):
        os.mkdir(cache_dir)

    cache_path = os.path.join(
        cache_dir,
        f"{symbol.upper()}==={interval.lower()}===" \
            f"{dt_format(start)}==={dt_format(end)}.csv"
    )

    # Specify through CLI if cached data should be re-written
    if os.path.exists(cache_path) and not force:
        return False

    data = _incremental_aggregation(symbol, interval, start, end, filter_eod=filter_eod)
    data.to_csv(cache_path)

    return len(data)


def init_cache(symbol: str, interval: str, lookback_yrs: int, force: bool) -> bool | int:
    """
    Initialize data cache. Returns the number of bars collected, 
    for no practical purpose.
    """
    interval = finnhub_tf(interval)

    today = dt.date.today()
    lookback = today - dt.timedelta(weeks=int(52*lookback_yrs))

    # Len returned by _store_cache
    return(_store_cache(symbol, interval, lookback, today, filter_eod=False, force=force))


def cache_walkforward(
    walkforward: dict[str, tuple[dt.date, dt.date]], 
    symbol: str, 
    interval: str,
    filter_eod: bool,
    force: bool
) -> None:
    """
    Creates a data cache containing all the walkforward data necessary to be used
    by the processing pipeline, without having to initialize the full data window.
    """
    assert isinstance(walkforward, dict)

    for start, end in walkforward.values():
        start = start - dt.timedelta(days=1)
        end = end + dt.timedelta(days=1)
        _store_cache(
            symbol, 
            finnhub_tf(interval), 
            start, 
            end, 
            filter_eod=filter_eod, 
            force=force
        )


def cache_all_walkforwards() -> None:
    """
    Caches walkforward data for all documented systems.
    """
    for tup in systems.systems.values():
        params = tup[1].Params
        cache_walkforward(
            walkforward = params.walkforward,
            symbol = params.symbol,
            interval = params.timeframe,
            filter_eod = params.filter_eod,
            force = False
        )


def _fetch_cache() -> pd.DataFrame:
    """
    Read cache directory and return a DataFrame of available cache files.
    Columns: Symbol, Interval, Start, End, Path.
    """
    if not os.path.exists((cache_path := os.path.join(current_dir, "data-cache"))):
        return pd.DataFrame()

    if not (paths := os.listdir(cache_path)):
        return pd.DataFrame()

    cache_files = [os.path.splitext(path)[0] for path in paths]
    cache_files = [cache.split("===") for cache in cache_files]
    
    symbols = [cache[0] for cache in cache_files]
    intervals = [cache[1] for cache in cache_files]
    starts = [cache[2] for cache in cache_files]
    ends = [cache[3] for cache in cache_files]

    return pd.DataFrame(
        {
            "Symbol": symbols,
            "Interval": intervals,
            # "Start": pd.to_datetime(starts, format=config.Datetime.date_format),
            # "End": pd.to_datetime(ends, format=config.Datetime.date_format)
            "Start": [dt.datetime.strptime(str_time, config.Datetime.date_format) for str_time in starts],
            "End": [dt.datetime.strptime(str_time, config.Datetime.date_format) for str_time in ends],
            "Path": paths,
        }
    )


def load_cache(symbol: str, interval: str, start: dt.date, end: dt.date) -> pd.DataFrame:
    """
    Attempts to load data from cache. If usable cache was found, a DataFrame 
    is returned. Otherwise, an empty DataFrame is returned. That way, when you call
    .empty on the result of this function, a bool is returned, representative
    of whether or not there is usable cache data inside.
    """
    cache_db = _fetch_cache()
    if cache_db.empty: return pd.DataFrame()

    date_format = config.Datetime.date_format

    # Query
    symbol_res = cache_db[cache_db.Symbol == symbol]
    interval_res = symbol_res[symbol_res.Interval == interval]
    if interval_res.empty:  # attempt with converted timeframe
        interval_res = symbol_res[symbol_res.Interval == finnhub_tf(interval)]
    start_res = interval_res[
        interval_res.Start < pd.to_datetime(start, format=date_format)
    ]
    end_res = start_res[start_res.End > pd.to_datetime(end, format=date_format)]
    if end_res.empty: return pd.DataFrame()  # empty DF so df.empty returns False

    # Gather data
    path = os.path.join(current_dir, "data-cache", list(end_res["Path"])[0])
    cache_df = pd.read_csv(path)
    cache_df["Date"] = pd.to_datetime(cache_df["Date"])
    cache_df.set_index("Date", inplace=True)

    return cache_df[start:end]


def delete_cache(symbol: str, interval: str) -> bool:
    """
    Delete cache files if they exist. Only available filtering is by symbol
    and interval, not by start and end dates. Returns True if the cache was found
    and deleted, False if the cache was not found.
    """
    symbol = symbol.upper()
    cache_db = _fetch_cache()

    if cache_db.empty: return False

    symbol_res = cache_db[cache_db.Symbol == symbol]
    interval_res = symbol_res[symbol_res.Interval == interval]
    if interval_res.empty:
        interval_res = symbol_res[symbol_res.Interval == finnhub_tf(interval)]
    if interval_res.empty: return False

    for idx in range(len(interval_res)):
        os.remove(os.path.join(current_dir, "data-cache", list(interval_res["Path"])[idx]))

    return True


def list_cache() -> list[str]:
    """
    Returns a list of colored, Rich-formatted, strings, structured 
    in the following fashion. 1m AAPL data from 2021-08-17 to 2022-08-16.
    """
    cache_db = _fetch_cache()

    date_format = config.Datetime.date_format

    result_strs: list[str] = []
    for idx in range(len(cache_db)):
        result_strs.append(
            f"[green]{finnhub_tf(cache_db['Interval'][idx], backwards=True)}[/] "
            f"data on [green]{cache_db['Symbol'][idx].upper()}[/] "
            f"from {dt.datetime.strftime(cache_db['Start'][idx], date_format)} "
            f"to {dt.datetime.strftime(cache_db['End'][idx], date_format)}."
        )

    return result_strs
