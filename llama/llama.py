import time
import pickle
import threading
import base64

DEFAULT_SLEEP_TIME = 0.5

class Llama(object):
  def __init__(self, client, queuename):
    self.client = client
    self.queuename = queuename

  def handle_pika_delivery(self, channel, method, header, body):
    self.handle(channel, method.delivery_tag, body)

  def handle(self, channel, delivery_tag, body):
    message = pickle.loads(base64.b64decode(body))
    channel.basic_ack(delivery_tag = delivery_tag)
    self.do_message(message)

  def monitor(self):
    self.monitorthread = threading.Thread(target=self.client.monitor, args=(self.queuename, self.handle_pika_delivery))
    self.monitorthread.start()

  def publish(self, message, queuename=None):
    if queuename is None:
      queuename = self.queuename
    body = pickle.dumps(message, 2)
    self.client.publish(body, routing_key=queuename)

  def get_sleep_time(self):
    return DEFAULT_SLEEP_TIME

  def begin_wait_loop(self):
    while True:
      self.do_action()
      time.sleep(self.get_sleep_time())
      
  def do_action(self):
    pass

  def do_message(self, message):
    pass
