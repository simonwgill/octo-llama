from pycassa.pool import ConnectionPool
from pycassa.columnfamily import ColumnFamily
from pycassa.index import *
from pycassa.cassandra import ttypes
import json
import datetime


class JSONDateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        else:
            return json.JSONEncoder.default(self, obj)



def has_many_woeids(x):
  key, values = x
  return len(values) > 1

pool = ConnectionPool('processing_llama_Processor')
trends = ColumnFamily(pool, 'Trend')

for trend_name, country_specifics in filter(has_many_woeids, trends.get_range()):
  print json.dumps(country_specifics, sort_keys=True, indent=4, separators=(',', ': '), cls=JSONDateTimeEncoder)
  #track_trend(trend_name, country_specifics['query'], country_specifics.keys)
