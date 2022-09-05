"""
Check a system's Params class to ensure it has all the required, properly structured
information. If it doesn't, the whole processing pipeline is thrown off. Eventually,
explore replacing this with Pydantic.
"""
import datetime as dt
import sys
import config
import utils


# ---- Necessary structure ----

params_structure = {
    "symbol": lambda attr: isinstance(attr, str),
    "timeframe": lambda attr: isinstance(attr, str) \
        and any(True for suf in {"m", "h", "d", "w"} if attr.endswith(suf)),
    "filter_eod": lambda attr: isinstance(attr, bool),
    "walkforward": lambda attr: isinstance(attr, dict) \
        and all([isinstance(key, str) for key in attr.keys()]) \
        and all([key in {"train", "up", "down", "chop"} for key in attr.keys()]) \
        and all([isinstance(val, tuple) for val in attr.values()]) \
        and all([isinstance(val, dt.date) or isinstance(dt.datetime) \
            for tups in attr.values() for val in tups]),
    "optimizers": lambda attr: isinstance(attr, dict) \
        and all([isinstance(key, str) for key in attr.keys()])
}


def check_system(params_class, idx: int) -> None:
    """
    Checks the class. If an error is found, a fatal exception or assertion error 
    is thrown.
    """
    # Ensure parameter enforcement is enabled in config
    if not config.Systems.parameter_enforcement: return

    assert isinstance(idx, int)
    attrs = params_class.__dict__

    error_prefix = f"System {idx} parameter enforcement error:"
    error_style = "bold red"

    for attr, check in params_structure.items():
        if not attr in attrs:
            utils.console.log(
                f"{error_prefix} Attribute '{attr}' not in system {idx} Params class.",
                style = error_style
            )
            sys.exit()
        if not check(attrs[attr]):
            utils.console.log(
                f"{error_prefix} "
                f"System {idx} Params attribute '{attr}' failed its structural test.",
                style = error_style
            )
            sys.exit()
