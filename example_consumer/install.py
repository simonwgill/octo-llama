from pycassa.system_manager import *

sys = SystemManager()
sys.create_keyspace('example_consumer_Buyer', SIMPLE_STRATEGY, { 'replication_factor': '3' })
sys.create_column_family('example_consumer_Buyer', 'Holdings')
sys.create_column_family('example_consumer_Buyer', 'Quotes')
sys.create_column_family('example_consumer_Buyer', 'Cash')
sys.alter_column('example_consumer_Buyer', 'Holdings', 'number_of_shares', INT_TYPE)
sys.alter_column('example_consumer_Buyer', 'Holdings', 'price', FLOAT_TYPE)
sys.alter_column('example_consumer_Buyer', 'Holdings', 'cost', FLOAT_TYPE)
sys.alter_column('example_consumer_Buyer', 'Quotes', 'timestamp', DATE_TYPE)
sys.alter_column('example_consumer_Buyer', 'Quotes', 'price', FLOAT_TYPE)
sys.alter_column('example_consumer_Buyer', 'Cash', 'amount', FLOAT_TYPE)
