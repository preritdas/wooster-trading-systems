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
    assert (label := label.lower()) in {"train", "up", "down", "chop"}

    if label == "train": return "In-Sample Training Results"
    elif label == "up": return "Out-of-Sample Uptrend Results"
    elif label == "down": return "Out-of-Sample Downtrend Results"
    elif label == "chop": return "Out-of-Sample Chop Results"


# ---- Files ----

current_dir = os.path.dirname(
    os.path.realpath(__file__)
)


def create_new_system() -> bool:
    """
    CURRENTLY NOT FUNCTIONAL AND NOT USED.

    Create .py system file for the next system. Returns True if successful,
    False if the file already exists, meaning the new system hasn't yet been
    indexed in the systems.systems dictionary.
    """
    idx = max(systems.systems) + 1
    module_name = idx_to_name(idx, predix="", title=False)
    module_path = os.path.join(current_dir, "systems", f"{module_name}.py")
    
    # Ensure it doesn't yet exist
    if os.path.exists(module_path):
        return False

    # Make the file
    with open(module_path, "w", encoding="utf-8") as module:
        module.write("put template contents here.")


def plot_path(idx: int, label: str, flag_nonexistent: bool = False) -> bool | str:
    """
    Searches for the result path of the given indexed strategy.
    If it doesn't exist, returns False.

    Label is the plot type, either "train", "up", "down", or "chop". 
    """
    if not label in {"train", "up", "down", "chop"}:
        raise ValueError(f"Invalid plot label value, {label}.")
    
    name = idx_to_name(idx, lower=True)
    path = os.path.join(current_dir, "results", "plots", f"{name} {label}.html")

    if flag_nonexistent:
        if not os.path.exists(path): return False
    
    return path


def stats_path(idx: int = None, flag_nonexistent: bool = False) -> bool | str:
    """
    Searches for the result path of the given indexed strategy.
    If it doesn't exist, returns False.
    """
    name = idx_to_name(idx, lower=True)
    path = os.path.join(current_dir, "results", "stats", f"{name}.html")

    if flag_nonexistent:
        if not os.path.exists(path): return False
    
    return path


def system_exists(index: int) -> bool:
    """
    Check if a system by index. 
    """
    try:
        index = int(index)
    except ValueError as e:
        raise ValueError("Index must be an integer.")

    return index in systems.systems


def correct_html_title(name: str, filepath: str, insert: bool = False) -> None:
    """
    Opens the HTML file and replaces the <title> field 
    with the provided name. Recurses if OSError is raised,
    sleeping 0.1 seconds until it successfully fixes the file.

    If insert is true, inserts a new title tag after the <meta> tag,
    assuming there is no title tag in the document yet.
    """
    try:
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
    except OSError:
        time.sleep(0.1)
        correct_html_title(name, filepath, insert)


def insert_html_favicon(filepath: str) -> None:
    """
    Inserts favicon.
    """
    try:
        kit.append_by_query(
            query = "<meta",
            content = '\t\t<link rel="icon" href="favicon.PNG">',
            file = fr"{filepath}"
        )
    except OSError:
        time.sleep(0.1)
        insert_html_favicon(filepath)


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

    html_console.save_html(filepath := stats_path(idx))
    correct_html_title(
        name = f"{idx_to_name(idx)} Performance Metrics",
        filepath = filepath,
        insert = True
    )
    insert_html_favicon(filepath)
