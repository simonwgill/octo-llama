import os

parentdir = os.path.dirname(os.path.abspath(__file__))
os.sys.path.insert(0,parentdir)

from llama.pika_client import *
publisher = PikaPublisher("demonstration")

from listening_llama.listener import Listener
listener = Listener(publisher, "trends", "1")
listener.begin_wait_loop()
