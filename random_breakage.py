
import datetime
import random
import time

lowest_time = 20
highest_time = 120

period = datetime.timedelta(seconds = random.randint(lowest_time, highest_time))
end = datetime.datetime.now() + period

while datetime.datetime.now() < end:
	pass
