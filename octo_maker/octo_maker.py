
import proc_man
import comms
import time

class OctoMaker(object):
	def __init__(self):
		self.processes = proc_man.ProcessManager()
		self.comms = comms.Communications()
		self.minimum_cluster_size = 4
		self.cluster_size_reached = False
		self.master = False
		
		self.heartbeat_count = 0
		
		self.processes.on_proc_died = self.on_process_died
		self.processes.on_proc_heartbeat = self.on_process_local_heartbeat
		self.comms.on_proc_delegation = self.on_process_delegation
		self.comms.on_proc_heartbeat = self.on_process_remote_heartbeat
		self.comms.on_cluster_size_estimate = self.on_cluster_size_estimate
		self.comms.on_master_status_changed = self.on_master_status_changed
	
	def on_process_died(self, process_id):
		print "[octo-maker] process %s died" % process_id
		self.comms.broadcast_process_death(process_id)
	
	def on_process_local_heartbeat(self, process_ids):
		self.heartbeat_count += 1
		#print "[octo-maker] heartbeat", self.heartbeat_count
		#print "[octo-maker] local '%s' processes: %s" % (self.comms.queue_name[-6:], process_ids)
		self.comms.broadcast_process_heartbeat(process_ids)
	
	def on_process_delegation(self, source, process_id):
		print "[octo-maker] received delegation request for process %s" % process_id
		return self.processes.receive_process_delegation(process_id)
	
	def on_process_remote_heartbeat(self, source, process_ids):
		#print "[octo-maker] node '%s' processes: %s" % (source[-6:], process_ids)
		self.processes.process_remote_heartbeat(process_ids)
	
	def on_cluster_size_estimate(self, size):
		print "[octo-maker] estimated cluster size changed: %s" % size
		#if size >= self.minimum_cluster_size and not self.cluster_size_reached:
		#	self.cluster_size_reached = True
		#	self.comms.claim_master()
		if self.master:
			self.comms.send_control_message('all', 'became-master')
	
	def on_master_status_changed(self, is_master):
		print "[octo-maker] master status: %s" % is_master
		self.master = is_master
		self.processes.allow_process_spawning = self.master
	
	def start(self):
		self.comms.start_async()
		#time.sleep(2.0)
		self.processes.mainloop()
