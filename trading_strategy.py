import logging
import pandas as pd
from binance import AsyncClient
from retrying import retry

logger = logging.getLogger()

class TradingStrategy:
    def __init__(self, client, fast_ema, slow_ema,logger):
        self.client = client
        self.fast_ema = fast_ema
        self.slow_ema = slow_ema
        self.logger = logger

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
        try:
            order = await self.client.futures_create_order(symbol=symbol, side=side, type='MARKET', quantity=quantity)
            return order
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            return None