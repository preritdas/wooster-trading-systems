"""
Process systems.
"""
# External imports
import backtesting as bt
import pandas as pd

# Local imports
import os

# Project modules
import systems
import utils


# ---- Absolute file paths ----

current_dir = os.path.dirname(
    os.path.realpath(__file__)
)


def _process_system(
    strategy: bt.Strategy, 
    name: str, 
    data: pd.DataFrame
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
    filename = os.path.join(current_dir, f"results/{name}.html")
    backtest.plot(filename=filename, open_browser=False)

    return stats, filename


def process_system_idx(index: int) -> tuple[pd.Series, str]:
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
        data = utils.data(
            symbol = system[1].Params.symbol,
            interval = system[1].Params.timeframe,
            period = system[1].Params.period
        )
    )


def process_latest_system() -> tuple[pd.Series, str]:
    """
    Process the latest system based on the systems submodule catalog.

    Returns a tuple containing the results series and a string path 
    to the interactive plot.
    """
    return process_system_idx(index=max(systems.systems))
