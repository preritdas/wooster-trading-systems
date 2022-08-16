"""
Data downloads, etc.
"""
# External imports
from sys import displayhook
import yfinance as yf  # data
import pandas as pd  # type hints
import num2words as numwords  # idx to words

# Rich
from rich.console import Console; console = Console()
from rich.table import Table
from rich.text import Text

# Local imports
import os  # file paths
import datetime as dt
import config


# ---- Console tools ----
def create_recorded_console() -> Console:
    """
    Creates a new console object with recording enabled, 
    so it can then be exported as HTML etc.
    """
    return Console(record=True)


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


def plot_path(idx: int = None, flag_nonexistent: bool = False) -> bool | str:
    """
    Searches for the result path of the given indexed strategy.
    If it doesn't exist, returns False.
    """
    name = idx_to_name(idx)
    path = os.path.join(current_dir, f"results/plots/{name}.html")

    if flag_nonexistent:
        if not os.path.exists(path): return False
    
    return path


def stats_path(idx: int = None, flag_nonexistent: bool = False) -> bool | str:
    """
    Searches for the result path of the given indexed strategy.
    If it doesn't exist, returns False.
    """
    name = idx_to_name(idx)
    path = os.path.join(current_dir, f"results/stats/{name}.html")

    if flag_nonexistent:
        if not os.path.exists(path): return False
    
    return path


# ---- Language ----

def idx_to_name(idx: int, prefix: str = "Wooster ") -> str:
    """
    Ex. turns `2` into "Wooster Two", and 23 into "Wooster TwentyTwo".
    """
    num = str(numwords.num2words(idx))
    words = [word.title() for word in num.split("-")]

    full_num = ""
    for word in words: full_num += word

    return prefix + full_num


# ---- Renders ----

def render_results(results: pd.Series, name: str = "") -> Table:
    """
    Renders results to console.
    """
    if name: name += " "

    # Get all metrics as long as they're not private attributes
    all_metrics = [metric for metric in results.index if metric[0] != "_"]
    
    # Preferred metrics

    preferred_table = Table(
        title = f"[red]{name}[/]Preferred Performance Metrics",
        style = "dim"
    )
    preferred_table.add_column("Metric")
    preferred_table.add_column("Value")

    for metric in config.Results.preferred_metrics:
        all_metrics.remove(metric)
        if isinstance((result := results[metric]), float): result = round(result, 3)

        # Style certain results
        style = "none"
        if metric in config.Results.highlight_preferred:
            style = config.Results.highlight_preferred_style
        preferred_table.add_row(Text(metric, style), Text(str(result), style))

    # Secondary metrics, loop over remaining metrics

    secondary_table = Table(
        title = Text(
            f"Secondary Performance Metrics", 
            style=config.Results.secondary_metrics_style
        ), 
        style = config.Results.secondary_metrics_style
    )
    secondary_table.add_column(
        Text(
            "Metric", 
            style=config.Results.secondary_metrics_style
        )
    )
    secondary_table.add_column(
        Text(
            "Value", 
            style=config.Results.secondary_metrics_style
        )
    )

    for metric in all_metrics: 
        if isinstance((result := results[metric]), float): result = round(result, 3)
        secondary_table.add_row(
            Text(
                metric, 
                style=config.Results.secondary_metrics_style
            ), 
            Text(str(result), style=config.Results.secondary_metrics_style)
        )

    # Display

    display_table = Table.grid(padding=0, expand=False)
    display_table.add_column(""); display_table.add_column("")
    display_table.add_row(preferred_table, secondary_table)

    return display_table
