import os
import time
import logging
import pandas as pd
import pandas_ta as ta
from binance import AsyncClient
from dotenv import load_dotenv
from retrying import retry
import asyncio
from trading_strategy import TradingStrategy
from paper_trading import PaperTrading

# Load the environment variables from the .env file
load_dotenv()

# Set up logging
logging.basicConfig(filename='trade.log', filemode='w', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('main')

# Define your Binance API credentials
api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')

# Check if the API credentials are set
if not api_key or not api_secret:
    logger.error("API credentials are not set")
    exit(1)

# Define your trading parameters
TIME_FRAME = os.getenv('TIME_FRAME', '5m')
FAST_EMA = int(os.getenv('FAST_EMA', 20))
SLOW_EMA = int(os.getenv('SLOW_EMA', 200))
SYMBOL = os.getenv('SYMBOL', 'BTCUSDT')
QUANTITY = float(os.getenv('QUANTITY', 0.001))
SLEEP_INTERVAL = int(os.getenv('SLEEP_INTERVAL', 60))

# Define constants
BUY = 'BUY'
SELL = 'SELL'
MARKET = 'MARKET'

client = AsyncClient(api_key, api_secret)

# Initialize paper trading with $1000
paper_trading = PaperTrading(1000)

async def main():
    strategy = TradingStrategy(client, FAST_EMA, SLOW_EMA,logger)
    while True:
        start_time = time.time()
        try:
            data = await strategy.get_historical_data(SYMBOL, TIME_FRAME, '1')
        except Exception as e:
            logger.error(f"Failed to fetch historical data: {e}")
            continue
        buy_signal, sell_signal = strategy.implement_strategy(data)
        current_price = data['Close'].iloc[-1]
        if buy_signal:
            logger.info('Buy signal detected')
            order = await strategy.place_order(BUY, SYMBOL, QUANTITY)
            paper_order = paper_trading.place_order(BUY, SYMBOL, QUANTITY, current_price)
            if order and paper_order:
                logger.info(f"Buy order placed: {order}")
                logger.info(f"Paper trade: Buy order placed")
        elif sell_signal:
            logger.info('Sell signal detected')
            order = await strategy.place_order(SELL, SYMBOL, QUANTITY)
            paper_order = paper_trading.place_order(SELL, SYMBOL, QUANTITY, current_price)
            if order and paper_order:
                logger.info(f"Sell order placed: {order}")
                logger.info(f"Paper trade: Sell order placed")
        profit = paper_trading.calculate_profit(current_price)
        logger.info(f"Paper trade: Current profit: {profit}")
        await asyncio.sleep(max(0, SLEEP_INTERVAL - (time.time() - start_time)))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())