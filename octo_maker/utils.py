
import datetime

now = datetime.datetime.now

class TimePoint(object):
	def __init__(self, point=now()):
		self.point = point
	
	def is_past_point(self):
		return now() >= self.point
	
	def delta_now(self):
		return (self.point - now()).total_seconds()
	
	def reset(self):
		self.point = now()
	
	def advance(self, seconds):
		self.point += datetime.timedelta(seconds = seconds)
	
	def elapsed_seconds(self):
		return (now() - self.point).total_seconds()
	
	def does_elapsed_exceed(self, seconds):
		return (self.elapsed_seconds() >= seconds)
