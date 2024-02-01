## Trading Bot Readme

This readme provides an overview of a trading bot that trades BTCUSDT based on the exponential moving average (EMA) crossover strategy.

### Strategy

The bot uses the following parameters for the EMA crossover strategy:

- EMA 20: The bot considers a bullish signal when the price crosses above the 20-period EMA.
- EMA 200: The bot considers a bearish signal when the price crosses below the 200-period EMA.
- Candlestick Interval: The bot analyzes the price action on 5-minute candlesticks.

### Requirements

To run the trading bot, you need the following:

- Binance API credentials
- Python 3.7 or higher
- Required Python packages (specified in the `requirements.txt` file)

### Usage

1. Clone the repository: `git clone https://github.com/your-username/trading-bot.git`
2. Install the required packages: `pip install -r requirements.txt`
3. Set up your Binance API credentials in the `.env` file. , edit the `.env.test`
4. Run the bot: `python bot.py`

### Disclaimer

Please note that trading cryptocurrencies involves risks, and this bot is provided for educational purposes only. Use it at your own risk.

For more information, refer to the full documentation in the [README.md](/Users/sly/trading/binance_ema/README.md) file.
