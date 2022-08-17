"""
Create the CLI.
"""
# External imports
import webbrowser
import typer
import pyperclip

# Local imports
from time import perf_counter # optionally time commands

# Project modules
import processing
import utils
import config
import texts


app = typer.Typer(
    no_args_is_help = True, 
    add_completion = False, 
    help = "Process, optimize, and view the results for Wooster trading systems."
)


@app.command()
def process(
    index: int = typer.Argument(
        ...,
        help = "Strategy identifier. Ex. 2 for Wooster Two."
    ),
    results: bool = typer.Option(
        default = True,
        help = "Deprecated. Results are now always shown for console html rendering."
    ),
    time: bool = typer.Option(
        default = False,
        help = "Time the operation and print the result to console."
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
        help = "Change the performance metric being optimized."
    ),
    textalert: bool = typer.Option(
        default = False,
        help = "Send a text message alerting when the operation is over. " \
            "This is useful when optimizing powerful, computationally " \
            "intensive strategies. Must be pre-configured."
    )
):
    """
    Process a strategy by index, and optimize it based on the selected optimizer.

    The default optimizer is set in config.ini, currently SQN. Specify 
    a different optimizer with the [blue]--optimizer[/] flag. You can optimize
    pretty much any numeric metric as outputted in the results.
    """
    if time: start = perf_counter()

    system_name = utils.idx_to_name(index)
    optimizing_str = "and optimizing " if optimize else ""
    utils.console.log(
        f"Processing {optimizing_str}[red]{system_name}[/].\n"
    )

    result = processing.process_system_idx(
        index, 
        optimize = optimize, 
        optimizer = optimizer
    )

    utils.console.line()
    result_table = utils.render_results(result[0], utils.idx_to_name(index))
    html_console = utils.create_recorded_console()
    html_console.print(result_table)
    html_console.save_html(utils.stats_path(index))

    if launch:
        with utils.console.status("Launching interactive plot in your browser."):
            webbrowser.open(result[1])
            pyperclip.copy(result[1])
            utils.console.print(
                "\nLaunched in your browser. If you'd like to use a different "
                "browser, paste the contents of your clipboard into your preferred browser."
            )
    
    if time: utils.console.print(f"That took {perf_counter() - start:.2f} seconds.")

    # Text alert
    if textalert:
        if not texts.keys_given():
            utils.console.print(
                "You must provide yoru Nexmo credentials in keys.ini "
                "if you'd like to use the textalert feature."
            )
            return

        texts.text_me(
            f"{system_name} has finished backtesting"
            f"{' and optimizing.' if optimize else '.'}"
        )
        

@app.command()
def latest():
    """
    Get the name and index of the latest Wooster system. You can use the index
    to then process or launch results, if they exist, by calling 
    `wooster process idx` or `wooster launch idx` where `idx` is replaced
    by the index specified by this command.
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
    Launch an existing results plot in the browser. Use this command to view 
    pre-computed results without having to re-process a strategy.
    """
    if not (path := utils.plot_path(index, flag_nonexistent=True)):
        utils.console.print(
            "There are currently no results stored for "
            f"[red]{utils.idx_to_name(index)}[/]. "
            "If the strategy exists, first process it with the [blue]process[/] command. "
            "Note that you can launch the interactive plot directly from the "
            "process command with the [blue]--launch[/] flag."
        )
        return

    webbrowser.open(path)
    pyperclip.copy(path)
    utils.console.print(
        "Launched in your browser. If you'd like to use a different "
        "browser, paste the contents of your clipboard into your preferred browser."
    )
