# Wooster Systems

[![asciicast](https://asciinema.org/a/WZoORNecs2HiOfXnY7nquwtMo.svg)](https://asciinema.org/a/WZoORNecs2HiOfXnY7nquwtMo)

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

### Smaller features

- No-loss incremental aggregation of market data to comply with freemium data provider restrictions and rate limits.
- This is a really small one, among many useful command options, but deserves to be here nonetheless because of the immense convenience it's given me. `--textalert` option in `process` command to receive a text message once processing has completed. When a strategy has several parameters with wide value ranges, optimization can take a _very_ long time, as optimization tests the product of all parameter configurations. `--textalert` adds convenience to server-side deployment. Note that even the _setup_ for this feature is completely optional - if no Nexmo API keys are provided, no features are broken. The flag then simply does nothing.
- Optionally change not just the optimized statistic, but the optimization method itself - grid optimization or minimal forest optimization with scikit. If grid optimization (default) is used on most Mac/Darwin/Linux machines, optimization will make use of multiple cores, completing operations several times faster than otherwise.
- Defaults configuration through [config.ini](config.ini) - modify preferred metrics, highlighted metrics, default optimizer, etc.
- Status handling across modules and submodules, because processing (aggregating up to 10 years of intraday non-cached data, backtesting, optimizing, re-backtesting on out-of-sample market conditions) can often take just a little while. Rich status icons and progress bars keep track of where the program is (and how far along) at almost all times. This includes estimated remaining time! For example, when optimizing many parameters on heavy data, you'll see a progress bar with an estimated time to optimization completion.
- Stored optimized parameter - whenever a strategy is optimized (via the `wooster process` command), the found optimal parameter combination is serialized as JSON and stored in the `results/optimizers` subdirectory. The `wooster optimizers` command allows a user to view the optimal parameter combination for a given strategy by index. Example directly below.
- Stored computed results - redisplay backtest and optimization results for a system without having to reprocess it.

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


## Deps

On top of the pip requirements, must have TA-Lib core (kind of a pain but use homebrew on Mac, tarball with python3.10-dev on Ubuntu, and the raw .whl file on Windows for v0.4.24). Firebase CLI is optional - website is automatically updated on git push as Firebase is configured with GitHub Actions.


As this read-me has no real info on commands and features yet, here are some example commands from regular usage.

```bash
wooster latest 

wooster process 1 --time --optimizer "Sharpe Ratio" --method grid --textalert --launch
wooster process 2 --no-optimize

wooster cache init aapl --interval 5m --lookbackyears 5
wooster cache delete aapl --interval 5m
wooster cache ls

wooster launch 1 stats
wooster launch 1 plot --label chop
```

[![plot-preview](readme-content/plot_preview.PNG)](https://wooster.preritdas.com/plots/Wooster%20One.html)
