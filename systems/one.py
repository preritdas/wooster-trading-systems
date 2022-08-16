"""
Wooster One trading system, trained and backtested.
"""
# External imports
import talib as ta
import backtesting as bt

# Local imports
import datetime as dt


class Params:
    """
    Strategy meta-configurations. These are not indicator settings, or 
    any such optimizable parameters; rather, symbols, timeframes, 
    date-ranges, etc.
    """
    symbol = "AAPL"
    timeframe = "5m"
    period = "60d"
    start = dt.datetime.today() - dt.timedelta(days=55)
    end = dt.datetime.today() - dt.timedelta(days=1)

    optimizers = {
        "rsi_period": range(2, 30),
        "constraint": lambda params: params.rsi_period > 2  # handled by above
    }


# ---- Strategy ----

class WoosterOne(bt.Strategy):
    """
    Godspeed, Wooster One.

    A simple, first strategy. If the RSI is above 80 overbought, sell. 
    If it's under 20 oversold, buy. Wooster Two will close the position once 
    the RSI crosses 50, on either end.
    """
    rsi_period = 14

    def init(self):
        """
        Abstract strategy method to define and wrap indicators etc.
        """
        self.rsi = self.I(ta.RSI, self.data.Close, timeperiod=self.rsi_period)

    def next(self):
        # Sell signal
        if self.rsi[-1] > 80:
            if self.position.is_long: self.position.close()
            elif not self.position: self.sell()

        # Buy signal
        elif self.rsi[-1] < 20:
            if self.position.is_short: self.position.close()
            elif not self.position: self.buy()
