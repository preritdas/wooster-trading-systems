"""
Create the CLI.
"""
# External imports
import webbrowser
import typer; app = typer.Typer()
import pyperclip

# Project modules
import processing
import utils
import config


@app.command()
def process(
    index: int,
    results: bool = typer.Option(
        default = True,
        help = "Show a rendering of the system's performance."
    ),
    launch: bool = typer.Option(
        default = False,
        help = "Launch a browser to interactively view the results plot."
    ),
    optimize: bool = typer.Option(
        default = True,  
        help = "Optimize the strategy parameters."
    ),
    optimizer: str = typer.Option(
        default = config.Optimization.default_optimizer,
        help = "Choose what statistic to optimize."
    )
):
    """
    Process a strategy by index, and optimize it based on the selected optimizer.
    """
    optimizing_str = "and optimizing " if optimize else ""
    with utils.console.status(
        f"Processing {optimizing_str}{utils.idx_to_name(index)}."
    ):
        result = processing.process_system_idx(
            index, 
            optimize = optimize, 
            optimizer = optimizer
        )

    if results: utils.render_results(result[0])

    if launch:
        with utils.console.status("Launching interactive plot in your browser."):
            webbrowser.open(result[1])
            pyperclip.copy(result[1])
            utils.console.print(
                "\nLaunched in your browser. If you'd like to use a different "
                "browser, paste the contents of your clipboard into your preferred browser."
            )
        

@app.command()
def latest():
    """
    Get the name and index of the latest Wooster system. 
    """
    idx = max(processing.systems.systems)
    name = utils.idx_to_name(idx)

    utils.console.print(
        f"The latest system is [red]{name}[/]. "
        f"As its name suggests, you can process it with the index [red]{idx}[/]."
    )


@app.command()
def launch(
    index: int = typer.Argument(
        ..., 
        help="Numeric index of the queried strategy."
    )
):
    """
    Launch an existing results plot in the browser.
    """
    if not (path := utils.plot_path(index)):
        utils.console.print(
            f"There are currently no results stored for {utils.idx_to_name(index)}. "
            "If the strategy exists, process it with the `process` command. "
        )
        return

    webbrowser.open(path)
    pyperclip.copy(path)
    utils.console.print(
        "Launched in your browser. If you'd like to use a different "
        "browser, paste the contents of your clipboard into your preferred browser."
    )