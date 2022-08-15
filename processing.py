"""
Process systems.
"""
# External imports
import backtesting as bt
import pandas as pd

# Local imports
import os
import multiprocessing; multiprocessing.set_start_method('fork')

# Project modules
import systems
import utils


# ---- Absolute file paths ----

current_dir = os.path.dirname(
    os.path.realpath(__file__)
)


# ---- Strategy backtests and processing ----

def _process_system(
    strategy: bt.Strategy, 
    name: str,
    index: int,
    data: pd.DataFrame,
    optimize: bool,
    optimizer: str
) -> tuple[pd.Series, str]:
    """
    Base processor. Backtests, stores performance website, 
    and returns results series.

    Returns a tuple containing the results series and a string path 
    to the interactive plot.
    """
    backtest = bt.Backtest(
        data = data,
        strategy = strategy,
        cash = 100_000
    )

    stats = backtest.run()

    if optimize:
        optimizers = systems.systems[index][1].Params.optimizers
        optimizers["maximize"] = optimizer
        stats = backtest.optimize(**optimizers)

    filename = os.path.join(current_dir, f"results/plots/{name}.html")
    backtest.plot(filename=filename, open_browser=False)

    return stats, filename


def process_system_idx(
    index: int, 
    optimize: bool, 
    optimizer: str
) -> tuple[pd.Series, str]:
    """
    Find and process a system by its given index.

    Returns a tuple containing the results series and a string path 
    to the interactive plot.
    """
    if not isinstance(index, int):
        raise ValueError("Index must be an integer.")

    system = systems.systems[index]

    return _process_system(
        strategy = system[2],
        name = system[0],
        index = index,
        data = utils.data(
            symbol = system[1].Params.symbol,
            interval = system[1].Params.timeframe,
            start = system[1].Params.start,
            end = system[1].Params.end
        ),
        optimize = optimize,
        optimizer = optimizer
    )
