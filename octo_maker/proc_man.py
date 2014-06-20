
import subprocess
import threading
import datetime
import shlex
import time

from utils import TimePoint

now = datetime.datetime.now

class LocalProcess(object):
	def __init__(self, our_pid, invocation):
		self.our_pid = our_pid
		self.os_pid = None
		self.retries = 0
		self.max_retries = 5
		
		self.process_handle = None
		self.invocation = invocation
	
	def invoke(self):
		print "[octo-maker:proc-man] invoking process: '%s'" % self.invocation
		parsed = shlex.split(self.invocation)
		try:
			self.process_handle = subprocess.Popen(parsed, stdout=subprocess.PIPE)
			self.os_pid = self.process_handle.pid
		except OSError, e:
			print "os error:", e
	
	def heartbeat(self):
		still_alive = True
		
		if not self.is_process_alive():
			self.os_pid = None
			if self.retries < self.max_retries:
				self.retries += 1
				self.invoke()
			else:
				still_alive = False
		
		return still_alive
	
	def is_process_alive(self):
		if self.process_handle is None:
			return False
			
		return (self.process_handle.poll() is None)

class ProcessManager(object):
	def __init__(self):
		self.on_proc_died = lambda x: None
		self.on_proc_heartbeat = lambda x: None
		self.thread = None
		
		self.heartbeats = {}
		
		self.heartbeat_seconds = 5.0
		self.timeout_seconds = self.heartbeat_seconds * 2
		self.warmup_seconds = self.heartbeat_seconds * 4
		
		self.heartbeat_period = datetime.timedelta(seconds = self.heartbeat_seconds)
		self.next_heartbeat = now() + self.heartbeat_period
		
		self.allow_process_spawning = False
		self.local_processes = []
		
		self.process_table = {}
		
		self.process_table = self.load_process_list('octo_maker/processes.conf')
		
		# create initial heartbeat entries for all known processes
		for pid in self.process_table.keys():
			self.update_heartbeat(pid)
	
	def has_process(self, pid):
		for process in self.local_processes:
			if process.our_pid == pid:
				return True
		return False
	
	def receive_process_delegation(self, process_id):
		# if we're already running it, return success, we're already responsible for it
		if self.has_process(process_id):
			return True
		
		process = LocalProcess(process_id, self.process_table[process_id])
		process.invoke()
		self.local_processes.append(process)
		self.update_heartbeat(process.our_pid)
		
		return True
	
	def process_remote_heartbeat(self, process_ids):
		for pid in process_ids:
			self.update_heartbeat(pid)
	
	def update_heartbeat(self, pid):
		#print "[octo-maker:proc-man] pid %s updated" % pid
		if pid not in self.heartbeats.keys():
			self.heartbeats[pid] = TimePoint()
		else:
			self.heartbeats[pid].reset()
	
	def start_async(self):
		self.thread = threading.Thread(target = self.mainloop)
		self.thread.setDaemon(True)
		self.thread.start()
	
	def load_process_list(self, filepath):
		handle = open(filepath, 'r')
		counter = 0
		
		result = {}
		
		print "[octo-maker:proc-man] loading process list:"
		for line in handle.readlines():
			line = line.strip()
			if not line: continue
			
			result[counter] = line
			print "\t%s: '%s'" % (counter, line)
			counter += 1
		
		return result
	
	def remove_local(self, pid):
		for process in self.local_processes:
			if process.our_pid == pid:
				self.local_processes.remove(process)
				break
	
	def produce_heartbeat(self):
		still_alive = []
		local_dead = []
		
		for process in self.local_processes:
			if process.heartbeat():
				self.update_heartbeat(process.our_pid)
				still_alive.append(process.our_pid)
			else:
				print "[octo-maker] local process %s died too many times" % process.our_pid
				local_dead.append(process.our_pid)
		
		for pid in local_dead:
			self.remove_local(pid)
		
		self.on_proc_heartbeat(still_alive)
	
	def update_taskings(self):
		if not self.allow_process_spawning:
			return
			
		died = []
		max_simultaneous = 10
		
		for pid in self.heartbeats.keys():
			elapsed = self.heartbeats[pid].elapsed_seconds()
			if elapsed >= self.timeout_seconds:
				died.append(pid)
				#print "[octo-maker:proc-man] process %s died, timeout: %s" % (pid, elapsed)
				if len(died) >= max_simultaneous:
					break
		
		for pid in died:
			self.on_proc_died(pid)
			self.heartbeats[pid].reset()
	
	def mainloop(self):
		while True:
			if now() < self.next_heartbeat:
				time.sleep(0.5)
				continue
			self.next_heartbeat = now() + self.heartbeat_period
			
			self.produce_heartbeat()
			self.update_taskings()
