"""
Wooster Two.
"""
# External imports
import backtesting as bt


class Params:
    """
    Param template for Wooster Two.
    """
    symbol = None
    timeframe = None
    period = None
    start = None
    end = None

    optimizers: dict = {
        "constraint": lambda params: True
    }


class WoosterTwo(bt.Strategy):
    """
    Godspeed, Wooster Two.

    
    """
    indicator = 123

    def init(self):
        """
        Indicators etc.
        """

    def next(self):
        """
        Trading logic.
        """
