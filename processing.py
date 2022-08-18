"""
Process systems.
"""
# External imports
import backtesting as bt
import pandas as pd
import mypytoolkit as kit

# Local imports
import os
import sys  # check operating system
import multiprocessing  # change start method if macOS
import time  # handle invalid argument OSError 22

# Project modules
import systems
import utils


# Multiprocessing start method for backtesting
if sys.platform == "darwin": multiprocessing.set_start_method("fork")


# ---- Absolute file paths ----

current_dir = os.path.dirname(
    os.path.realpath(__file__)
)


# ---- Strategy backtests and processing ----

def _process_system(
    strategy: bt.Strategy, 
    name: str,
    index: int,
    data: pd.DataFrame | dict[str, pd.DataFrame],
    optimize: bool,
    optimizer: str,
    method: str,
    progress: bool
) -> tuple[pd.Series, str]:
    """
    Base processor. Backtests, stores performance website, 
    and returns results series.

    If data is passed in as a dict, keys must be "train", "up", "down", and "chop."
    Each key's value must be a DataFrame. If a dict is passed and all four of these
    keys are not present with their correct values, a ValueError is raised.

    Returns a tuple containing the results series and a string path 
    to the interactive plot.
    """
    # If dict, ensure data is labeled properly with DataFrame data
    if isinstance(data, dict) and optimize:
        assert "train" in data and "up" in data and "down" in data and "chop" in data
        assert isinstance(data["train"], pd.DataFrame) \
            and isinstance(data["up"], pd.DataFrame) \
            and isinstance(data["down"], pd.DataFrame) \
            and isinstance(data["chop"], pd.DataFrame)

    backtest = bt.Backtest(
        data = data,
        strategy = strategy,
        cash = 100_000
    )

    stats = backtest.run(show_progress=progress)

    if optimize:
        optimizers = systems.systems[index][1].Params.optimizers
        optimizers["maximize"] = optimizer
        stats = backtest.optimize(
            max_tries = 1, 
            show_progress = progress, 
            method = method, 
            **optimizers
        )

    plotpath = os.path.join(current_dir, "results", "plots", f"{name}.html")
    backtest.plot(filename=plotpath, open_browser=False)

    # Reset the page title so it's not the filename
    time.sleep(1)  # Prevent OS error 22
    kit.append_by_query(
        query = "<title>",
        content = f"\t\t<title>{name}</title>",
        file = fr"{plotpath}",
        replace = True
    )

    return stats, plotpath


def process_system_idx(
    index: int, 
    optimize: bool, 
    optimizer: str,
    method = "grid",
    progress: bool = True
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
        optimizer = optimizer,
        method = method,
        progress = progress
    )
