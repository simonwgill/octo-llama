import os
import logging
parentdir = os.path.dirname(os.path.abspath(__file__))
os.sys.path.insert(0,parentdir)

logging.basicConfig(format='%(levelname)s:%(message)s',level=logging.DEBUG)


from llama.pika_client import *
publisher = PikaPublisher("demonstration")

from listening_llama.listener import Listener
listener = Listener(publisher, "trends", "23424819")
listener.begin_wait_loop()
