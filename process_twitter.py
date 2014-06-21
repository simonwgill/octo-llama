import os
import logging
parentdir = os.path.dirname(os.path.abspath(__file__))
os.sys.path.insert(0,parentdir)

logging.basicConfig(format='%(levelname)s:%(message)s',level=logging.DEBUG)

from llama.pika_client import *
publisher = PikaPublisher("demonstration")

from processing_llama.processor import Processor
processor = Processor(publisher, "trends")
processor.monitor()
processor.begin_wait_loop()
