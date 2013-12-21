import shutil
import tkFileDialog
import os.path
import datetime
import serial
import time
from Tkinter import *

W = 800
H = 600
MAX_HR = 200
MIN_HR = 50

### tables:
class Table:
    pass
class Athlete:
    '''
    Last, Frist, Age, Sex, z1_max, z2_max, z3_max, z4a_max, z4b_max, z5a_max, z5b_max, z5c_max, LT
    '''

UNITS = {'MIN': 60,
         'HOUR': 3600,
         'SEC': 1}
MIN = UNITS['MIN']
SEC = UNITS['SEC']
HOUR = UNITS['HOUR']

class Workout:
    '''
    Name, definition
    '''
    @staticmethod
    def parse_workout(s):
        name, s = s.split("::")
        intervals = [x.strip()  for x in s.lower().split(',')]
        now = 0
        out = []
        for interval in intervals:
            zone, duration = interval.split()
            if zone[0] != 'z':
                raise ValueError("Unexpected zone '%s' in workout\n    '%s'" % (zone, s))
            zone = zone[1:]
            if '*' in duration:
                duration, unit = duration.split('*')
                duration = float(duration) * UNITS[unit.upper()]
            else:
                duration = float(duration) ## default to seconds
            out.append((now, now + duration, zone))
            now += duration
        return name, out

workout_string = 'UNDER_OVER::Z2 15*MIN, Z3 5*MIN, ' + ','.join(7 * ['Z4a 1*MIN, Z3 1*MIN, Z4b 1*MIN, Z3 1*MIN, Z2 4*MIN'])
workout_string = '50 on 50 off::Z2 1*MIN, ' + ','.join(3 * ['Z4b 50, Z2 50,Z4b 50, Z2 50,Z4b 50, Z2 50,Z4b 50, Z2 50,Z4b 50, Z2 50,Z4b 50, Z2 50,Z4b 50, Z2 4*MIN'])
name, intervals = Workout.parse_workout(workout_string)

root = Tk()
history_f = Frame(root)
history_f.pack(side=LEFT)
canvas = Canvas(root, width=W, height=H)
canvas.create_rectangle(1, 1, W, H)
canvas.pack(side=LEFT)
current_f = Frame(root)
font = 'Courier', 60

## time: total, togo
time_frame = Frame(root)
total_time_l = Label(time_frame, text='00:00:00', font=font)
togo_time_l= Label(time_frame, text='00:00', font=font)

total_time_l.pack()
togo_time_l.pack()
time_frame.pack()

port = '/dev/ttyUSB1'
port = '/dev/ttyUSB0'

try:
    ser = serial.Serial(port, baudrate=9600, timeout=.05)
except:
    ser = None

def fast_readline():
    out = []
    c = 0
    while c != '\r':
        c = ser.read(1)
        out.append(c)
    return ''.join(out)
def get_hr():
    if ser:
        ser.write('G1' + chr(13))
        res = fast_readline()
        if len(res) > 5:
            out = int(res.split()[2])
        else:
            out = 0
    else:
        out = 0
    return out

## HR: lo, hi, current
hr_frame = Frame(root)
left_f = Frame(hr_frame)
left_f.pack(side=LEFT)
right_f = Frame(hr_frame)
right_f.pack(side=RIGHT);
hr_lo_l = Label(left_f, text="000", font=font)
hr_hi_l = Label(left_f, text="000", font=font)
hr_current_l = Label(left_f, text="000", font=font)
hr_zone_l = Label(right_f, text=":1", font=font)

status_l = Label(current_f, text="Ready", font=font);

Zone = {'1':(0, 145, '#000055'),
        '2':(146, 162, '#0000ff'),
        '3':(163, 171, '#00ff00'),
        '4a':(172, 178, '#880088'),
        '4b':(179, 186, '#990000'),
        '5a':(187, 192, '#ff0000'),
        '5b':(193, 195, '#ff0000'),
        '5c':(196, 250, '#ff0000')}

zone_codes = '1 2 3 4a 4b 5a 5b 5c'.split()

def make_interval(start, n, base):
    out = []
    now = start
    for i in range(n):
        for b in base:
            dur = b[1] - b[0]
            out.append((now, now + dur, b[2]))
            now += dur
    return out

warm_up = [( 0 * MIN, 15 * MIN, '2'),
           (15 * MIN, 20 * MIN, '3')]

hard = [(0 * MIN, 1 * MIN, '4a'),
        (1 * MIN, 2 * MIN, '3'),
        (2 * MIN, 3 * MIN, '4b'),
        (3 * MIN, 4 * MIN, '3'),
        (4 * MIN, 8 * MIN, '2'),
        ]
all = [] + warm_up + make_interval(warm_up[1][1], 7, hard)
# intervals = all


test_up = [( 0 * MIN, 2 * MIN, '2'),
           (2 * MIN, 4 * MIN, '3')]
# intervals = make_interval(0, 10, test_up)

status = 0

def roundup(n):
    return int(10 * (int(n / 10.) + 1))
def rounddown(n):
    return int(10 * (int(n / 10.)))

def transform(bbox):
    out = [W * bbox[0] / MAX_T, H * (bbox[1] - MIN_HR) / (MAX_HR - MIN_HR),
           W * bbox[2] / MAX_T, H * (bbox[3] - MIN_HR) / (MAX_HR - MIN_HR)]
    out[1] = H - out[1]
    out[3] = H - out[3]
    if out[1] >= H:
        out[1] = H - 1
    if out[3] >= H:
        out[3] = H - 1
    return out

def plot_clear():
    pass

def plot_workout(intervals):
    ## find max hr, time
    global MAX_T
    canvas.delete("grid")
    canvas.delete("hr_zone")
    canvas.delete('hr_line')
    canvas.delete('hr_point')
    
    max_hr = 0
    max_t = 0
    for row in intervals:
        t = row[1]
        if t > max_t:
            max_t = t
        zone = Zone[row[2]]
        if zone[1] > max_hr:
            max_hr = zone[1]
    MAX_T = roundup(max_t)
    max_hr = MAX_HR

    for row in intervals:
        zone = Zone[row[2]]
        lo, hi, color = zone
        lo -= .5
        hi += .5

        bbox = transform((row[0], lo, row[1], hi))
        canvas.create_rectangle(*bbox, fill=zone[2], tag='hr_zone')

    HR = Zone['4a'][1]
    canvas.create_line(*transform((0, HR, MAX_T, HR)), tag='grid', dash=(4, 4), fill='red')

    for HR in range(MIN_HR + 25, MAX_HR, 25):
        canvas.create_line(*transform((0, HR, MAX_T, HR)), tag='grid', dash=(4, 4), fill = 'grey')
    for T in range(15 * MIN, MAX_T, 15 * MIN):
        canvas.create_line(*transform((T, MIN_HR, T, MAX_HR)), tag='grid', dash=(4, 4), fill = 'grey')

plot_workout(intervals)
# here

interval = -1 ## before start
start_time = time.time()
def start(*args):
    global start_time, last, interval, status, hr_out
    if status == 1:
        stop()
    else:
        start_time = time.time()
        last = 0
        interval = 0
        status_l.config(text="Game On")
        button.config(text="Stop")
        status = 1
        fn = get_filename()
        print 'data stored in', fn
        hr_out = open(fn, 'w')
        print >> hr_out, 'time, heartrate, zone lo, zone hi, zone'

zone_label = '1'
def stop(*args):
    global status, interval
    interval = -1
    status_l.config(text='Ready')
    hr_zone_l.config(text=':%s' % zone_label)
    button.config(text="Start")
    status = 0

def get_filename():
    t = time.localtime()
    fn = '%4d%02d%02d-%02d%02d%02d-workout.csv' % (t.tm_year, t.tm_mon, t.tm_mday, 
                                                   t.tm_hour, t.tm_min, t.tm_sec)
    fn = os.path.join('Data', fn)
    return fn

last_point = None

def update():
    global interval, zone_label
    global last_point

    now = int(time.time())
    current_hr = get_hr()
    current_time = now - start_time
    
    total_time = now - start_time + 1
    if total_time > 0:
        hh, ss = divmod(total_time, 3600)
        mm, ss = divmod(total_time, 60)
    else:
        hh = mm = ss = 0
    total_time_l.config(text="%02d:%02d:%02d" % (hh, mm, ss))
        
    if 0 <= interval and interval < len(intervals):
        int_start, int_stop, zone_label = intervals[interval]
        dur = int_stop - int_start
        if last_point:
            line = (last_point[0], last_point[1], current_time, current_hr)
            line = transform(line)
            canvas.create_line(*line, tag='hr_line')
        last_point = current_time, current_hr
        point = transform((current_time, current_hr, 0, 0))
        point[0] = point[0] - 3
        point[1] = point[1] - 3
        point[2] = point[0] + 6
        point[3] = point[1] + 6
        canvas.delete('hr_point')
        canvas.create_oval(point, fill='red', tag='hr_point')
        
    else:
        int_start = 0
        int_stop = 3600
        zone_label = '1'
        dur = 3600
    zone = Zone[zone_label]
    togo = start_time + int_start + dur - now
    if togo > 0:
        mm, ss = divmod(togo, 60)
    else:
        mm = ss = 0
    togo_time_l.config(text="%02d:%02d" % (mm, ss))

    hr_lo_l.config(text="%03d" % zone[0])
    hr_hi_l.config(text="%03d" % zone[1])

    hr_current_l.config(text="%03d" % current_hr)
    hr_zone_l.config(text=":%s" % zone_label)
    if current_hr < zone[0]:
        hr_current_l.config(fg='blue')
    elif current_hr > zone[1]:
        hr_current_l.config(fg='red')
    else:
        hr_current_l.config(fg='green')
    if status:
        line = int(time.time() - start_time), current_hr, zone[0], zone[1], zone_label
        line = ','.join(map(str, line))
        print >> hr_out, line

    if togo < 0:
        interval += 1
    if interval < len(intervals):
        pass
    else:
        status_l.config(text="ready")
        stop()
    root.after(1000, update)
## start button
button = Button(current_f, text="Start", command=start, font=font)


hr_lo_l.pack(side=TOP)
hr_current_l.pack(side=TOP)
hr_hi_l.pack(side=TOP)
hr_zone_l.pack(side=RIGHT)
hr_frame.pack(side=TOP)
button.pack(side=TOP)
status_l.pack(side=TOP)
current_f.pack(side=TOP)


#### Callbacks
file_opt = {}
def file_open_dialog():
    out = tkFileDialog.askopenfilename(**file_opt)
    if out:
        print out

def file_save_dialog():
    saveasfn = tkFileDialog.asksaveasfilename(
        defaultextension='.WIF',
        filetypes=[
            ('Comma Separated Vale', '.csv'),
            ])
    if saveasfn:
        shutil.copyfile(fn, saveasfn)
        
menubar = Menu(root)
root.config(menu=menubar)
fileMenu = Menu(menubar)
fileMenu.add_command(label="Open", command=file_open_dialog)
fileMenu.add_command(label="Save", command=file_save_dialog)
fileMenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=fileMenu)


root.after(10, update)
root.mainloop()

