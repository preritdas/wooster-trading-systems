![pytest](https://github.com/preritdas/wooster-trading-systems/actions/workflows/pytest.yml/badge.svg)
![coverage-badge](tests/badge.svg)
![version](https://img.shields.io/badge/python-3.10-blue)
![maintenance-status](https://img.shields.io/badge/maintenance-actively--developed-brightgreen.svg)
![firebase](https://github.com/preritdas/wooster-trading-systems/actions/workflows/firebase-hosting-merge.yml/badge.svg)
![pages-build-deployment](https://github.com/preritdas/wooster-trading-systems/actions/workflows/pages/pages-build-deployment/badge.svg)


# :chart_with_upwards_trend: :robot: Wooster Systems :moneybag: :money_with_wings:

[![asciicast](https://asciinema.org/a/WZoORNecs2HiOfXnY7nquwtMo.svg)](https://asciinema.org/a/WZoORNecs2HiOfXnY7nquwtMo)

<!--features!-->
## Main features

- Predesigned proprietary Wooster trading strategies, most of which are ML-powered. Continually modifying and iterating on them.
- Comprehensive feature-packed CLI capable of independently handling all of the following features.
- Automatic backtesting of strategies against up to 10 years of historical data.
- Automatic multi-core optimization of strategy parameters on historical data, with the ability to change the optimized statistic (i.e. SQN, Sharpe Ratio, Return, etc.).
- Automatic backtesting of optimized strategy on out-of-sample uptrend, downtrend, and choppy market data, to combat overfitting and to see a strategy's true performance on new, un-optimized data. Walkforward principle, applied intentionally to various market conditions.
- Automatically formats above results (from all conditions) into beautiful HTML files, which automatically update on the [Wooster website](https://wooster.preritdas.com) on git push using GitHub Actions.
- Automatically generates sharp JS (Bokeh) interactive plots of above results, also automatically updated on the [Wooster website](https://wooster.preritdas.com) on git push.
- [Wooster website](https://wooster.preritdas.com) written in HTML and JavaScript with smart lookup - query strategy statistics or specific performance plots from the homepage.
- Data cache - initialize, view, and manage a local cache data repository to speed up data aggregation in the processing phase. When tuning and reprocessing a strategy, the walkforward data windows are often the same, so it doesn't make sense to (a) use up a data rate limit or (b) wait for the same data to download _again_ (especially when loading many years of intraday data for testing and optimization). An example (more sample CLI commands below): `wooster cache init aapl --interval 1m --lookbackyears 10` to store 10 years of minute bar data on AAPL, automatically used whenever any program feature tries to access 1m AAPL data within the last 10 years. 
  - With cached data, you can develop, train, optimize, backtest, and export systems _entirely_ offline.
- Data resampling - not constrained by Finnhub (or active data provider) timeframe/interval API limitations. For example, Finnhub only supports 1m, 5m, 15m, hourly, daily, and weekly data, meaning you cannot train and optimize a system on 2m or 10m data, for example. Now with completely under-the-hood support for resampling, without changing the behavior of the system setups - simply change the timefrmae in a system `Params` class. Works with caching, too.
- Parameter enforcement - The processing pipeline is independent of individual systems. Yet, it calls cataloged systems' `Params` class to gather all its information, from symbols to walk-forward windows to strategy optimizations. Thus, if a system's `Params` class fails to include a necessary attribute, or incorrectly structures a necessary attribute, the entire processing pipeline will likely fail. See PR #2.
- Full CI/CD pipeline. On pushes and pull requests, automatically run comprehensive tests on the processing pipeline, data aggregation, data caching, file lookups, utilities, and more, on Ubuntu, Linux, and macOS (CI). Automatically deploy rendered HTML files to the [wooster website](https://wooster.preritdas.com) (CD). All done via GitHub actions.

### Smaller features

- No-loss incremental aggregation of market data to comply with freemium data provider restrictions and rate limits.
- This is a really small one, among many useful command options, but deserves to be here nonetheless because of the immense convenience it's given me. `--textalert` option in `process` command to receive a text message once processing has completed. When a strategy has several parameters with wide value ranges, optimization can take a _very_ long time, as optimization tests the product of all parameter configurations. `--textalert` adds convenience to server-side deployment. Note that even the _setup_ for this feature is completely optional - if no Nexmo API keys are provided, no features are broken. The flag then simply does nothing.
- Optionally change not just the optimized statistic, but the optimization method itself - grid optimization or minimal forest optimization with scikit. If grid optimization (default) is used on most Mac/Darwin/Linux machines, optimization will make use of multiple cores, completing operations several times faster than otherwise.
- Defaults configuration through `config.ini` - modify preferred metrics, highlighted metrics, default optimizer, etc.
- Status handling across modules and submodules, because processing (aggregating up to 10 years of intraday non-cached data, backtesting, optimizing, re-backtesting on out-of-sample market conditions) can often take just a little while. Rich status icons and progress bars keep track of where the program is (and how far along) at almost all times. This includes estimated remaining time! For example, when optimizing many parameters on heavy data, you'll see a progress bar with an estimated time to optimization completion.
- Stored optimized parameter - whenever a strategy is optimized (via the `wooster process` command), the found optimal parameter combination is serialized as JSON and stored in the `results/optimizers` subdirectory. The `wooster optimizers` command allows a user to view the optimal parameter combination for a given strategy by index. Example directly below.
- Stored computed results - redisplay backtest and optimization results for a system without having to reprocess it. See PR #1.

```bash
# Stored optimal parameters example

> wooster optimizers 2

{
  'rsi_period': 9.0,
  'rsi_bottom_target': 13,
  'rsi_top_target': 87,
  'lstm_window': 5
}
```


# Dependencies

On top of the pip requirements, must have TA-Lib core (kind of a pain but use homebrew on Mac, tarball with python3.10-dev on Ubuntu, and the raw .whl file on Windows for v0.4.24). Firebase CLI is optional - website is automatically updated on git push as Firebase is configured with GitHub Actions. 


# Usage

Here are some random example commands from regular usage.

```bash
wooster latest 

wooster process 1 --time --optimizer "Sharpe Ratio" --method grid --textalert --launch
wooster process 2 --no-optimize
wooster process 1 --processall --textalert  # process/optimize every single system and alert when done

wooster cache init aapl --interval 5m --lookbackyears 5  # five years of 5m data cached
wooster cache delete aapl --interval 5m
wooster cache ls
wooster cachesystem 4  # only cache required data based on walk-forward intervals
wooster cachesystem 1 --cacheall  # cache required data for all systems

wooster diagnose  # run comprehensive unit tests on the whole architecture
wooster coveragereport  # launch unit test coverage report in browser

wooster results 4

wooster launch 1 stats  # open in browser
wooster launch 1 plot --label chop
```


# Unit Tests

Unit tests have been written to cover as close to all of the code as possible (current coverage is 97%). Run Pytest with `python -m pytest` instead of `pytest` as tests rely on project submodules, and this is easier than installing the whole project with `pip install -e .`. Unit tests are automatically run on `ubuntu-latest` using GitHub Actions on every push and pull request.


[![plot-preview](readme-content/plot_preview.PNG)](https://wooster.preritdas.com/plots/wooster%20one%20train.html)
