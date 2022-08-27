"""
Wooster Three.
"""
# External imports
import backtesting as bt
import talib as ta

# Local imports
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

    walkforward: dict[str, tuple[dt.date, dt.date]] = {
        "train": (dt.date(2014, 7, 1), dt.date(2014, 8, 31)),
        "up": (dt.date(2021, 7, 1), dt.date(2021, 9, 1)),
        "down": (dt.date(2018, 9, 1), dt.date(2018, 11, 1)),
        "chop": (dt.date(2020, 9, 1), dt.date(2020, 12, 20))
    }

    optimizers: dict = {
        "profit_percent": range(1, 10, 1),
        "stop_percent": range(1, 10, 1),
        "constraint": lambda params: params.profit_percent > params.stop_percent
    }


class WoosterThree(bt.Strategy):
    """
    Godspeed, Wooster Three.
    """
    profit_percent = 1
    stop_percent = 1

    def init(self):
        self.cdl_engulfing = self.I(ta.CDLENGULFING, self.data.Open, self.data.High, self.data.Low, self.data.Close)

    def next(self):
        if self.cdl_engulfing[-1] == 100:
            self.buy(
                limit = self.data.Close[-1] * (1 + self.profit_percent/100),
                stop = self.data.Close[-1] * (1 - self.stop_percent/100)
            )
        elif self.cdl_engulfing[-1] == -100:
            self.sell(
                limit = self.data.Close[-1] * (1 - self.profit_percent/100) ,
                stop = self.data.Close[-1] * (1 + self.stop_percent/100)
            )
