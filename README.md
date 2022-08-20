# Wooster Systems

## Main features

- Predesigned proprietary Wooster trading strategies, most of which are ML-powered. Continually modifying and iterating on them.
- Comprehensive feature-packed CLI capable of independently handling all of the following features.
- Automatic backtesting of strategy against historical data.
- Automatic multi-core optimization of strategy parameters on historical data, with the ability to change the optimized statistic (i.e. SQN, Sharpe Ratio, Return, etc.).
- Automatic backtesting of optimized strategy on out-of-sample uptrend, downtrend, and choppy market data, to combat overfitting and to see a strategy's true performance on new, un-optimized data. Walkforward principle, applied intentionally to various market conditions.
- Automatically formats above results (from all conditions) into beautiful HTML files, which automatically update on the [Wooster website](https://wooster.preritdas.com) on git push.
- Automatically generates sharp interactive plots of above results, also automatically updated on the [Wooster website](https://wooster.preritdas.com) on git push.
- [Wooster website](https://wooster.preritdas.com) written in HTML and JavaScript with smart lookup - query strategy statistics or specific performance plots from the homepage.
- Data cache - initialize, view, and manage a local cache data repository to speed up data aggregation in the processing phase. This is because when tuning and reproceessing a strategy, the walkforward data windows are often the same, so it doesn't make sense to (a) use up a data rate limit or (b) wait for the same data to re-load (which often takes time, especially when loading many years of intraday data for testing and optimization). An example: `wooster cache init aapl --interval 1m --lookbackyears 10` to store 10 years of minute bar data on AAPL, automatically used whenever any program feature tries to access 1m AAPL data within the last 10 years.

### Smaller features

- No-loss incremental aggregation of market data to comply with freemium data provider restrictions and rate limits.
- `--textalert` option in `process` command to receive a text message once processing has completed. When a strategy has several parameters with wide ranges, optimization can take a _very_ long time, as optimization tests the product of all parameter configurations. `--textalert` adds convenience to server-side deployment. Note that even the _setup_ for this feature is completely optional - if no Nexmo API keys are provided, no features are broken, and the flag simply has no action, except for a nonintrusive warning message.
- Optionally change not just the optimized statistic, but the optimization method itself - grid optimization of minimal forest optimization with scikit. If grid optimization (default) is used on most Mac/Darwin/Linux machines, optimization will make use of multiple cores, completing operations several times faster than otherwise.
- Defaults configuration through [config.ini](config.ini) - modify preferred metrics, highlighted metrics, default optimizer, etc.
- Status handling across modules and submodules, because processing (aggregating potentially years of non-cached data, backtesting, optimizing, re-backtesting on out-of-sample market conditions) can often take a little while. Rich status icons and progress bars keep track of where the program is (and how far along) at almost all times. This includes estimated remaining time! When optimizing many parameters on heavy data, you'll see a progress bar with an estimated time to completion.


## Deps

On top of the pip requirements, must have TA-Lib core (kind of a pain) and pretty soon firebase CLI for serving and deploying the interactive result plots.


As the read-me has no real info on commands and features, the following are some example commands run throughout regular usage.

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
