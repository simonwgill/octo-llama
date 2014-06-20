import pickle
import random
import uuid
from llama.llama import Llama
from pycassa.pool import ConnectionPool
from pycassa.columnfamily import ColumnFamily
from pycassa.index import *
from pycassa.cassandra import ttypes
from datetime import datetime

from twython import Twython, exceptions

TWITTER_API_KEY = "emuanjY83cDBsPbXSSTu2qgU6"
TWITTER_API_SECRET = "zKBCdu7F5Pb8qrWuMPJfEfZ6GK2PbetydA2UdEII0Qt51aIJzz"
ACCESS_TOKEN = "260543066-jtV6jrii3KBXeWODha4agymIIYzlHPnLNPqnI11M"
ACCESS_TOKEN_SECRET = "EF3VWX7NOA8iJuJMFm8eQ0W7TdDYR4bKyP0fDBL89kxDc"

class Listener(Llama):
    def __init__(self, client, qname, woeid):
        super(Listener, self).__init__(client, qname)
        self.woeid = woeid
        self.time_format = "%a, %d %b %Y %H:%M:%S +0000"
        self.twitter = Twython(TWITTER_API_KEY, TWITTER_API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    def get_sleep_time(self):
        #10 minute refresh time with a random 10 second swing in either direction
        return 10*60 + random.randint(-10, 10)

    def save_trend(self, as_of, name, query):
        print "In WOEID %s at %s, %s was trending." % (self.woeid, as_of, name)

    def do_action(self):
        try:
          trends = self.twitter.get_place_trends(id=self.woeid)[0]
          as_of = datetime.strptime(trends['as_of'], "%Y-%m-%dT%H:%M:%SZ")
          for trend in trends['trends']:
            self.save_trend(as_of, trend['name'], trend['query'])
            self.publish((self.woeid, as_of, trend['name'], trend['query']))
        except exceptions.TwythonRateLimitError:
            print "Rate limit reached. Will retry later."
