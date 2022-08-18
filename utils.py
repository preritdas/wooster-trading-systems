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

def _fetch_data(
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


def data(
    symbol: str, 
    interval: str,
    walkforward: dict[str, tuple[dt.datetime]]
) -> dict[str, pd.DataFrame]:
    """
    `walkforward` must be a dict containing walkforward labels, ex. train, up, down...
    The values with each of these must be a tuple with two, Datetime objects, the first
    being the start date and the end being the end date.
    """
    return_data = {}
    for label, start_end in walkforward.items():
        return_data[label] = _fetch_data(symbol, interval, start_end[0], start_end[1])

    return return_data


def full_label_name(label: str) -> str:
    """
    Returns the full label name. Ex. "train" becomes "In-Sample Training",
    "up" becomes "Out-of-Sample Uptrend", etc.
    """
    assert isinstance(label, str)
    assert (label := label.lower()) in {"train", "up", "down", "chop"}

    if label == "train": return "In-Sample Training Results"
    elif label == "up": return "Out-of-Sample Uptrend Results"
    elif label == "down": return "Out-of-Sample Downtrend Results"
    elif label == "chop": return "Out-of-Sample Chop Results"


# ---- Files ----

current_dir = os.path.dirname(
    os.path.realpath(__file__)
)


def plot_path(idx: int, label: str, flag_nonexistent: bool = False) -> bool | str:
    """
    Searches for the result path of the given indexed strategy.
    If it doesn't exist, returns False.

    Label is the plot type, either "train", "up", "down", or "chop". 
    """
    if not label in {"train", "up", "down", "chop"}:
        raise ValueError(f"Invalid plot label value, {label}.")
    
    label = label.title()

    name = idx_to_name(idx)
    path = os.path.join(current_dir, f"results/plots/{name} {label}.html")

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

def _render_results(results: pd.Series, idx: int = None, name: str = "") -> Table:
    """
    Renders results to console. Provide a results series. Only need to provide either
    `idx` or `name`. 
    """
    if name: name += " "
    if idx: name = idx_to_name(idx)

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


def display_results(
    results: dict[str, pd.Series], 
    idx: int, 
    record: bool = True
) -> None:
    """
    Print rendered results to console and save them to console.
    """
    if not isinstance(results, Table) and not isinstance(results, dict):
        raise ValueError("Results must be a table or dict of labeled tables.")

    html_console = create_recorded_console()
    if not record: html_console = Console()

    for label, result in results.items():
        table = _render_results(result)
        html_console.line()
        html_console.rule(full_label_name(label))
        html_console.line()
        html_console.print(table, justify="center")
        html_console.line()

    html_console.save_html(stats_path(idx))
