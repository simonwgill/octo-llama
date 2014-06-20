import pickle
import random
import uuid
from llama.llama import Llama
from pycassa.pool import ConnectionPool
from pycassa.columnfamily import ColumnFamily
from pycassa.index import *
from pycassa.cassandra import ttypes
import datetime
import sys
import traceback

class Processor(Llama):
    def __init__(self, client, qname):
        super(Processor, self).__init__(client, qname)
        self.pool = ConnectionPool('processing_llama_Processor')
        self.trends = ColumnFamily(self.pool, 'Trend')

	def get_sleep_time():
		return 60

    def do_message(self, message):
        if not isinstance(message, tuple) or len(message) != 4:
			return
        woeid, as_of, trend_name, query = message
        try:
          trend = self.trends.get(trend_name, super_column=woeid)
          trend['lastseen'] = as_of
          trend['number_seen'] += 1
          trend = { woeid: trend }
          self.trends.insert(trend_name, trend)
        except ttypes.NotFoundException:
		  self.trends.insert(trend_name, { woeid: { 'firstseen': as_of, 'lastseen': as_of, 'number_seen': 1}})
		  self.trends.insert(trend_name, {'data': { 'query': query, 'tracking': "False" }})

    def has_many_woeids(self, x):
        key, values = x
        return len(values) > 2 # one woeid plus general data

    def do_action(self):
      try:
        for trend_name, country_specifics in filter(self.has_many_woeids, self.trends.get_range()):
          if country_specifics['data']['tracking'] == "False":
            self.track_trend(trend_name, country_specifics['data']['query'], filter(lambda x: x != "data", country_specifics.keys()))
      except:
		exc, value, exctraceback = sys.exc_info()
		print "Error in processing_llama.processor.Processor.do_action: ", exc, value
		traceback.print_tb(exctraceback)
        
    def track_trend(self, trend_name, query, woeids):
      print "Tracking %s from %s" % (trend_name, woeids)
      self.mark_tracking(trend_name)
      self.publish((trend_name, query, woeids), "trend_to_track")

    def mark_tracking(self, trend_name):
      try:
          trend = self.trends.get(trend_name, super_column='data')
          trend['tracking'] = "True"
          self.trends.insert(trend_name, { 'data': trend })
      except ttypes.NotFoundException:
          pass
