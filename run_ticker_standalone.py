########################################
# To run this demo using py-amqplib, 
# uncomment this block, and  comment out
# the next block.
########################################

#from amqplib_client import *
#publisher = PyAmqpLibPublisher(exchange_name="my_exchange")

########################################
# To run this demo using pika,
# uncomment this block, and comment out
# the previous block
########################################

from pika_client import *
publisher = PikaPublisher(exchange_name="my_exchange")

########################################
# This part doesn't have to change
########################################

from ticker_system import *
ticker = Ticker(publisher, "")
ticker.monitor()

