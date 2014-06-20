import os

parentdir = os.path.dirname(os.path.abspath(__file__))
os.sys.path.insert(0,parentdir)

from llama.pika_client import *
publisher = PikaPublisher("stock-ticker")

from example_consumer.buy_low_sell_high import Buyer
buyer = Buyer(publisher, "", trend=25)
print "Buyer = %s" % id(buyer)
buyer.monitor()
buyer.begin_wait_loop()
