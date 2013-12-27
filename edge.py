import Adafruit_BBIO.GPIO as GPIO

GPIO.setup("P8_9", GPIO.IN)
GPIO.setup("P8_10", GPIO.IN)

def cadence_cb(pin_id):
    print pin_id, 
    if GPIO.input(pin_id):
        print("HIGH")
    else:
        print("LOW")

GPIO.cleanup()
GPIO.add_event_detect("P8_9", GPIO.BOTH, cadence_cb)
GPIO.add_event_detect("P8_10", GPIO.BOTH, cadence_cb)

raw_input("<Return> to stop\n")
