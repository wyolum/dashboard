'''
based on przemoli-pygametutorial-540433c50ffc
'''
import time
import math
import pygame
from pygame.locals import *
import cevent
from numpy import random
import time

DEG = math.pi / 180.
WIDTH = 800
HEIGHT = 480

MAX_HR = 200
MIN_HR = 50
UNITS = {'MIN': 60,
         'HOUR': 3600,
         'SEC': 1}
MIN = UNITS['MIN']
SEC = UNITS['SEC']
HOUR = UNITS['HOUR']
Zone = {'1':(0, 145, '#000055'),
        '2':(146, 162, '#0000ff'),
        '3':(163, 171, '#00ff00'),
        '4a':(172, 178, '#880088'),
        '4b':(179, 186, '#990000'),
        '5a':(187, 192, '#ff0000'),
        '5b':(193, 195, '#ff0000'),
        '5c':(196, 250, '#ff0000')}
COLORKEY = (1, 128, 1)
zone_codes = '1 2 3 4a 4b 5a 5b 5c'.split()

def html2rgb(s):
    rr = int(s[1:3], 16)
    gg = int(s[3:5], 16)
    bb = int(s[5:7], 16)
    return (rr, gg, bb)
    
fuel = 1000

class Widget:
    def __init__(self, parent, rect, colorkey=None, fill=(0, 0, 0), alpha=255, static=False):
        '''
        rect is where current widget live on parent
        rect[0] -- xleft
        rect[1] -- ytop
        rect[2] -- width
        rect[3] -- height
        '''
        self.surf = pygame.Surface((rect[2], rect[3]))
        self.text_surf = None

        self.surf.set_alpha(alpha)
        if colorkey is not None:
            self.colorkey = colorkey
            self.surf.set_colorkey(self.colorkey)
        if self.surf.fill is not None:
            self.surf.fill(fill)
        self.rect = rect
        self.parent = parent
        self.parent.widgets.append(self)
        self.static=static
        self.changed = True

    def render(self, surf):
        surf.blit(self.surf, (self.rect[0], self.rect[1]))
        self.changed = False
        
    def add_text(self, text, fontsize, location=None, color=(0, 0, 255)):
        if self.text_surf is None:
            self.text_surf = pygame.Surface((self.rect[2], self.rect[3]))
            
        font = pygame.font.Font(None, fontsize)
        text = font.render(text, 1, color)
        textpos = text.get_rect()
        if location is None:
            location = self.surf.get_rect().center
        textpos.center = location
        self.surf.blit(text, textpos)

        
class Chart(Widget):
    def __init__(self, parent, rect, xmin, xmax, ymin, ymax, *args, **kw):
        Widget.__init__(self, parent, rect, *args, **kw)
        self.mx = float(rect[2] - rect[0]) / (xmax - xmin)
        self.bx = rect[0]
        self.my = float(rect[3]) / (ymax - ymin)
        self.by = rect[1]
        self.width = xmax - xmin
        self.height = ymax - ymin
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax

        self.bars = []

    def addline(self, color, xstart, ystart, xstop, ystop, thickness=1):
        px = (xstart - self.xmin) * float(self.rect[2]) / self.width
        py = (ystart - self.ymin) * float(self.rect[3]) / self.height
        qx = (xstop - self.xmin) * float(self.rect[2]) / self.width
        qy = (ystop - self.ymin) * float(self.rect[3]) / self.height
        start = (px, self.rect[3] - py)
        stop = (qx, self.rect[3] - qy)
        pygame.draw.line(self.surf, color, start, stop, thickness)

    def addbar(self, bar):
        self.bars.append(bar)
        color, bar = bar
        rect = self.transform(bar)
        if rect:
            self.surf.fill(color, rect)

    def transform(self, xywh):
        x, y, w, h = xywh
        my = -self.rect[3] / float(self.ymax - self.ymin)
        top = my * (y - self.ymax)
        bottom = my * (y + h - self.ymax)
        bottom = float(h) / (self.ymax - self.ymin)

        # (x, y) = upper left
        # (x + w, y + h) = lower right
        out = [x * self.rect[2] / (self.xmax - self.xmin),
               top,
               w * self.rect[2] / float(self.xmax - self.xmin),
               h * self.rect[3] / float(self.ymax - self.ymin)]
        if out[3] < 1:
            out[3] = 1
        if out[-2] < 1:
            out[-2] = 1
        def intround(v):
            return int(round(v))
        out = map(intround, out)
        # print xywh, out, self.rect
        return out

def getHR():
    return 25 * math.sin(time.time() / 10.) + 175

def getSpeed():
    return 5 * math.cos(time.time() / 20.321) + 25
def getCadence():
    return 90 + 30 * math.cos(time.time() / 7.123 + math.pi/3)

class Progress(Widget):
    def __init__(self, parent, rect, todo_color, done_color, prog=0., *args, **kw):
        '''
        prog: progress from 0.0 to 1.0
        '''
        Widget.__init__(self, parent, rect, *args, **kw)
        self.todo_color = todo_color
        self.done_color = done_color
        self.value = prog
        self.update(self.value)
        
    def update(self, value):
        if value > 1:
            value = 1
        if value < 0:
            value = 0
        if abs(value - self.value) > .01:
            self.changed == True
            self.value = value
            d = self.rect[2] * (1 - self.value)
            self.surf.fill(self.todo_color, (0, 0, self.rect[2], self.rect[3]))
            self.surf.fill(self.done_color, (0, 0, d, self.rect[3]))
            percent = "%.0f%%" % ((1 - value) * 100)
            self.add_text(percent, 20, (self.rect[2]/2, self.rect[3]/2), (0, 0, 0))

class Gauge(Widget):
    def __init__(self, parent, center, radius, angles, min_max_values, value=None, dial_width=10, inner_radius=30, colorkey=COLORKEY, *args, **kw):
        rect = (center[0] - radius, center[1] - radius, 2 * radius, 2 * radius)
        Widget.__init__(self, parent, rect, colorkey=colorkey, fill=colorkey, *args, **kw)
        self.center = center
        self.radius = radius
        self.angles = angles
        self.values = min_max_values
        self.dial_width = dial_width
        self.inner_radius = inner_radius
        if value is not None:
            self.update(value)
    def val2angle(self, value):
        frac = float(value - self.values[0]) / (self.values[1] - self.values[0])
        if frac > 1.05:
            frac = 1.05
        if frac < -.05:
            frac = -.05
        angle = (self.angles[0] + frac * (self.angles[1] - self.angles[0])) * math.pi / 180
        return angle
    def update(self, value):
        angle = self.val2angle(value)
        points = [(self.radius - self.dial_width/2 * math.sin(angle),
                   self.radius + self.dial_width/2 * math.cos(angle)),
                  (self.radius + self.radius*math.cos(angle),
                   self.radius + self.radius*math.sin(angle)),
                  (self.radius + self.dial_width/2 * math.sin(angle),
                   self.radius - self.dial_width/2 * math.cos(angle))]
        
        self.surf.fill(self.colorkey)
        pygame.draw.polygon(self.surf, (0, 0, 255), points , 0)
        if self.inner_radius > 0:
            pygame.draw.circle(self.surf, (0, 0, 0), [self.radius, self.radius], self.inner_radius)

    def arc(self, minval, maxval, radius, thickness, color):
        '''
        draw a wedge behind the gauge
        '''
        pygame.draw.arc(self.surf, color, (self.radius - radius, self.radius-radius, 2 * radius, 2 * radius),
                        -self.val2angle(maxval) - 3*DEG, -self.val2angle(minval) + 3 * DEG, thickness)
        
    def render(self, surf):
        Widget.render(self, surf)

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
        
class Workout(cevent.CEvent):
    def __init__(self, workout_string):
        self.wkout_name, self.intervals = parse_workout(workout_string)
        self._running = True
        self._display_surf = None
        self._image_surf = None
        self.widgets = []
        self.done = False

    def on_init(self):
        pygame.init()
        end = self.intervals[-1][1]
        max_hr = max([Zone[z[2]][1] for z in self.intervals])
        min_hr = min([Zone[z[2]][0] for z in self.intervals])
        max_hr = 200
        self.chart = Chart(self, (40, 418, 570, 50), 0, end, min_hr, max_hr, static=True)
        self.hr_hist = Chart(self, (40, 418, 570, 50), 0, end, min_hr, max_hr, alpha=128, colorkey=COLORKEY, fill=COLORKEY)

        for start, stop, zone in self.intervals:
            lo, hi, color = Zone[zone]
            color = html2rgb(color)
            self.chart.addbar((color, (start, hi, stop - start, hi - lo)))

        ## create widgets.
        self.progress = Progress(self, (255, 373, WIDTH - 2 * 255, 25), (0, 255, 255), (0, 0, 255))
        self.fuel = Gauge(self, (WIDTH / 2, HEIGHT - 402), 100, [210, 330], [0, 1000], dial_width=5, inner_radius=0)
        self.speed = Gauge(self, (WIDTH / 2, HEIGHT / 2), 100, [140, 400], [0, 60])
        self.hr_zones = Gauge(self, (180, HEIGHT - 209), 90, [140, 400], [min_hr, max_hr], inner_radius=20, static=True)
        for zone in Zone:
            zone = Zone[zone]
            self.hr_zones.arc(zone[0], zone[1], 80, 3, html2rgb(zone[2]))
        self.hr_meter = Gauge(self, (180, HEIGHT - 209), 85, [140, 400], [min_hr, max_hr], inner_radius=20)
        self.cadence_zones = Gauge(self, (WIDTH-180, HEIGHT-209), 85, [140, 400], [50, 130], inner_radius=20, static=True)
        self.cadence_zones.arc(90, 100, 80, 3, (0, 255, 0))
        self.cadence = Gauge(self, (WIDTH-180, HEIGHT-209), 75, [140, 400], [0, 130], inner_radius=20)
        self.fuel.surf = pygame.Surface((200, 75))
        self.fuel.surf.set_colorkey(COLORKEY)
        self.fuel.surf.fill(COLORKEY)

        # self.text = Widget(self, (0, 55, WIDTH, 40), fill=(0, 0, 0))
        self._display_surf = pygame.display.set_mode((WIDTH,HEIGHT), pygame.HWSURFACE)
        self._running = True
        self._image_surf = pygame.image.load("WyoLum_racing.png").convert()

        ### put all static widgets on image surf
        for wid in self.widgets:
            if wid.static:
                wid.render(self._image_surf)
        
        self.start = time.time()
        self.interval_start = 0
        self.interval_num = 0
        self._display_surf.blit(self._image_surf,(0,0))

    def on_loop(self):
        global fuel

        
        ## update values
        rect = self._display_surf.get_rect()
        heartrate = getHR()
        speed = getSpeed()
        cadence = getCadence()
        fuel -= 10
        now = time.time() - self.start
        interval = self.intervals[self.interval_num]
        duration = (interval[1] - interval[0])
        togo = self.interval_start + duration - now
        if togo <= 0:
            self.interval_num += 1
            self.interval_start = now
            if self.interval_num >= len(self.intervals) :
                self.done = True
                
            

        ## update widgets
        self.fuel.update(fuel)
        self.progress.done_color = html2rgb(Zone[interval[2]][2])
        self.hr_meter.update(heartrate)
        self.cadence.update(cadence)
        self.hr_hist.addbar(((255, 255, 255, 128), (now, heartrate, 0, heartrate)))
        self.progress.update(togo / duration)
        self.speed.update(speed)

    def on_render(self):
        ## render children
        for wid in self.widgets:
            if not wid.static:
                self._display_surf.blit(self._image_surf, wid.rect[:2], (wid.rect))
                wid.render(self._display_surf)
            # pygame.display.update(wid.rect)
        ## black above and below fuel gauge
        self._display_surf.fill((0,0,0), (WIDTH/2 - 175/2, 0, 175, 30))
        # self._display_surf.fill((0,0,0), (234, 50, 175, 30))
        pygame.display.flip()
    def on_exit(self):
        self._running = False

    def on_cleanup(self):
        pygame.quit()

    def on_key_down(self, event):
        if event.key == K_ESCAPE:
            self._running = False
        
    def on_execute(self):
        if self.on_init() == False:
            self._running = False
    
        while( self._running and not self.done):
            self.on_render() ## only render once per second
            for i in range(200): ## watch for events and updates
                self.on_loop()
                for event in pygame.event.get():
                    self.on_event(event)

        pygame.display.flip()
        font = pygame.font.Font(None, 48)
        text = font.render("Workout Complete!", 1, (255, 0, 0))
        textpos = text.get_rect()
        location = self._display_surf.get_rect().centerx
        textpos.center = location, 75
        self._display_surf.blit(text, textpos)
        pygame.display.flip()

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            time.sleep(.05)
            
        self.on_cleanup()
 
 
if __name__ == "__main__" :
    workout_string = '50 on 50 off::Z2 1*MIN, ' + ','.join(3 * ['Z4b 50, Z2 50,Z4b 50, Z2 50,Z4b 50, Z2 50,Z4b 50, Z2 50,Z4b 50, Z2 50,Z4b 50, Z2 50,Z4b 50, Z2 4*MIN'])
    workout_string = 'UNDER_OVER::Z2 15*MIN, Z3 5*MIN, ' + ','.join(7 * ['Z4a 1*MIN, Z3 1*MIN, Z4b 1*MIN, Z3 1*MIN, Z2 4*MIN'])    
    theApp = Workout(workout_string)
    theApp.on_execute()
