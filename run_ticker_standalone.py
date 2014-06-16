import os

parentdir = os.path.dirname(os.path.abspath(__file__))
os.sys.path.insert(0,parentdir)

from llama.pika_client import *
publisher = PikaPublisher("stock-ticker")

from example_producer.ticker_system import Ticker
ticker = Ticker(publisher, "")
ticker.begin_wait_loop()
