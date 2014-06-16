import time
import pickle

DEFAULT_SLEEP_TIME = 0.5

class Llama(object):
  def __init__(self, client, queuename):
    self.client = client
    self.queuename = queuename

  def handle_pika_delivery(self, channel, method, header, body):
    self.handle(channel, method.delivery_tag, body)

  def handle(self, channel, delivery_tag, body):
    message = pickle.loads(body)
    channel.basic_ack(delivery_tag = delivery_tag)
    self.do_message(message)

  def monitor(self):
    self.client.monitor(self.queuename, self.handle_pika_delivery)

  def publish(self, message):
    self.client.publish(pickle.dumps(message), routing_key="")

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
