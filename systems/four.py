"""
Wooster Four trading system, trained and backtested.
"""
# External imports
import backtesting as bt
import pandas as pd

# Local imports
import datetime as dt


class Params:
    """
    Strategy meta-configurations. These are not indicator settings, or 
    any such optimizable parameters; rather, symbols, timeframes, 
    date-ranges, etc.
    """
    symbol = "AMD"
    timeframe = "1m"
    filter_eod = True

    walkforward = {
        "train": (dt.date(2014, 7, 1), dt.date(2014, 8, 1)),
        "up": (dt.date(2021, 7, 1), dt.date(2021, 7, 14)),
        "down": (dt.date(2018, 9, 1), dt.date(2018, 9, 14)),
        "chop": (dt.date(2020, 9, 1), dt.date(2020, 9, 14))
    }

    optimizers = {
        "constraint": lambda params: True
    }


def previous_high(data: pd.DataFrame) -> pd.Series:
    """
    Returns a series of the previous day's high.
    """
    def _day_df(day: dt.date):
        _df = data.loc[data.index.date == day]
        return _df
    
    def highest_price(day: dt.date):
        df = _day_df(day)
        return df["High"].max()

    highest_prices = []
    for i in range(len(data)):
        today = data.index[i].to_pydatetime().date()
        yesterday = today - dt.timedelta(1)
        highest_prices.append(highest_price(yesterday))

    data["Yesterday High"] = highest_prices
    return data["Yesterday High"]


def previous_low(data: pd.DataFrame) -> pd.Series:
    """
    Returns a series of the previous day's high.
    """
    def _day_df(day: dt.date):
        _df = data.loc[data.index.date == day]
        return _df
    
    def lowest_price(day: dt.date):
        df = _day_df(day)
        return df["Low"].min()

    highest_prices = []
    for i in range(len(data)):
        today = data.index[i].to_pydatetime().date()
        yesterday = today - dt.timedelta(1)
        highest_prices.append(lowest_price(yesterday))

    data["Yesterday Low"] = highest_prices
    return data["Yesterday Low"]


# ---- Strategy ----

class WoosterFour(bt.Strategy):
    """
    Godspeed, Wooster Four.

    You trade breaches of the previous day's highs and lows.
    """
    def init(self):
        """
        Abstract strategy method to define and wrap indicators etc.
        """
        self.yesterday_high = self.I(previous_high, self.data.df, show_progress=True)
        self.yesterday_low = self.I(previous_low, self.data.df, show_progress=True)

    def next(self):
        if self.data.High[-1] > self.yesterday_high[-1]:
            self.buy()
        elif self.data.Low[-1] < self.yesterday_low[-1]:
            self.sell()
