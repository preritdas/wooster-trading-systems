"""
Process systems.
"""
# External imports
import backtesting as bt
import pandas as pd

# Local imports
import datetime as dt  # type hints
import os
import sys  # check operating system
import multiprocessing  # change start method if macOS

# Project modules
import systems
import utils
import data


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
    data: dict[str, pd.DataFrame],
    optimize: bool,
    optimizer: str,
    method: str,
    progress: bool
) -> dict[str, pd.Series]:
    """
    Base processor. Backtests, stores performance website, 
    and returns results series.

    Data must be passed as a dict, keys must be "train", "up", "down", and "chop."
    Each key's value must be a DataFrame. If a dict is passed and all four of these
    keys are not present with their correct values, a ValueError is raised.

    Returns a tuple containing the results series and a string path 
    to the interactive plot.
    """
    assert isinstance(data, dict)
    assert "train" in data.keys(), "You must always provide training data."
    assert all([label in utils.LABELS for label in data.keys()])
    assert all(isinstance(value, pd.DataFrame) for value in data.values())

    backtest = bt.Backtest(
        data = data["train"],
        strategy = strategy,
        cash = 100_000
    )
    
    stats = backtest.run(show_progress=progress)
    params: dict = stats._strategy._params

    if optimize:
        stats = backtest.optimize(
            max_tries = 1,
            show_progress = progress,
            method = method,
            maximize = optimizer,
            **systems.systems[index][1].Params.optimizers
        )

        # Store optimized params locally and as CSV
        params = stats._strategy._params
        utils.store_params(name, params)

   # Use precomputed train backtest results and save plot
    results = {"train": stats}
    _plotpath = utils.plot_path(index, "train")
    with utils.console.status(
        "Plotting and exporting training results to HTML..."
    ):
        backtest.plot(filename=_plotpath, open_browser=False, resample=False)
        utils.correct_html_title(f"{name.title()} Training Results", _plotpath)
        utils.insert_html_favicon(_plotpath)

    # Backtest the other labeled conditions
    for pos, label in enumerate(data):
        if label == "train": continue  # pre-computed train data handled above

        _walkforward_bt = bt.Backtest(
            data[label], 
            strategy, 
            cash = 100_000
        )
        results[label] = _walkforward_bt.run(
            show_progress = True,
            progress_message = f"Testing {'optimized' if optimize else ''} " \
                f"strategy on {label} data...",
            newline = pos == 1,  # insert newline if first test after train
            **params
        )
        
        # Save results
        with utils.console.status(
            f"Plotting and exporting {label.lower()} results to HTML..."
        ):
            _plotpath = utils.plot_path(index, label)
            _walkforward_bt.plot(filename=_plotpath, open_browser=False, resample=False)

            # Reset the page title so it's not the filename
            utils.correct_html_title(f"{name.title()} {label.title()} Results", _plotpath)
            utils.insert_html_favicon(_plotpath)

    utils.store_results(index, results)
    return results


def _fetch_walkforward(system_idx: int) -> dict[str, tuple[dt.date, dt.date]]:
    """
    Read through the systems catalog and return the walkforward specified in the
    system's Params class. This was separated because it'll likely be of use in 
    other external functions.
    """
    return systems.systems[system_idx][1].Params.walkforward


def process_system_idx(
    index: int, 
    optimize: bool, 
    optimizer: str = None,
    method = "grid",
    progress: bool = True
) -> dict[str, pd.Series]:
    """
    Find and process a system by its given index.

    Returns a tuple containing the results series and a string path 
    to the interactive plot.
    """
    if not isinstance(index, int):
        raise ValueError("Index must be an integer.")

    if optimize and optimizer is None:
        raise ValueError("You requested optimization but provided no optimizer.")

    system = systems.systems[index]

    return _process_system(
        strategy = system[2],
        name = system[0],
        index = index,
        data = data.data(
            symbol = system[1].Params.symbol,
            interval = system[1].Params.timeframe,
            walkforward = _fetch_walkforward(index),
            filter_eod = system[1].Params.filter_eod
        ),
        optimize = optimize,
        optimizer = optimizer,
        method = method,
        progress = progress
    )
