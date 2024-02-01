from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import os 

api_key = os.environ.get('API_KEY')
api_secret = os.environ.get('API_SECRET')

client = Client(api_key, api_secret)
