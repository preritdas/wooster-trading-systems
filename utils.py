"""
Data downloads, etc.
"""
# External imports
import yfinance as yf  # data
import pandas as pd  # type hints
from rich.console import Console; console = Console()
import num2words as numwords  # idx to words

# Local imports
import os  # file paths
import datetime as dt


# ---- Data ----

def data(
    symbol: str, 
    interval: str, 
    start: dt.datetime,
    end: dt.datetime
) -> pd.DataFrame:
    """
    Download data from yfinance. Does not work with period, must take start
    and end as datetime type, where end is at least one day prior. 
    This is because if you run the system while the market is open, plotting breaks.
    """
    return yf.download(
        tickers = symbol,
        interval = interval,
        start = start,
        end = end,
        progress = False,
        show_errors = True
    )


# ---- Files ----

current_dir = os.path.dirname(
    os.path.realpath(__file__)
)


def plot_path(idx: int = None) -> bool | str:
    """
    Searches for the result path of the given indexed strategy.
    If it doesn't exist, returns False.
    """
    name = idx_to_name(idx)
    path = os.path.join(current_dir, f"results/plots/{name}.html")

    if not os.path.exists(path):
        return False
    
    return path


# ---- Language ----

def idx_to_name(idx: int, prefix: str = "Wooster ") -> str:
    """
    Ex. turns `2` into "Wooster Two", and 23 into "Wooster TwentyTwo".
    """
    num = str(numwords.num2words(idx))
    words = [word.title() for word in num.split("-")]

    full_num = ""
    # Join them
    for word in words:
        full_num += word

    return prefix + full_num


# ---- Renders ----

def render_results(results: pd.Series) -> None:
    """
    Renders results to console.
    """
    console.print(results)
