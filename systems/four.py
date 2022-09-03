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

    def yesterday_extreme(self, direction):
        assert direction in {"max", "min"}

        yesterday_dt = self.data.index[0].to_pydatetime() - dt.timedelta(1)
        yesterday = yesterday_dt.strftime("%Y-%m-%d")

        high_series = self.data.High.s
        yesterday_highs = high_series.loc[(high_series.index == yesterday)]

        return yesterday_highs.max() if direction == "max" else yesterday_highs.min()


    def next(self):
        if self.data.High[-1] > self.yesterday_extreme("max"):
            self.buy()
        elif self.data.Low[-1] < self.yesterday_extreme("min"):
            self.sell()
