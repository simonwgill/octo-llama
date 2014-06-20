
import datetime

now = datetime.datetime.now

class TimePoint(object):
	def __init__(self, point=now()):
		self.point = point
	
	def reset(self):
		self.point = now()
	
	def elapsed_seconds(self):
		return (now() - self.point).total_seconds()
