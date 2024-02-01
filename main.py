import os
import time
import logging
import pandas as pd
import pandas_ta as ta
from binance import AsyncClient
from dotenv import load_dotenv
from retrying import retry
import asyncio
# Load the environment variables from the .env file
load_dotenv()

# Set up logging
logging.basicConfig(filename='trade.log', filemode='w', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

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

class TradingStrategy:
    def __init__(self, client, fast_ema, slow_ema):
        self.client = client
        self.fast_ema = fast_ema
        self.slow_ema = slow_ema

    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    async def get_historical_data(self, symbol, interval, lookback):
        """Fetch historical data from Binance."""
        frame = pd.DataFrame(await self.client.get_historical_klines(symbol, interval, lookback + ' day ago UTC'))
        if frame.empty:
            logger.error("No data returned from Binance API")
            return pd.DataFrame()
        frame = frame.iloc[:, :6]
        frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        frame = frame.set_index('Time')
        frame.index = pd.to_datetime(frame.index, unit='ms')
        frame = frame.astype(float)
        return frame

    def implement_strategy(self, data):
        """Implement the EMA crossover strategy."""
        if data.empty:
            logger.error("Data frame is empty")
            return False, False
        data.ta.ema(close='Close', length=self.fast_ema, append=True)
        data.ta.ema(close='Close', length=self.slow_ema, append=True)
        data['Buy_Signal'] = (data['EMA_20'] > data['EMA_200'])
        data['Sell_Signal'] = (data['EMA_20'] < data['EMA_200'])
        return data['Buy_Signal'].iloc[-1], data['Sell_Signal'].iloc[-1]

    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    async def place_order(self, side, symbol, quantity):
        """Place an order on Binance."""
        order = await self.client.futures_create_order(symbol=symbol, side=side, type=MARKET, quantity=quantity)
        return order

async def main():
    strategy = TradingStrategy(client, FAST_EMA, SLOW_EMA)
    while True:
        start_time = time.time()
        data = await strategy.get_historical_data(SYMBOL, TIME_FRAME, '1')
        buy_signal, sell_signal = strategy.implement_strategy(data)
        if buy_signal:
            logger.info('Buy signal detected')
            order = await strategy.place_order(BUY, SYMBOL, QUANTITY)
            if order:
                logger.info(f"Buy order placed: {order}")
        elif sell_signal:
            logger.info('Sell signal detected')
            order = await strategy.place_order(SELL, SYMBOL, QUANTITY)
            if order:
                logger.info(f"Sell order placed: {order}")
        await asyncio.sleep(max(0, SLEEP_INTERVAL - (time.time() - start_time)))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())