import backtesting as bt
import datetime as dt


class Params:
    """
    Strategy meta-configurations. These are not indicator settings, or 
    any such optimizable parameters; rather, symbols, timeframes, 
    date-ranges, etc.
    """
    symbol = "EURUSD"
    timeframe = "5m"
    filter_eod = False

    walkforward = {
        "train": (dt.date(2022, 1, 10), dt.date(2022, 1, 23)),
    }

    optimizers = {
        "constraint": lambda params: True
    }


def adjust_level(level: float, dir: str, level_distance: float) -> float:
    assert (dir := dir.lower()) in {'up', 'down'}, "Direction must be 'up' or 'down'."

    if abs(level % level_distance) < 1e-9:
        return level

    return level_distance * (level // level_distance + (1 if dir == 'up' else 0))


class WoosterSix(bt.Strategy):
    """
    Identifies psychological reversal points according to round numbers.
    Trades a reversal when the price crosses a round number.
    Only run on EURUSD - psychological levels are every 0.01.
    """
    LEVEL_DISTANCE = 0.01
    PIP = 0.00001

    def init(self):
        self.prev_nearest_level_above: float | None = None
        self.prev_nearest_level_below: float | None = None

    def next(self):
        self.prev_nearest_level_above = adjust_level(self.data["High"][-2], 'up', self.LEVEL_DISTANCE)
        self.prev_nearest_level_below = adjust_level(self.data["Low"][-2], 'down', self.LEVEL_DISTANCE)

        # Check for a touch/breach above
        if self.data["High"][-1] > self.prev_nearest_level_above:
            self.sell(
                size=1,
                tp=self.data.Close[-1] - (100 * self.PIP),
                sl=self.data.Close[-1] + (100 * self.PIP),
            )
        elif self.data["Low"][-1] < self.prev_nearest_level_below:
            self.buy(
                size=1,
                tp=self.data.Close[-1] + (100 * self.PIP),
                sl=self.data.Close[-1] - (100 * self.PIP)
            )
