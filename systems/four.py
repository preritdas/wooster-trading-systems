"""
Wooster Four trading system, trained and backtested.
"""
# External imports
import backtesting as bt
import pandas as pd
import numpy as np

# Local imports
import datetime as dt
from typing import Generator


class Params:
    """
    Strategy meta-configurations. These are not indicator settings, or 
    any such optimizable parameters; rather, symbols, timeframes, 
    date-ranges, etc.
    """
    symbol = "AAPL"
    timeframe = "10m"
    filter_eod = True

    walkforward = {
        "train": (dt.date(2022, 1, 10), dt.date(2022, 6, 23)),
        "up": (dt.date(2022, 1, 1), dt.date(2022, 7, 13)),
        "down": (dt.date(2022, 1, 17), dt.date(2022, 9, 3)),
        "chop": (dt.date(2021, 6, 30), dt.date(2022, 2, 10))
    }

    optimizers = {
        "constraint": lambda params: True
    }


def previous_high(data: pd.DataFrame) -> Generator:
    """
    Returns a series of the previous day's high.
    """
    def _day_df(day: dt.date):
        _df = data.loc[data.index.date == day]
        return _df
    
    def highest_price(day: dt.date):
        df = _day_df(day)
        return df["High"].max()

    for i in range(len(data)):
        today = data.index[i].to_pydatetime().date()
        yesterday = today - dt.timedelta(1)
        highest = highest_price(yesterday)

        tries = 0
        while np.isnan(highest):
            highest = highest_price(yesterday - dt.timedelta(1))
            tries += 1
            if tries == 5: break
        
        yield highest 


def previous_low(data: pd.DataFrame) -> Generator:
    """
    Returns a series of the previous day's high.
    """
    def _day_df(day: dt.date):
        _df = data.loc[data.index.date == day]
        return _df
    
    def lowest_price(day: dt.date):
        df = _day_df(day)
        return df["Low"].min()

    for i in range(len(data)):
        today = data.index[i].to_pydatetime().date()
        yesterday = today - dt.timedelta(1)
        lowest = lowest_price(yesterday)
        
        tries = 0
        while np.isnan(lowest):
            lowest = lowest_price(yesterday - dt.timedelta(1))
            tries +=1
            if tries == 5: break
        
        yield lowest


# ---- Strategy ----

class WoosterFour(bt.Strategy):
    """
    Trading breaches of the previous day's highs and lows.
    """
    def init(self):
        """
        Abstract strategy method to define and wrap indicators etc.
        """
        self.yesterday_high = previous_high(self.data.df)
        self.yesterday_low = previous_low(self.data.df)

    def next(self):
        prev_high = next(self.yesterday_high)
        prev_low = next(self.yesterday_low)

        if self.data.High[-1] > prev_high:
            if self.position.is_short: self.position.close()
            elif self.position.is_long: pass
            else: self.buy()
        elif self.data.Low[-1] < prev_low:
            if self.position.is_long: self.position.close()
            elif self.position.is_short: pass
            else: self.sell()
