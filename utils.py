"""
Data downloads, etc.
"""
# External imports
import pandas as pd  # type hints
import num2words as numwords  # idx to words
import mypytoolkit as kit  # html title correciton

# Rich
from rich.console import Console; console = Console()
from rich.table import Table
from rich.text import Text

# Local imports
import os  # file paths
import config
import time  # prevent os error 22
import json  # store params as json

# Project modules
import systems


# ---- Constants ----

LABELS = {"train", "up", "down", "chop"}


# ---- Console tools ----

def create_recorded_console() -> Console:
    """
    Creates a new console object with recording enabled, 
    so it can then be exported as HTML etc.
    """
    return Console(record=True, width=120, height=25)


# ---- Labeling ---- 

def full_label_name(label: str) -> str:
    """
    Returns the full label name. Ex. "train" becomes "In-Sample Training",
    "up" becomes "Out-of-Sample Uptrend", etc.
    """
    assert isinstance(label, str)
    assert (label := label.lower()) in LABELS

    if label == "train": return "In-Sample Training Results"
    elif label == "up": return "Out-of-Sample Uptrend Results"
    elif label == "down": return "Out-of-Sample Downtrend Results"
    elif label == "chop": return "Out-of-Sample Chop Results"


# ---- Files ----

current_dir = os.path.dirname(
    os.path.realpath(__file__)
)


def handle_os_error(function):
    """
    Decorator to handle OS Error 22.
    """
    def wrapper(*args, **kwargs):
        try:
            function(*args, **kwargs)
        except OSError:
            time.sleep(0.1)
            wrapper(*args, **kwargs)

    return wrapper


def plot_path(idx: int, label: str, flag_nonexistent: bool = False) -> str:
    """
    Searches for the result path of the given indexed strategy.
    If it doesn't exist, returns False.

    Label is the plot type, either "train", "up", "down", or "chop". 
    """
    if label not in LABELS:
        raise ValueError(f"Invalid plot label value, {label}.")
    
    name = idx_to_name(idx, lower=True)
    path = os.path.join(current_dir, "results", "plots", f"{name} {label}.html")

    if flag_nonexistent:
        if not os.path.exists(path): return ""
    
    return path


def stats_path(idx: int, flag_nonexistent: bool = False) -> str:
    """
    Searches for the result path of the given indexed strategy.
    If it doesn't exist, returns False.
    """
    name = idx_to_name(idx, lower=True)
    path = os.path.join(current_dir, "results", "stats", f"{name}.html")

    if flag_nonexistent:
        if not os.path.exists(path): return ""
    
    return path


def results_path(idx: int, label: str) -> str:
    """
    Gets a results path.
    """
    assert isinstance(label, str)

    label = label.lower()
    assert label in LABELS

    name = idx_to_name(idx, lower=True)
    return os.path.join(current_dir, "results", "raw", f"{name} {label}.csv")


def system_exists(index: int) -> bool:
    """
    Check if a system by index. 
    """
    try:
        index = int(index)
    except ValueError:
        raise ValueError("Index must be an integer.")

    return index in systems.systems


@handle_os_error
def correct_html_title(name: str, filepath: str, insert: bool = False) -> None:
    """
    Opens the HTML file and replaces the <title> field 
    with the provided name. Recurses if OSError is raised,
    sleeping 0.1 seconds until it successfully fixes the file.

    If insert is true, inserts a new title tag after the <meta> tag,
    assuming there is no title tag in the document yet.
    """
    if insert:
        kit.append_by_query(
            query = "<meta",  # no close brace
            content = f"\t\t<title>{name}</title>", 
            file = fr"{filepath}",
            replace = False
        )
    else: 
        kit.append_by_query(
            query = "<title>",
            content = f"\t\t<title>{name}</title>",
            file = fr"{filepath}",
            replace = True
        )


@handle_os_error
def insert_html_favicon(filepath: str) -> None:
    """
    Inserts favicon.
    """
    kit.append_by_query(
        query = "<meta",
        content = '\t\t<link rel="icon" href="favicon.PNG">',
        file = fr"{filepath}"
    )


def store_params(system_name: str, params: dict) -> None:
    """
    Takes dictionary parameters (usually optimized) and stores them in the
    results/optimizers subdirectory, with a system name file name in JSON format.
    """
    system_name = system_name.lower()
    param_path = os.path.join(
        current_dir, 
        "results", 
        "optimizers", 
        f"{system_name}.json"
    )

    # Convert all data types to floats (np unrecognizable)
    params = {param: float(value) for param, value in params.items()}

    # Write the file
    with open(param_path, "w") as param_file: 
        param_file.write(json.dumps(params, indent=4))

    
def read_params(system_name: str = None, system_idx: int = None) -> dict[str, float]:
    """
    Reads stored parameters. Provide either `system_name` or `system_idx`. If both
    are provided for some reason, idx takes precendence. At least one must be provided.
    If the queried parameters json file does not exist, returns an empty dictionary.
    """
    if not system_name and not system_idx:
        raise ValueError("You must provide either a system name or index.")

    if system_name: system_name = system_name.lower()
    elif system_idx: system_name = idx_to_name(system_idx, lower=True)

    param_path = os.path.join(
        current_dir,
        "results",
        "optimizers",
        f"{system_name}.json"
    )

    # Ensure file exists
    if not os.path.exists(param_path): return {}

    with open(param_path, 'r') as param_file:
        return json.load(param_file)


# ---- Language ----

def idx_to_name(
    idx: int,
    prefix: str = "Wooster ",
    title: bool = True,
    lower: bool = False
) -> str:
    """
    Ex. turns `2` into "Wooster Two", and 23 into "Wooster TwentyTwo".

    `lower` supercedes title.
    """
    num = str(numwords.num2words(idx))
    words = [word.title() if title else word for word in num.split("-")]
 
    # Connect the words
    full_num = "".join(words)  

    # Deal with spaces and "and" if > 100
    full_num = "".join([word for word in full_num.split(" ") if word.lower() != "and"])

    _res = prefix + full_num
    return _res.lower() if lower else _res


# ---- Results ----

def store_results(idx: int, results: dict[str, pd.Series]) -> None:
    """
    Takes in fully computed dict results with labels and stores them as individual
    CSV files.
    """
    for label, result in results.items():
        path = results_path(idx, label)

        # Remove private, complex items like trades df and equity curve
        for metric, value in result.copy().iteritems():
            if metric[0] == "_": result.drop(metric, inplace=True)
            if isinstance(value, float): result[metric] = round(value, 3)

        result.to_csv(path)


def load_results(idx: int) -> dict[str, pd.Series]:
    """
    Loads previously stored results into format readable by display results.
    """
    results_dir = os.path.join(current_dir, "results", "raw")
    files = os.listdir(results_dir)

    results = {}
    for label in LABELS:
        expected_file = results_path(idx, label)
        
        if os.path.basename(expected_file) not in files: 
            continue

        # Read with squeeze to allow returning a series with one column
        results[label] = pd.read_csv(expected_file, index_col=0).squeeze("columns")

    return results


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
            "Secondary Performance Metrics", 
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
    if not isinstance(results, dict):
        raise ValueError("Results must be a dict with label keys and Series values.")

    html_console = create_recorded_console()
    if not record: html_console = Console()

    for label, result in results.items():
        table = _render_results(result)
        html_console.line()
        html_console.rule(full_label_name(label))
        html_console.line()
        html_console.print(table, justify="center")
        html_console.line()

    if record: 
        html_console.save_html(filepath := stats_path(idx))
        correct_html_title(
            name = f"{idx_to_name(idx)} Performance Metrics",
            filepath = filepath,
            insert = True
        )
        insert_html_favicon(filepath)
