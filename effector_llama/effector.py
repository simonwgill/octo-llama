import pickle
import random
import uuid
from llama.llama import Llama
from pycassa.pool import ConnectionPool
from pycassa.columnfamily import ColumnFamily
from pycassa.index import *
from pycassa.cassandra import ttypes
import datetime
import smtplib
import logging

class Effector(Llama):
    def __init__(self, client, qname, address):
        super(Effector, self).__init__(client, qname)
        self.address = address

    def do_message(self, message):
      trend_name, query, woeids = message

      sender = 'simonwgill@gmail.com'
      receivers = [self.address]

      message = """From: Simon Gill <simonwgill@gmail.com>
To: Simon Gill <simonwgill@gmail.com>
Subject: %s is Trending for %s

You should check out twitter using the api query string %s
""" % (trend_name, str(woeids), query)

      try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(sender, receivers, message)         
        logging.info("Successfully sent email")
      except smtplib.SMTPException:
        logging.error("Unable to send email", traceback.format_exc())
