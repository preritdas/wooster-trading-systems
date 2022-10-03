"""
Wooster Five system, working with raw price mean reversion.
"""
import backtesting as bt
import numpy as np

# Local
import datetime as dt


class Params:
    """
    Strategy meta-configurations. These are not indicator settings, or 
    any such optimizable parameters; rather, symbols, timeframes, 
    date-ranges, etc.
    """
    symbol = "AAPL"
    timeframe = "1m"
    filter_eod = True

    walkforward = {
        "train": (dt.date(2022, 1, 10), dt.date(2022, 1, 23))
    }

    optimizers = {
        # "Z_THRESHOLD": range(1.1, 3.0, 0.2),
        # "RR_RATIO": range(0, 5),
        # "RISK": range(0.0, 0.1, 0.1),
        "constraint": lambda params: True
    }


class WoosterFive(bt.Strategy):
    """
    Godspeed, Wooster Five.
    """
    Z_THRESHOLD = 2
    RR_RATIO = 2
    RISK = 0.01

    def init(self):
        pass

    def z_score(self) -> float:
        mean: float = self.data.Close.mean()
        distance: float = self.data.Close[-1] - mean
        return distance / np.std(self.data.Close)

    def next(self):
        if self.z_score() > self.Z_THRESHOLD and not self.position:
            self.buy(
                sl = self.data.Close[-1] * (1 - self.RISK),
                tp = self.data.Close[-1] * (1 + (self.RR_RATIO * self.RISK))
            )
        elif self.z_score() < -self.Z_THRESHOLD and not self.position:
            self.sell(
                sl = self.data.Close[-1] * (1 + self.RISK),
                tp = self.data.Close[-1] * (1 - (self.RR_RATIO * self.RISK))
            )
