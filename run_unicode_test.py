import os

parentdir = os.path.dirname(os.path.abspath(__file__))
os.sys.path.insert(0,parentdir)

from llama.pika_client import *
publisher = PikaPublisher("demonstration")

from unicode_publisher_test.tester import Listener
listener = Listener(publisher, "trends", "23424975")
listener.begin_wait_loop()
