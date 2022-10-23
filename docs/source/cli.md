# CLI Reference

Process, optimize, and view the results for Wooster trading systems.

**Usage**:

```console
$ wooster [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `cache`: Maintain a local store of cache market data,...
* `cachesystem`: Cache all the data necessary to backtest and...
* `coveragereport`: Launch a browser with the latest unit test...
* `diagnose`: Run comprehensive unittests on the entire...
* `latest`: Get the name and index of the latest Wooster...
* `launch`: Launch an existing results plot or...
* `optimizers`: See a system's optimized parameters (if the...
* `process`: Process a strategy by index, and optimize it...
* `results`: Display an already-computed system's results.

## `wooster cache`

Maintain a local store of cache market data, accessible by processors, to 
drastically speed up the 'data aggregation' phase of processing.

**Usage**:

```console
$ wooster cache [OPTIONS] ACTION [SYMBOL]
```

**Arguments**:

* `ACTION`: Either 'init', 'delete', or 'list'/'ls'.   [required]
* `[SYMBOL]`: Symbol to interface with. Unnecessary when using 'list'/'ls'.

**Options**:

* `--interval TEXT`: Interval to store the data in. 1m by default.  [default: 1m]
* `--lookbackyears INTEGER`: Number of years to aggregate historical data.  [default: 10]
* `--force / --no-force`: If a warning is returned that your cache exists, rewrite new cache.  [default: False]
* `--time / --no-time`: Display the amount of time the operation took.  [default: False]
* `--help`: Show this message and exit.

## `wooster cachesystem`

Cache all the data necessary to backtest and optimize a certain system. 

This is more efficient than initializing a window of data with the cache command,
without any regard for which sub-windows are actually used by the processing pipeline.

**Usage**:

```console
$ wooster cachesystem [OPTIONS] INDEX
```

**Arguments**:

* `INDEX`: Index of the system whose walkforward data you'd like to cache.  [required]

**Options**:

* `--cacheall / --no-cacheall`: Override index and cache necessary data for all Wooster systems.  [default: False]
* `--help`: Show this message and exit.

## `wooster coveragereport`

Launch a browser with the latest unit test coverage report.

**Usage**:

```console
$ wooster coveragereport [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `wooster diagnose`

Run comprehensive unittests on the entire Wooster system. 

If something seems awry in system functionality, this command will run 
comprehensive tests on all areas of functionality, including the entire
processing pipeline.

**Usage**:

```console
$ wooster diagnose [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `wooster latest`

Get the name and index of the latest Wooster system. You can use the index
to then process or launch results, if they exist, by calling 
`wooster process idx` or `wooster launch idx` where `idx` is replaced
by the output of this command.

**Usage**:

```console
$ wooster latest [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `wooster launch`

Launch an existing results plot or comprehensive performance stats in the browser. 
Use this command to view pre-computed results without having to re-process 
a strategy.

**Usage**:

```console
$ wooster launch [OPTIONS] INDEX VIEW
```

**Arguments**:

* `INDEX`: Numeric index of the queried strategy.  [required]
* `VIEW`: Specify whether launching the stats or a plot.  [required]

**Options**:

* `--label TEXT`: If opening a plot, specify train, up, down, or chop results.  [default: train]
* `--help`: Show this message and exit.

## `wooster optimizers`

See a system's optimized parameters (if the system has been optimized). If 
the system exists but no optimizers are shown, run the process command first. 

**Usage**:

```console
$ wooster optimizers [OPTIONS] INDEX
```

**Arguments**:

* `INDEX`: System index, ex. 2 for Wooster Two.  [required]

**Options**:

* `--help`: Show this message and exit.

## `wooster process`

Process a strategy by index, and optimize it based on the selected optimizer.

The default optimizer is set in config.ini, currently SQN. Specify 
a different optimizer with the --optimizer flag. You can optimize
pretty much any numeric metric as outputted in the results.

**Usage**:

```console
$ wooster process [OPTIONS] INDEX
```

**Arguments**:

* `INDEX`: Strategy identifier. Ex. 2 for Wooster Two.  [required]

**Options**:

* `--time / --no-time`: Time the operation and print the result to console.  [default: False]
* `--launch / --no-launch`: Launch a browser to interactively view the results plot.  [default: False]
* `--processall / --no-processall`: Override [blue]index[/] and process all systems.  [default: False]
* `--optimize / --no-optimize`: Optimize the strategy parameters.  [default: True]
* `--optimizer TEXT`: Change the performance metric being optimized.  [default: SQN]
* `--method TEXT`: Optimization method. Currently only grid and skopt are supported.  [default: grid]
* `--textalert / --no-textalert`: Send a text message alerting when the operation is over. This is useful when optimizing powerful, computationally intensive strategies. Must be pre-configured.  [default: False]
* `--help`: Show this message and exit.

## `wooster results`

Display an already-computed system's results. Does not re-process the system.
Results are displayed in the console, just as when processing a system. Use the
launch command to view results in the browser.

**Usage**:

```console
$ wooster results [OPTIONS] INDEX
```

**Arguments**:

* `INDEX`: Index of the system you want to view stored results for.  [required]

**Options**:

* `--help`: Show this message and exit.
