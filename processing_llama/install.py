from pycassa.system_manager import *

keyspace = "processing_llama_Processor"

sys = SystemManager()
sys.create_keyspace(keyspace, SIMPLE_STRATEGY, { 'replication_factor': '3' })
sys.create_column_family(keyspace, 'Trend', super=True)
sys.alter_column(keyspace, 'Trend', 'firstseen', DATE_TYPE)
sys.alter_column(keyspace, 'Trend', 'lastseen', DATE_TYPE)
sys.alter_column(keyspace, 'Trend', 'number_seen', INT_TYPE)
