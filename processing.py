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

    stats = backtest.run(show_progress=True)

    if optimize:
        optimizers = systems.systems[index][1].Params.optimizers
        optimizers["maximize"] = optimizer
        stats = backtest.optimize(show_progress=True, **optimizers)

    plotpath = os.path.join(current_dir, "results", "plots", f"{name}.html")
    backtest.plot(filename=plotpath, open_browser=False)

    # Reset the page title so it's not the filename
    time.sleep(1)  # experimental: does this trigger OSError 22? 
    kit.append_by_query(
        query = "<title>",
        content = f"\t\t<title>{name}</title>",
        file = fr"{plotpath}",
        replace = True
    )

    # try:
    #     kit.append_by_query(
    #         query = "<title>",
    #         content = f"\t\t<title>{name}</title>",
    #         file = fr"{filepath}",
    #         replace = True
    #     )
    # except OSError as e:
    #     if "Invalid argument" in str(e): 
    #         utils.console.log("Caught invalid argument error.")
    #         time.sleep(1)
    #         kit.append_by_query(
    #             query = "<title>",
    #             content = f"\t\t<title>{name}</title>",
    #             file = fr"{filepath}",
    #             replace = True
    #         )
    #     else:
            # raise OSError(e)

    return stats, plotpath


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
