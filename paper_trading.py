
import logging

logger = logging.getLogger('main')

class PaperTrading:
    def __init__(self, balance):
        self.balance = balance
        self.asset_balance = 0

    def place_order(self, side, symbol, quantity, price):
        if side == 'BUY':
            if self.balance < quantity * price:
                logger.error("Insufficient balance for the paper trade")
                return False
            self.balance -= quantity * price
            self.asset_balance += quantity
            logger.info(f"Paper trade: Buy order placed: {quantity} {symbol} at {price}")
        elif side == 'SELL':
            if self.asset_balance < quantity:
                logger.error("Insufficient asset balance for the paper trade")
                return False
            self.balance += quantity * price
            self.asset_balance -= quantity
            logger.info(f"Paper trade: Sell order placed: {quantity} {symbol} at {price}")
        logger.info(f"Paper trade: Current balance: {self.balance}, Current asset balance: {self.asset_balance}")
        return True

    def calculate_profit(self, current_price):
        return self.asset_balance * current_price - self.balance