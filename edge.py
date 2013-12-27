import Adafruit_BBIO.GPIO as GPIO
import time
from numpy import diff, median, nan, array
SPEED_PIN = "P8_10"
CADENCE_PIN = "P8_9"
PINS = [SPEED_PIN, CADENCE_PIN]

for pin in PINS:
    GPIO.setup(pin, GPIO.IN)

class Buff:
    def __init__(self, max_size=10):
        self.data = []
        self.max_size = max_size

    def append(self, item):
        self.data.append(item)
	self.data = self.data[-self.max_size:]

    def get(self):
        out = self.data[:]
        return out

event_times = {'P8_9':Buff(),
               'P8_10':Buff()}

def cadence_cb(pin_id):
    event_times[pin_id].append(time.time())
    
GPIO.cleanup()
for key in event_times:
    GPIO.add_event_detect(key, GPIO.FALLING, cadence_cb, 0)

def get_duration(pin_id, min_dur=.1, shelf_life=5):
    times = array(event_times[key].get())
    times = times[time.time() - times < shelf_life]
    deltas = diff(times)
    deltas = deltas[deltas > min_dur] ## at least min_dur
    if len(times) > 0:
        out = median(deltas), times[-1]
    else:
        out = nan, nan
    return out

if __name__ == "__main__":
    while True:
        for key in event_times:
            print key, get_duration(key)
        time.sleep(1)

