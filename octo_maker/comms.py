
import threading
import datetime
import cPickle
import pika

from utils import TimePoint

class TaskDelegationMessage(object):
	def __init__(self, parent_uuid, process_id):
		self.parent_uuid = parent_uuid
		self.process_id = process_id

class ProcessHeartbeatMessage(object):
	def __init__(self, parent_uuid, process_ids):
		self.parent_uuid = parent_uuid
		self.process_ids = process_ids

class ControlMessage(object):
	def __init__(self, parent_uuid, command, values):
		self.parent_uuid = parent_uuid
		self.command = command
		self.values = values

class KnownNode(object):
	def __init__(self, parent_uuid, process_ids):
		self.parent_uuid = parent_uuid
		self.process_ids = process_ids
		self.is_master = False
		self.last_contact = TimePoint()

class Communications(object):
	def __init__(self):
		self.on_proc_delegation = lambda x, y: False
		self.on_proc_heartbeat = lambda x, y: None
		self.on_cluster_size_estimate = lambda x: None
		self.thread = None
		
		self.claimed_master = False
		self.claim_ack_count = 0
		self.was_master = False
		self.master_claim_seconds = 60.0
		self.master_claim_period = datetime.timedelta(seconds = self.master_claim_seconds)
		self.master_claim_timeout = datetime.datetime.now()
		
		self.connection = None
		self.channel = None
		self.queue_name = None
		
		self.control_queue_name = None
		
		self.known_nodes = {}
		self.last_cluster_size_estimate = 1
		
		self.node_timeout = 60.0
	
	def reset_master_claim(self):
		self.claimed_master = False
		self.claim_ack_count = 0
	
	def set_master(self, parent_uuid):
		for host in self.known_nodes.values():
			host.is_master = (host.parent_uuid == parent_uuid)
	
	def estimate_cluster_size(self):
		count = 0
		
		for host in self.known_nodes.values():
			if host.last_contact.elapsed_seconds() < self.node_timeout:
				count += 1
		
		return count
	
	def broadcast_process_death(self, process_id):
		#print "[octo-maker:comms] broadcasting proc death:", process_id
		message = TaskDelegationMessage(self.queue_name, process_id)
		self.broadcast('octo-maker.task-queue', message, True)
	
	def broadcast_process_heartbeat(self, process_ids):
		#print "[octo-maker:comms] broadcasting proc heartbeat:", process_ids
		message = ProcessHeartbeatMessage(self.queue_name, process_ids)
		self.broadcast_via_exchange(
			'octo-maker.process-heartbeat', '', message, False
		)
	
	def claim_master(self):
		self.claimed_master = True
		self.claim_ack_count = 0
		self.send_control_message('all', 'claim-master')
	
	def send_control_message(self, target, command, values = {}):
		self.broadcast_via_exchange(
			'octo-maker.control',
			'octo-maker.node.%s' % target,
			ControlMessage(self.queue_name, command, values),
			True
		)
	
	def broadcast(self, queue, message, persistent):
		self.broadcast_via_exchange('', queue, message, persistent)
	
	def broadcast_via_exchange(self, exchange, queue, message, persistent):
		delivery_mode = None
		if persistent:
			delivery_mode = 2
		
		self.channel.basic_publish(
			exchange = exchange,
			routing_key = queue,
			body = cPickle.dumps(message, cPickle.HIGHEST_PROTOCOL),
			properties = pika.BasicProperties(
				delivery_mode = delivery_mode
			)
		)
	
	def update_known_host(self, parent_uuid, processes = []):
		if parent_uuid not in self.known_nodes.keys():
			self.known_nodes[parent_uuid] = KnownNode(parent_uuid, processes)
		else:
			self.known_nodes[parent_uuid].last_contact.reset()
		
		cluster_size = self.estimate_cluster_size()
		if cluster_size != self.last_cluster_size_estimate:
			self.on_cluster_size_estimate(cluster_size)
			self.last_cluster_size_estimate = cluster_size
	
	def handle_task_delegation(self, channel, method, properties, body):
		message = cPickle.loads(body)
		
		self.update_known_host(message.parent_uuid)
		
		accepted = self.on_proc_delegation(message.parent_uuid, message.process_id)
		
		if accepted:
			print "[octo-maker:comms] accepted task"
			self.channel.basic_ack(method.delivery_tag)
		else:
			print "[octo-maker:comms] rejected task"
			self.channel.basic_nack(method.delivery_tag)
		
	def handle_process_heartbeat(self, channel, method, properties, body):
		message = cPickle.loads(body)
		
		self.update_known_host(message.parent_uuid, message.process_ids)
		
		if message.parent_uuid == self.queue_name:
			#print "[octo-maker:comms] ignoring heartbeat echo"
			self.channel.basic_ack(method.delivery_tag)
		else:
			self.on_proc_heartbeat(message.parent_uuid, message.process_ids)
			self.channel.basic_ack(method.delivery_tag)
	
	def handle_control_message(self, channel, method, properties, body):
		message = cPickle.loads(body)
		
		self.update_known_host(message.parent_uuid)
		
		if message.command == 'claim-master':
			if datetime.datetime.now() >= self.master_claim_timeout:
				self.master_claim_timeout += self.master_claim_period
				
				self.send_control_message(message.parent_uuid, 'ack-claim')
		elif message.command == 'ack-claim':
			if self.claimed_master:
				self.claim_ack_count += 1
				if self.claim_ack_count >= (self.estimate_cluster_size() * 0.5):
					self.send_control_message('all', 'became-master')
		elif message.command == 'became-master':
			self.reset_master_claim()
			self.set_master(message.parent_uuid)
			is_master = message.parent_uuid == self.queue_name
			if is_master is not self.was_master:
				self.on_master_status_changed(is_master)
				self.was_master = is_master
		
		self.channel.basic_ack(method.delivery_tag)
	
	def start_async(self):
		self.thread = threading.Thread(target = self.mainloop)
		self.thread.setDaemon(True)
		self.thread.start()
	
	def mainloop(self):
		self.connection = pika.AsyncoreConnection(pika.ConnectionParameters(
			'localhost',
			credentials = pika.PlainCredentials('guest', 'guest')
		))
		self.channel = self.connection.channel()
		
		self.channel.exchange_declare(
			exchange = 'octo-maker.process-heartbeat',
			type = 'fanout'
		)
		
		self.channel.exchange_declare(
			exchange = 'octo-maker.control',
			type = 'topic'
		)
		
		result = self.channel.queue_declare(exclusive=True)
		self.queue_name = result.queue
		print "[octo-maker:comms] started as queue '%s'" % self.queue_name
		self.channel.queue_bind(
			exchange = 'octo-maker.process-heartbeat',
			queue = self.queue_name
		)
		
		result = self.channel.queue_declare(exclusive=True)
		self.control_queue_name = result.queue
		bindings = ['octo-maker.node.all', 'octo-maker.node.%s' % self.queue_name]
		for binding in bindings:
			self.channel.queue_bind(
				exchange = 'octo-maker.control',
				queue = self.control_queue_name,
				routing_key = binding
			)
		
		self.channel.queue_declare(
			queue = 'octo-maker.task-queue',
			durable = True
		)
		
		self.channel.basic_qos(prefetch_count = 1)
		
		self.channel.basic_consume(
			self.handle_task_delegation,
			queue = 'octo-maker.task-queue'
		)
		
		self.channel.basic_consume(
			self.handle_process_heartbeat,
			queue = self.queue_name
		)
		
		self.channel.basic_consume(
			self.handle_control_message,
			queue = self.control_queue_name
		)
		
		pika.asyncore_loop()
