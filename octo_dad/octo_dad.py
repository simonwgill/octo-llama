
import BaseHTTPServer
import threading
import datetime
import cPickle
import pika
import json

class ProcessHeartbeatMessage(object):
	def __init__(self, parent_uuid, process_ids):
		self.parent_uuid = parent_uuid
		self.process_ids = process_ids

class ControlMessage(object):
	def __init__(self, parent_uuid, command, values):
		self.parent_uuid = parent_uuid
		self.command = command
		self.values = values

class WebException(Exception):
	def __init__(self, code, message):
		self.code = code
		self.message = message
		
class Response(object):
	def __init__(self, contents, content_type):
		self.contents = contents
		self.content_type = content_type
	
	def length(self):
		return len(self.contents)

class OctoDadHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			contents = self.generate_contents()			
			self.send_response(200)
			self.send_header("Content-type", contents.content_type)
			self.send_header("Content-Length", contents.length())
			self.end_headers()
			self.wfile.write(contents.contents)
		except WebException as exception:
			self.send_error(exception.code, exception.message)
		except Exception as exception:
			self.send_error(500, "Something broke inside:\r\n%s" % str(exception))
	
	def generate_contents(self):
		if self.path == '/':
			self.path = '/index.html'
		if self.path in self.server.whitelist:
			content_type = "text/plain"
			
			extension = "html"
			if self.path.rfind(".") != -1:
				extension = self.path[self.path.rfind(".")+1:]
			
			if extension == "html":
				content_type = "text/html"
			elif extension == "css":
				content_type = "text/css"
			elif extension == "js":
				content_type = "application/javascript"
			
			return Response(self.grab_file(self.path), content_type)
		elif self.path.endswith(".json"):
			return Response(self.make_json(), 'application/json')
		else:
			print "[octo-dad] not in whitelist:", self.path
			raise WebException(404, "File not Found")
	
	def grab_file(self, filepath):
		full_path = self.server.root_path + filepath
		try:
			f = open(full_path, 'rb')
			return f.read()
		except:
			raise WebException(404, "File not Found")
	
	def make_json(self):
		result = None
		
		if self.path in self.server.handlers.keys():
			result = self.server.handlers[self.path]()
		else:
			raise WebException(404, "File not Found")
		
		return json.dumps(result)

class KnownHost(object):
	def __init__(self, name, processes):
		self.name = name
		self.master = 'unknown'
		self.processes = processes
		self.last_contact = datetime.datetime.now()
		
	def heard_from(self, process_ids = None):
		self.last_contact = datetime.datetime.now()
		if process_ids is not None:
			self.processes = process_ids
	
	def time_since_heard(self):
		return (datetime.datetime.now() - self.last_contact)
	
	def seconds_since_contact(self):
		return self.time_since_heard().total_seconds()

class OctoDad(BaseHTTPServer.HTTPServer):
	def __init__(self, server_address):
		BaseHTTPServer.HTTPServer.__init__(self, server_address, OctoDadHandler)
		self.root_path = 'web'
		self.whitelist = [
			'/index.html',
			'/css/normalize.css',
			'/css/main.css',
			'/css/octo-dad.css',
			'/js/vendor/modernizr-2.6.2.min.js',
			'/js/plugins.js',
			'/js/main.js'
		]
		
		self.known_hosts = {}
		
		self.rmq_thread = threading.Thread(target = self.run_rabbit_interface)
		self.rmq_thread.setDaemon(True)
		self.rmq_thread.start()
		
		self.handlers = {
			'/api/octo-dad.json': self.json_octo_dad
		}
	
	def json_octo_dad(self):
		result = {}
		
		hosts = self.known_hosts
		
		cluster_info = {}
		for key in hosts.keys():
			node = hosts[key]
			
			node_info = {
				'name': node.name,
				'processes': node.processes,
				'master': node.master,
				'last_contact': str(node.last_contact),
				'last_contact_seconds': node.seconds_since_contact()
			}
			cluster_info[key] = node_info
		
		result["cluster_info"] = cluster_info
			
		return result
		
	def run_rabbit_interface(self):
		connection = pika.AsyncoreConnection(pika.ConnectionParameters(
			'localhost',
			credentials = pika.PlainCredentials('guest', 'guest')
		))
		channel = connection.channel()
		
		channel.exchange_declare(
			exchange = 'octo-maker.process-heartbeat',
			type = 'fanout'
		)
		
		result = channel.queue_declare(exclusive=True)
		queue_name = result.queue
		print "[octo-dad] listening as queue '%s'" % queue_name
		channel.queue_bind(
			exchange = 'octo-maker.process-heartbeat',
			queue = queue_name
		)
		
		result = channel.queue_declare(exclusive=True)
		control_queue_name = result.queue
		
		channel.queue_bind(
			exchange = 'octo-maker.control',
			queue = control_queue_name,
			routing_key = 'octo-maker.node.*'
		)
		
		channel.basic_consume(
			self.handle_process_heartbeat,
			queue = queue_name
		)
		
		channel.basic_consume(
			self.handle_control_message,
			queue = control_queue_name
		)
		
		pika.asyncore_loop()
	
	def update_hosts(self, parent_uuid, processes=None):
		if parent_uuid not in self.known_hosts.keys():
			if processes is None:
				processes = []
			self.known_hosts[parent_uuid] = KnownHost(parent_uuid, processes)
		else:
			self.known_hosts[parent_uuid].heard_from(processes)
			
		too_old = []
		for key in self.known_hosts.keys():
			node = self.known_hosts[key]
			if node.seconds_since_contact() >= 240:
				too_old.append(key)
		
		for key in too_old:
			del self.known_hosts[key]
	
	def handle_process_heartbeat(self, channel, method, properties, body):
		message = cPickle.loads(body)
		
		#print "[octo-dad] heartbeat:", message.parent_uuid, message.process_ids
		self.update_hosts(message.parent_uuid, message.process_ids)
	
	def handle_control_message(self, channel, method, properties, body):
		message = cPickle.loads(body)
		
		self.update_hosts(message.parent_uuid)
		
		if message.parent_uuid in self.known_hosts.keys():
			if message.command == 'claim-master':
				self.known_hosts[message.parent_uuid].master = 'negotiating'
			elif message.command == 'became-master':
				for key in self.known_hosts.keys():
					if key == message.parent_uuid:
						self.known_hosts[key].master = 'yes'
					else:
						self.known_hosts[key].master = 'no'
		
	@staticmethod
	def run(port):
		server_address = ('', port)
		httpd = OctoDad(server_address)
		httpd.serve_forever()
