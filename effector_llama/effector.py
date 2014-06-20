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

class Effector(Llama):
    def __init__(self, client, qname, address):
        super(Effector, self).__init__(client, uuid.uuid4().hex)
        self.address = address

    def do_message(self, message):
      trend_name, query, woeids = message
      print "You should look into %s as it is showing up in %s countries" % (trend_name, str(woeids))
