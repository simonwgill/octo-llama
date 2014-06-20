#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pickle
import random
import uuid
from llama.llama import Llama
from pycassa.pool import ConnectionPool
from pycassa.columnfamily import ColumnFamily
from pycassa.index import *
from pycassa.cassandra import ttypes
from datetime import datetime

class Listener(Llama):
    def __init__(self, client, qname, woeid):
        super(Listener, self).__init__(client, qname)
        self.woeid = woeid

    def get_sleep_time(self):
        return 20

    def do_action(self):
      self.publish((self.woeid, datetime.now(), 'Engländer', ''))
