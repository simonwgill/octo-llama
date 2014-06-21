import time
import pickle
import threading
import base64
import traceback
import logging
import datetime

DEFAULT_SLEEP_TIME = 0.5

class Llama(object):
  def __init__(self, client, queuename):
    self.client = client
    self.queuename = queuename

  def handle_pika_delivery(self, channel, method, header, body):
    self.handle(channel, method.delivery_tag, body)

  def handle(self, channel, delivery_tag, body):
    try:
      message = pickle.loads(body)
      if (message[0] == self.queuename):
        self.do_message(message[1])
      logging.debug("Ack of delivery_tag %s" % delivery_tag)
      channel.basic_ack(delivery_tag = delivery_tag)
    except:
      logging.warning("Rejecting message with delivery_tag %s due to exception:\n %s" % (delivery_tag, traceback.format_exc()))
      channel.basic_reject(delivery_tag = delivery_tag, requeue=False)

  def monitor(self):
    self.monitorthread = threading.Thread(target=self.client.monitor, args=(self.queuename, self.handle_pika_delivery))
    self.monitorthread.daemon = True
    self.monitorthread.start()

  def publish(self, message, queuename=None):
    if queuename is None:
      queuename = self.queuename
    body = pickle.dumps((queuename, message), 2)
    self.client.publish(body, routing_key=queuename)

  def get_sleep_time(self):
    return DEFAULT_SLEEP_TIME

  def begin_wait_loop(self):
    while True:
      self.do_action()
      self.delay(self.get_sleep_time())

  def delay(self, timing):
    period = datetime.timedelta(seconds = timing)
    end = datetime.datetime.now() + period
    while datetime.datetime.now() < end:
      time.sleep(0.5)
      
  def do_action(self):
    pass

  def do_message(self, message):
    pass
