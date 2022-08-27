"""
Wooster One with trade exits based on RSI. Extermely simple strategies, such that 
any bottleneck is infrastructural rather than strategy related. Real, promising
strategies come later.
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

    walkforward = {
        "train": (dt.date(2014, 7, 1), dt.date(2015, 8, 31)),
        "up": (dt.date(2021, 7, 1), dt.date(2022, 1, 1)),
        "down": (dt.date(2018, 9, 1), dt.date(2019, 2, 1)),
        "chop": (dt.date(2020, 9, 1), dt.date(2021, 2, 20))
    }

    optimizers: dict = {
        "rsi_period": range(3, 20, 1),
        "buy_rsi_entry": range(15, 25, 1),
        "buy_rsi_target": range(75, 90, 1),
        "sell_rsi_entry": range(75, 85, 1),
        "sell_rsi_target": range(10, 25, 1),
        "constraint": lambda params: params.buy_rsi_entry < params.buy_rsi_target and params.sell_rsi_entry > params.sell_rsi_target
    }


class WoosterTwo(bt.Strategy):
    """
    Godspeed, Wooster Two.

    Same as Wooster One but sell the position if RSI crosses 50, from
    either direction. Simple strategy, see docstring at the top of this
    module.
    """
    rsi_period = 14
    buy_rsi_entry = 20
    buy_rsi_target = 50
    sell_rsi_entry = 80
    sell_rsi_target = 50

    def init(self):
        """
        Initialize RSI for later use.
        """
        self.rsi = self.I(ta.RSI, self.data.Close, timeperiod=self.rsi_period)

    def next(self):
        """
        Trading logic - Wooster One, but cloes the position when RSI hits its
        targets (defined as optimizable class variable parameters).
        """
        # Position management
        if self.position.is_long:  # check for buy target
            if self.rsi[-1] >= self.buy_rsi_target: self.position.close()
        if self.position.is_short:
            if self.rsi[-1] <= self.sell_rsi_target: self.position.close()
        
        # New positions
        if self.rsi[-1] < self.buy_rsi_entry: self.buy()
        elif self.rsi[-1] > self.sell_rsi_entry: self.sell()
