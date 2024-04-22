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


# class WoosterSeven(bt.Strategy):
#     """Adjust the strategy to use limit orders."""
#     LEVEL_DISTANCE = 0.01
#     PIP = 0.00001

#     def init(self):
#         self.prev_nearest_level_above: float | None = None
#         self.prev_nearest_level_above: float | None = None

#         self.nearest_level_below: float | None = None
#         self.nearest_level_below: float | None = None

#     def adjust_and_trade(self):
#         self.nearest_level_above = adjust_level(self.data["High"][-1], 'up', self.LEVEL_DISTANCE)
#         self.nearest_level_below = adjust_level(self.data["Low"][-1], 'down', self.LEVEL_DISTANCE)

#         if self.prev_nearest_level_above is None:
#             self.prev_nearest_level_above = self.nearest_level_above
#             self.prev_nearest_level_below = self.nearest_level_below
#             return

#         lowest_last_hour = self.data["Low"][-60:].min()
#         highest_last_hour = self.data["High"][-60:].max()

#         if not (
#             lowest_last_hour > self.prev_nearest_level_below
#             and highest_last_hour < self.prev_nearest_level_above
#         ):
#             return

#         if not (
#             self.prev_nearest_level_above == self.nearest_level_above
#             and self.prev_nearest_level_below == self.nearest_level_below
#         ):
#             return

#         for order in self.orders:
#             if order.limit in {self.prev_nearest_level_above, self.prev_nearest_level_below}:
#                 order.cancel()

#         self.buy(
#             size=1,
#             tp=self.prev_nearest_level_below + (20 * self.PIP),
#             sl=self.prev_nearest_level_below - (20 * self.PIP),
#             limit=self.prev_nearest_level_below
#         )
#         self.sell(
#             size=1,
#             tp=self.prev_nearest_level_above - (20 * self.PIP),
#             sl=self.prev_nearest_level_above + (20 * self.PIP),
#             limit=self.prev_nearest_level_above
#         )

#         self.prev_nearest_level_above = self.nearest_level_above
#         self.prev_nearest_level_below = self.nearest_level_below

#     def next(self):
#         self.adjust_and_trade()


class WoosterSeven(bt.Strategy):
    """Adjust the strategy to use limit orders."""
    LEVEL_DISTANCE = 0.01
    PIP = 0.00001

    def init(self):
        self.nearest_level_above: float | None = None
        self.nearest_level_below: float | None = None
        self.lag_trade_count = 0

    def calc_levels(self):
        self.nearest_level_above = adjust_level(self.data["High"][-1], 'up', self.LEVEL_DISTANCE)
        self.nearest_level_below = adjust_level(self.data["Low"][-1], 'down', self.LEVEL_DISTANCE)

    def in_range(self) -> bool:
        highest_last_60 = self.data["High"][-12:].max()
        lowest_last_60 = self.data["Low"][-12:].min()
        return self.nearest_level_below < lowest_last_60 < highest_last_60 < self.nearest_level_above

    def cancel_orders(self):
        for order in self.orders:
            order.cancel()

    def place_orders(self):
        for order in self.orders:
            if order.limit in {self.nearest_level_above, self.nearest_level_below}:
                order.cancel()

        self.buy(
            size=1,
            tp=self.nearest_level_below + (100 * self.PIP),
            sl=self.nearest_level_below - (100 * self.PIP),
            limit=self.nearest_level_below
        )
        self.sell(
            size=1,
            tp=self.nearest_level_above - (100 * self.PIP),
            sl=self.nearest_level_above + (100 * self.PIP),
            limit=self.nearest_level_above
        )

    def next(self):
        self.calc_levels()

        if self.in_range() and self.position.size == 0:
            self.place_orders()
