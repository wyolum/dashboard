import Adafruit_BBIO.GPIO as GPIO
import time
from numpy import diff

GPIO.setup("P8_9", GPIO.IN)
GPIO.setup("P8_10", GPIO.IN)

class Buff:
    def __init__(self, max_size=10):
        self.data = []
        self.max_size = max_size

    def append(self, item):
        self.data.append(item)
	self.data = self.data[-self.max_size:]

    def get(self):
        return self.data[:]

times = {'P8_9':Buff(),
         'P8_10':Buff()}

def cadence_cb(pin_id):
    times[pin_id].append(time.time())
    
GPIO.cleanup()
for key in times:
    GPIO.add_event_detect(key, GPIO.FALLING, cadence_cb, 0)

while True:
    for key in times:
        print key, diff(times[key].get())
    time.sleep(1)

