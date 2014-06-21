import os
import logging
parentdir = os.path.dirname(os.path.abspath(__file__))
os.sys.path.insert(0,parentdir)

logging.basicConfig(format='EffectTwitter:%(levelname)s:%(message)s',level=logging.DEBUG)


from llama.pika_client import *
publisher = PikaPublisher("demonstration")

from effector_llama.effector import Effector
effector = Effector(publisher, "trend_to_track", "simonwgill@gmail.com")
effector.monitor()
effector.begin_wait_loop()
