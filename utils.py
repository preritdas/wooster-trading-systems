"""
Data downloads, etc.
"""
import yfinance as yf
import pandas as pd
from rich.console import Console; console = Console()
import num2words as numwords


# ---- Data ----

def data(symbol: str, interval: str, period: str) -> pd.DataFrame:
    """
    Download data from yfinance.
    """
    return yf.download(
        tickers = symbol,
        interval = interval,
        period = period,
        progress = False,
        show_errors = True
    )


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
