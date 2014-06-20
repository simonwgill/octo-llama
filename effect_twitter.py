import os

parentdir = os.path.dirname(os.path.abspath(__file__))
os.sys.path.insert(0,parentdir)

from llama.pika_client import *
publisher = PikaPublisher("demonstration")

from effector_llama.effector import Effector
effector = Effector(publisher, "trend_to_track", "example@email.local")
effector.monitor()
