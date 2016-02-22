import kivy
kivy.require('1.0.6') # replace with your current kivy version !

#sPIder V2.0

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.slider import Slider
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from math import cos, sin, pi
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ListProperty, ObjectProperty
from kivy.uix.label import Label
from kivy.uix.settings import SettingsWithTabbedPanel
from kivy.uix.settings import SettingsWithSidebar
from kivy.logger import Logger
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, SlideTransition, SwapTransition, FadeTransition, WipeTransition, FallOutTransition, RiseInTransition
from time import time
from kivy.animation import Animation
from kivy.core.window import Window


import RPi.GPIO as GPIO
import sys
import datetime
import time
import os
import subprocess
import glob

#_____________________________________________________________
        #GPIO SETUP


#name GPIO pins
seekupPin = 13
seekdownPin = 19
auxPin = 16
amfmPin = 26
garagePin = 20
radarPin = 21
ledsPin = 5
driverwindowdownPin = 17  
driverwindowupPin = 15 
passwindowdownPin = 27 
passwindowupPin = 18 


HotKey1Pin = 6
HotKey2Pin = 12

#setup GPIO
GPIO.setmode(GPIO.BCM)

GPIO.setwarnings(False)

GPIO.setup(seekupPin, GPIO.OUT)
GPIO.setup(seekdownPin, GPIO.OUT)
GPIO.setup(auxPin, GPIO.OUT)
GPIO.setup(amfmPin, GPIO.OUT)
GPIO.setup(garagePin, GPIO.OUT)
GPIO.setup(radarPin, GPIO.OUT)
GPIO.setup(ledsPin, GPIO.OUT)
GPIO.setup(driverwindowdownPin, GPIO.OUT)
GPIO.setup(driverwindowupPin, GPIO.OUT)
GPIO.setup(passwindowdownPin, GPIO.OUT)
GPIO.setup(passwindowupPin, GPIO.OUT)

GPIO.setup(HotKey1Pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(HotKey2Pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)



#initial state of GPIO
GPIO.output(seekupPin, GPIO.HIGH)
GPIO.output(seekdownPin, GPIO.HIGH)
GPIO.output(auxPin, GPIO.HIGH)
GPIO.output(amfmPin, GPIO.HIGH)
GPIO.output(garagePin, GPIO.HIGH)
GPIO.output(radarPin, GPIO.HIGH)
GPIO.output(ledsPin, GPIO.LOW)
GPIO.output(driverwindowdownPin, GPIO.HIGH)
GPIO.output(driverwindowupPin, GPIO.HIGH)
GPIO.output(passwindowdownPin, GPIO.HIGH)
GPIO.output(passwindowupPin, GPIO.HIGH)


#TEMP PROBE STUFF

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
#base_dir = '/sys/bus/w1/devices/'
#device_folder = glob.glob(base_dir + '28*')[0]
#device_file = device_folder + '/w1_slave'

global temp_f #make this var global for use in messages
temp_f = 0

global TEMPON
TEMPON = 0

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp():
    global temp_f
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        #time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c_raw = float(temp_string) / 1000.0
        temp_f_raw = temp_c_raw * 9.0 / 5.0 + 32.0
        temp_f = "{0:.0f}".format(temp_f_raw) #only whole numbers
    
#_________________________________________________________________
        #VARIABLES

global SEEKUPON 
SEEKUPON = 0

global SEEKDOWNON 
SEEKDOWNON = 0

global AUXON 
AUXON = 0

global AMFMON 
AMFMON = 0

global GARAGEON 
GARAGEON = 0

global RADARON 
RADARON = 0

global LEDSON 
LEDSON = 0

global WINDOWSDOWNON 
WINDOWSDOWNON = 0

global WINDOWSUPON 
WINDOWSUPON = 0

global clock
clock = 1

global analog
analog = 1

global message
message = 0

global swminute
swminute = 0

global swsecond
swsecond = 0

global swtenth
swtenth = 0

global swactive
swactive = 0

global swstring
swstring = 0

global testvar
testvar = 0

global testvar2
testvar2 = 0

global hotkey1string
hotkey1string = "Seek Up"

global hotkey2string
hotkey2string = "None"

global screenon
screenon = 1

global windowuptime #time it takes front windows to rise
windowuptime = 7

global windowdowntime #time it takes front windows to open
windowdowntime = 6

global clocktheme
clocktheme = 1


#__________________________________________________________________
        

        #GPIOIN STUFFS

def HotKey1(channel):
    global hotkey1string
    global screenon
    global windowuptime
    global windowdowntime
    global WINDOWSUPON
    global WINDOWSDOWNON
    if hotkey1string == "Seek Up":
        Clock.schedule_once(seekup_callback)
        Clock.schedule_once(seekup_callback,.1)
    if hotkey1string == "Seek Down":
        Clock.schedule_once(seekdown_callback)
        Clock.schedule_once(seekdown_callback,.1)
    if hotkey1string == "Garage":
        Clock.schedule_once(garage_callback)
        Clock.schedule_once(garage_callback,.1)
    if hotkey1string == "Radar":
        Clock.schedule_once(radar_callback)
    if hotkey1string == "Cup Lights":
        Clock.schedule_once(leds_callback)

    if hotkey1string == "Windows Up":
        if WINDOWSDOWNON == 0: #only works when windows down isnt running
            Clock.schedule_once(windowsup_callback)
            Clock.schedule_once(windowsupOFF_callback, windowuptime)
            return
        if WINDOWSUPON == 1:
            Clock.schedule_once(windowsupOFF_callback) #if windows going up while pushed, will cancel and stop windows

    if hotkey1string == "Windows Down":
        if WINDOWSUPON == 0: #only works when windows up isnt running
            Clock.schedule_once(windowsdown_callback)
            Clock.schedule_once(windowsdownOFF_callback, windowdowntime)
            return
        if WINDOWSDOWNON == 1:
            Clock.schedule_once(windowsdownOFF_callback) #if windows going down while pushed, will cancel and stop windows

    if hotkey1string == "Screen Toggle":
        if screenon == 1:
            os.system("sudo echo 1 > /sys/class/backlight/rpi_backlight/bl_power") #turns screen off
            screenon = 0
            return
        if screenon == 0:
            os.system("sudo echo 0 > /sys/class/backlight/rpi_backlight/bl_power") #turns screen on
            screenon = 1
            return
    if hotkey1string == "None":
        return
    

def HotKey2(channel):
    global hotkey2string
    global screenon
    global windowuptime
    global windowdowntime
    global WINDOWSUPON
    global WINDOWSDOWNON
    if hotkey2string == "Seek Up":
        Clock.schedule_once(seekup_callback)
        Clock.schedule_once(seekup_callback,.1)
    if hotkey2string == "Seek Down":
        Clock.schedule_once(seekdown_callback)
        Clock.schedule_once(seekdown_callback,.1)
    if hotkey2string == "Garage":
        Clock.schedule_once(garage_callback)
        Clock.schedule_once(garage_callback,.1)
    if hotkey2string == "Radar":
        Clock.schedule_once(radar_callback)
    if hotkey2string == "Cup Lights":
        Clock.schedule_once(leds_callback)
        
    if hotkey2string == "Windows Up":
        if WINDOWSDOWNON == 0: #only works when windows down isnt running
            Clock.schedule_once(windowsup_callback)
            Clock.schedule_once(windowsupOFF_callback, windowuptime)
            return
        if WINDOWSUPON == 1:
            Clock.schedule_once(windowsupOFF_callback) #if windows going up while pushed, will cancel and stop windows

    if hotkey2string == "Windows Down":
        if WINDOWSUPON == 0: #only works when windows up isnt running
            Clock.schedule_once(windowsdown_callback)
            Clock.schedule_once(windowsdownOFF_callback, windowdowntime)
            return
        if WINDOWSDOWNON == 1:
            Clock.schedule_once(windowsdownOFF_callback) #if windows going down while pushed, will cancel and stop windows

    if hotkey2string == "Screen Toggle":
        if screenon == 1:
            os.system("sudo echo 1 > /sys/class/backlight/rpi_backlight/bl_power") #turns screen off
            screenon = 0
            return
        if screenon == 0:
            os.system("sudo echo 0 > /sys/class/backlight/rpi_backlight/bl_power") #turns screen on
            screenon = 1
            return
    if hotkey2string == "None":
        return

GPIO.add_event_detect(HotKey1Pin, GPIO.FALLING, callback=HotKey1, bouncetime=1000)

GPIO.add_event_detect(HotKey2Pin, GPIO.FALLING, callback=HotKey2, bouncetime=1000)
            
            
        #DEFINE CLASSES            


        #ROOT CLASSES

class ROOT(FloatLayout):
    pass
class QUICKEYSLayout(FloatLayout):
    pass

        #MAIN SCREEN CLASSES

class MainScreen(Screen):
    pass
class AudioScreen(Screen):
    pass
class PerfScreen(Screen):
    pass
class AppsScreen(Screen):
    global clock
    pass
class ControlsScreen(Screen):
    pass
class SettingsScreen(Screen):
    pass

class KillScreen(Screen):
    pass

        #APP SCREEN CLASSES

class PaintScreen(Screen):
    pass
class FilesScreen(Screen):
    pass
class LogoScreen(Screen):
    pass
class ClockChooserScreen(Screen):
    pass
class ClassicClockScreen(Screen):
    pass
class SportClockScreen(Screen):
    pass
class ExecutiveClockScreen(Screen):
    pass
class InfoClockScreen(Screen):
    pass
class PhotoClockScreen(Screen):
    pass

class GPSScreen(Screen):
    pass

class StopwatchScreen(Screen):
    pass

class DiagnosticsScreen(Screen):
    pass

class HotKey1ChooserScreen(Screen):
    pass
class HotKey2ChooserScreen(Screen):
    pass
class OffScreen(Screen):
    pass

        #SCREENMANAGER CLASS

class ScreenManagement(ScreenManager):
    pass



class AnchorLayout(AnchorLayout):
    
    pass



        #APP CLASSES

class CLOCK(Label): #CLOCK widget - contains the main interface's Clock
    
    
    def update(self, *args):
        time_hour = time.strftime("%I") #time_hour

        if time_hour[0] == "0": #one digit format
            time_hour = " "+time_hour[1]

        time_minute = time.strftime("%M") #time_minute

        time_now = time_hour+":"+time_minute #create sting format (hour:minute)
        
        if clock == 1:
            self.font_size = 60
            self.pos = (0,190)
            self.text = time_now
            
        if clock == 0:
            self.font_size = 60
            self.pos = (0,190)
            self.text = " "

        if clock == 2:
            self.font_size = 140
            self.text = time_now
            self.pos = (-200,150)
          

        #VARIABLE PRINTER
            #to use - comment out the normal clock == 1 if, and choose a type of var and uncomment

        #if clock == 1:
            #self.font_size = 30
            #self.pos = (0,190)
            #self.text = "%d" %WINDOWSUPON + "%d" %WINDOWSDOWNON #for numbers
            #self.text = str(SettingsScreen.buttons.analogclockswitch.active) #for strings

class MESSAGE(Label): #MESSAGE class - will display a set message any where on a page - use vars to set these
    
    
    def update(self, *args):
        
        #temp variable stuff

        #os.system('/opt/vc/bin/vcgencmd measure_temp') #system command for temp
        if message == 1:
            temperaturestring = subprocess.check_output(["/opt/vc/bin/vcgencmd","measure_temp"])
            corevoltagestring = subprocess.check_output(["/opt/vc/bin/vcgencmd","measure_volts core"])

            temperature = (temperaturestring.split('=')[1][:-3])
            corevoltage = (corevoltagestring.split('=')[1][:-3])
            

        #stopwatch variable stuff
     
        global swminute
        global swsecond
        global swtenth
        global swactive
        global swstring
        global swminutestring
        global swsecondstring

        
        if swactive == 1:
            swtenth += 1
            if swtenth == 10:
                swtenth = 0
                swsecond += 1
            if swsecond == 60:
                swsecond = 0
                swminute += 1

        #fortmatting for stopwatch display
        if swsecond < 10:
            swsecondstring = "0"+str(swsecond)
        else:
            swsecondstring = str(swsecond)
            
        if swminute < 10:
            swminutestring = "0"+str(swminute)
        else:
            swminutestring = str(swminute)
            
        swstring = (swminutestring+":"+swsecondstring+":"+str(swtenth)+"0")

        #date variable stuff

        if message == 3:
            day = time.strftime("%A")
            month = time.strftime("%B")
            date = time.strftime("%d")

            if date[0] == "0": #one digit format for day of month
                date = " "+date[1]

            dateinfo = day + ", " + month + " " + date

        
        #the logic for what the message says
        if message == 0:
            self.text = " "

        if message == 1: #used for displaying the CPU temp
            self.text = "CPU Temp = "+temperature+" "+ u'\N{DEGREE SIGN}' + "C\n" + "Core Voltage = " + corevoltage + " V"
            self.font_size = 60
            self.pos = (0,0)
            #self.color = (0.0, 1.0, 1.0)

        if message == 2: #used for displaying the stopwatch hour:minute:second:onehundreth
            self.text = swstring
            self.font_size = 150
            self.pos = (0,50)
            #self.color = (1.0, 1.0, 1.0)
            
        if message == 3: # used for displaying the date on the info clock page
            self.text = dateinfo
            self.font_size = 60
            self.pos = (0,0)
            #self.color = (1.0, 1.0, 1.0)

        if message == 4:  #used for displaying the set hotkey labels
            #if HotKey1

            self.text = "Hot Key 1: "+ hotkey1string + "\n \n \n" + "Hot Key 2: " + hotkey2string + "\n" + "                                                     "
            #self.text = hotkey1string + "\n \n \n" + hotkey2string
            self.font_size = 20
            self.pos = (-240,88)
            #self.color = (0.0, 0.0, 0.0)

        if message == 5: # used for displaying the status of radar on mainscreen - green dot in upper left means on
            if RADARON == 1:
                self.text = "."
            if RADARON == 0:
                self.text = " "
            self.font_size = 100
            #self.color = (0.2, 0.5, 0.2)
            self.pos = (-390,255)


            
class CabinTempWidget(Label): #Cabin Temperature class - will display cabin temp in F on any screen
    
    def update(self, *args):

        temp_f_string = str(temp_f)
        
        if TEMPON == 1:
            self.text = temp_f_string + u'\N{DEGREE SIGN}'
        if TEMPON == 0: 
            self.text = " "
        self.font_size = 50
        self.pos = (350,200)
        

class Painter(Widget): #Paint App
    
    def on_touch_down(self, touch):
        with self.canvas:
            touch.ud["line"] = Line(points=(touch.x, touch.y))

    def on_touch_move(self,touch):
        touch.ud["line"].points += [touch.x, touch.y]

#Analog Clock Stuffs

class Ticks(Widget):
    def __init__(self, **kwargs):
        super(Ticks, self).__init__(**kwargs)
        self.bind(pos=self.update_clock)
        self.bind(size=self.update_clock)

    def update_clock(self, *args):
        global clocktheme
        self.canvas.clear()
        with self.canvas:
            time = datetime.datetime.now()
            x = self.center_x
            y = self.center_y + 36 # to move the clock on x and y axis -  36 is middle if .85 is screen percentage
            if analog == 0: #no analog
                Color(0.2, 0.5, 0.0, 0.0)
                Line(points=[self.center_x, self.center_y, self.center_x+0.8*self.r*sin(pi/30*time.second), self.center_y+0.8*self.r*cos(pi/30*time.second)], width=1, cap="round")
                Color(0.3, 0.6, 0.0, 0.0)
                Line(points=[self.center_x, self.center_y, self.center_x+0.7*self.r*sin(pi/30*time.minute), self.center_y+0.7*self.r*cos(pi/30*time.minute)], width=2, cap="round")
                Color(0.4, 0.7, 0.0, 0.0)
                th = time.hour*60 + time.minute
                Line(points=[self.center_x, self.center_y, self.center_x+0.5*self.r*sin(pi/360*th), self.center_y+0.5*self.r*cos(pi/360*th)], width=3, cap="round")

            if analog == 1: #stock green analog clock on mainscreen(default), theme can be changed by tapping clock 
                if clocktheme == 1: #Green
                    Color(0.2, 0.5, 0.2)
                    Line(points=[self.center_x, self.center_y, self.center_x+0.8*self.r*sin(pi/30*time.second), self.center_y+0.8*self.r*cos(pi/30*time.second)], width=1, cap="round")
                    Color(0.3, 0.6, 0.3)
                    Line(points=[self.center_x, self.center_y, self.center_x+0.7*self.r*sin(pi/30*time.minute), self.center_y+0.7*self.r*cos(pi/30*time.minute)], width=2, cap="round")
                    Color(0.4, 0.7, 0.4)
                    th = time.hour*60 + time.minute
                    Line(points=[self.center_x, self.center_y, self.center_x+0.5*self.r*sin(pi/360*th), self.center_y+0.5*self.r*cos(pi/360*th)], width=3, cap="round")

                if clocktheme == 2: #Blue
                    Color(0.2, 0.6, 0.8)
                    Line(points=[self.center_x, self.center_y, self.center_x+0.8*self.r*sin(pi/30*time.second), self.center_y+0.8*self.r*cos(pi/30*time.second)], width=1, cap="round")
                    Color(0.0, 0.4, 0.8)
                    Line(points=[self.center_x, self.center_y, self.center_x+0.7*self.r*sin(pi/30*time.minute), self.center_y+0.7*self.r*cos(pi/30*time.minute)], width=2, cap="round")
                    Color(0.0, 0.4, 0.8)
                    th = time.hour*60 + time.minute
                    Line(points=[self.center_x, self.center_y, self.center_x+0.5*self.r*sin(pi/360*th), self.center_y+0.5*self.r*cos(pi/360*th)], width=3, cap="round")

                if clocktheme == 3: #Red
                    Color(0.8, 0.0, 0.0)
                    Line(points=[self.center_x, self.center_y, self.center_x+0.8*self.r*sin(pi/30*time.second), self.center_y+0.8*self.r*cos(pi/30*time.second)], width=1, cap="round")
                    Color(0.8, 0.0, 0.0)
                    Line(points=[self.center_x, self.center_y, self.center_x+0.7*self.r*sin(pi/30*time.minute), self.center_y+0.7*self.r*cos(pi/30*time.minute)], width=2, cap="round")
                    Color(0.8, 0.0, 0.0)
                    th = time.hour*60 + time.minute
                    Line(points=[self.center_x, self.center_y, self.center_x+0.5*self.r*sin(pi/360*th), self.center_y+0.5*self.r*cos(pi/360*th)], width=3, cap="round")

                if clocktheme == 4: #Orange
                    Color(1.0, 0.6, 0.2)
                    Line(points=[self.center_x, self.center_y, self.center_x+0.8*self.r*sin(pi/30*time.second), self.center_y+0.8*self.r*cos(pi/30*time.second)], width=1, cap="round")
                    Color(1.0, 0.5, 0.0)
                    Line(points=[self.center_x, self.center_y, self.center_x+0.7*self.r*sin(pi/30*time.minute), self.center_y+0.7*self.r*cos(pi/30*time.minute)], width=2, cap="round")
                    Color(1.0, 0.5, 0.0)
                    th = time.hour*60 + time.minute
                    Line(points=[self.center_x, self.center_y, self.center_x+0.5*self.r*sin(pi/360*th), self.center_y+0.5*self.r*cos(pi/360*th)], width=3, cap="round")

                if clocktheme == 5: #DarkGrey
                    Color(0.25, 0.25, 0.25)
                    Line(points=[self.center_x, self.center_y, self.center_x+0.8*self.r*sin(pi/30*time.second), self.center_y+0.8*self.r*cos(pi/30*time.second)], width=1, cap="round")
                    Color(0.25, 0.25, 0.25)
                    Line(points=[self.center_x, self.center_y, self.center_x+0.7*self.r*sin(pi/30*time.minute), self.center_y+0.7*self.r*cos(pi/30*time.minute)], width=2, cap="round")
                    Color(0.25, 0.25, 0.25)
                    th = time.hour*60 + time.minute
                    Line(points=[self.center_x, self.center_y, self.center_x+0.5*self.r*sin(pi/360*th), self.center_y+0.5*self.r*cos(pi/360*th)], width=3, cap="round")

                if clocktheme == 6: #WhiteRed
                    Color(1.0, 0.0, 0.0)
                    Line(points=[self.center_x, self.center_y, self.center_x+0.8*self.r*sin(pi/30*time.second), self.center_y+0.8*self.r*cos(pi/30*time.second)], width=1, cap="round")
                    Color(1.0, 1.0, 1.0)
                    Line(points=[self.center_x, self.center_y, self.center_x+0.7*self.r*sin(pi/30*time.minute), self.center_y+0.7*self.r*cos(pi/30*time.minute)], width=2, cap="round")
                    Color(1.0, 1.0, 1.0)
                    th = time.hour*60 + time.minute
                    Line(points=[self.center_x, self.center_y, self.center_x+0.5*self.r*sin(pi/360*th), self.center_y+0.5*self.r*cos(pi/360*th)], width=3, cap="round")

                if clocktheme == 7: #Black(off)
                    Color(0.0, 0.0, 0.0)
                    Line(points=[self.center_x, self.center_y, self.center_x+0.8*self.r*sin(pi/30*time.second), self.center_y+0.8*self.r*cos(pi/30*time.second)], width=1, cap="round")
                    Color(0.0, 0.0, 0.0)
                    Line(points=[self.center_x, self.center_y, self.center_x+0.7*self.r*sin(pi/30*time.minute), self.center_y+0.7*self.r*cos(pi/30*time.minute)], width=2, cap="round")
                    Color(0.0, 0.0, 0.0)
                    th = time.hour*60 + time.minute
                    Line(points=[self.center_x, self.center_y, self.center_x+0.5*self.r*sin(pi/360*th), self.center_y+0.5*self.r*cos(pi/360*th)], width=3, cap="round")



            if analog == 2:    #red hands for classic watch      
                Color(1.0, 0.0, 0.0, 0.9)
                Line(points=[x, y, x+0.8*self.r*sin(pi/30*time.second), y+0.8*self.r*cos(pi/30*time.second)], width=1, cap="round")
                Color(1.0, 0.0, 0.0, 0.8)
                Line(points=[x, y, x+0.7*self.r*sin(pi/30*time.minute), y+0.7*self.r*cos(pi/30*time.minute)], width=2, cap="round")
                Color(1.0, 0.0, 0.0, 0.7)
                th = time.hour*60 + time.minute
                Line(points=[x, y, x+0.5*self.r*sin(pi/360*th), y+0.5*self.r*cos(pi/360*th)], width=3, cap="round")
 
            if analog == 3:     #hands for sport watch    
                Color(1.0, 0.0, 0.0, 0.9)
                Line(points=[x, y, x+0.8*self.r*sin(pi/30*time.second), y+0.8*self.r*cos(pi/30*time.second)], width=1, cap="round")
                Color(1.0, 0.0, 0.0, 0.8)
                Line(points=[x, y, x+0.7*self.r*sin(pi/30*time.minute), y+0.7*self.r*cos(pi/30*time.minute)], width=2, cap="round")
                Color(1.0, 0.0, 0.0, 0.7)
                th = time.hour*60 + time.minute
                Line(points=[x, y, x+0.5*self.r*sin(pi/360*th), y+0.5*self.r*cos(pi/360*th)], width=3, cap="round")

            if analog == 4:    #black hands for executive watch        
                Color(0.0, 0.0, 0.0, 0.9)
                Line(points=[x, y, x+0.8*self.r*sin(pi/30*time.second), y+0.8*self.r*cos(pi/30*time.second)], width=1, cap="round")
                Color(0.0, 0.0, 0.0, 0.8)
                Line(points=[x, y, x+0.7*self.r*sin(pi/30*time.minute), y+0.7*self.r*cos(pi/30*time.minute)], width=2, cap="round")
                Color(0.0, 0.0, 0.0, 0.7)
                th = time.hour*60 + time.minute
                Line(points=[x, y, x+0.5*self.r*sin(pi/360*th), y+0.5*self.r*cos(pi/360*th)], width=3, cap="round")


class MyClockWidget(FloatLayout):
    Ticks = Ticks()

    pass



#____________________________________________________________________
        #Build KV files


KVFILE = Builder.load_file("main.kv")
CLOCKKVFILE = Builder.load_file("clock.kv")

#_________________________________________________________________
        #MAIN APP
        

class MainApp(App):
    def build(self):
        global root
        root = ROOT() #set root widget (does nothing)
        
        
        clockwidget = CLOCK() #sets clock widget
        messagewidget = MESSAGE() #sets the message widget
        analogclock = MyClockWidget() #sets the analog clock widget
        cabintempwidget = CabinTempWidget() #sets the temp widget in upper right corner on main screen

        
       
        Clock.schedule_interval(clockwidget.update, .1) #updates the main menu clock

        Clock.schedule_interval(analogclock.ticks.update_clock, .1) #updates the analog clock

        Clock.schedule_interval(messagewidget.update, .104556) #updates the message display

        #Clock.schedule_once(cabintempwidget.update) #call once to get initial temp
        Clock.schedule_interval(cabintempwidget.update, .1) #updates the temp every minute
        
        #add the widgets
        
        root.add_widget(KVFILE) #adds the main GUI
        
        root.add_widget(clockwidget) #main digital clock
        root.add_widget(analogclock) #analog clock
        root.add_widget(messagewidget) #adds message widget

        root.add_widget(cabintempwidget) #adds temp widget

        return root


#SCHEDUALING

        #AUDIO

    def seekup_callback_schedge(obj):
        Clock.schedule_once(seekup_callback)
        Clock.schedule_once(seekup_callback, 0.1) #on for .1 secs, then off again

    def seekdown_callback_schedge(obj):
        Clock.schedule_once(seekdown_callback) 
        Clock.schedule_once(seekdown_callback, 0.1) #on for .1 secs, then off again

    def aux_callback_schedge(obj):
        Clock.schedule_once(aux_callback)
        Clock.schedule_once(aux_callback, 0.1) #on for .1 secs, then off again

    def amfm_callback_schedge(obj):
        Clock.schedule_once(amfm_callback) 
        Clock.schedule_once(amfm_callback, 0.1) #on for .1 secs, then off again

        #CONTROLS

    def garage_callback_schedge(obj):
        Clock.schedule_once(garage_callback) #called once - setup to only activate when button is down

    def radar_callback_schedge(obj):
        Clock.schedule_once(radar_callback) #called once so next press alternates status

    def leds_callback_schedge(obj):
        Clock.schedule_once(leds_callback) #called once so next press alternates status

    def windowsup_callback_schedge(obj):
        global WINDOWSUPON
        global WINDOWSDOWNON
        if WINDOWSDOWNON == 0: #only works when windows down isnt running
            Clock.schedule_once(windowsup_callback) #called once so next press alternates status
            Clock.schedule_once(windowsupOFF_callback, windowuptime) #on for set x secs, then off again - time needs edited
            return
        if WINDOWSUPON == 1:
            Clock.schedule_once(windowsupOFF_callback) #if windows going up while pushed, will cancel and stop windows


    def windowsdown_callback_schedge(obj):
        global WINDOWSUPON
        global WINDOWSDOWNON
        if WINDOWSUPON == 0: #only works when windows up isnt running
            Clock.schedule_once(windowsdown_callback) #called once so next press alternates status
            Clock.schedule_once(windowsdownOFF_callback, windowdowntime) #on for set x secs, then off again - time needs edited
            return
        if WINDOWSDOWNON == 1:
            Clock.schedule_once(windowsdownOFF_callback) #if windows going down while pushed, will cancel and stop windows

#VARIBLE SETTINGS
        
    def kill_clock(obj): #use on_release: app.kill_clock() to call
        global clock
        clock = 0
    def add_clock(obj): #use on_release: app.add_clock() to call
        global clock
        clock = 1
    def add_infosizeclock(obj): #use on_release: app.add_infosizeclock() to call
        global clock
        clock = 2

    def kill_analog(obj): #use on_release: app.kill_analog() to call
        global analog
        analog = 0
    def add_analog(obj): #use on_release: app.add_analog() to call
        global analog
        analog = 1
    def add_classicanalog(obj): #use on_release: app.add_classicanalog() to call
        global analog
        analog = 2
    def add_sportanalog(obj): #use on_release: app.add_sportanalog() to call
        global analog
        analog = 3
    def add_executiveanalog(obj): #use on_release: app.add_executiveanalog() to call
        global analog
        analog = 4
        
       
    def kill_message(obj): #use on_release: app.kill_message() to call
        global message
        message = 0
        
    def add_message_temp(obj): #use on_release: app.add_message_temp() to call
        global message
        message = 1

    def add_message_stopwatch(obj): #use on_release: app.add_message_stopwatch() to call
        global message
        message = 2

    def add_message_infoclock(obj): #use on_release: app.add_message_infoclock() to call
        global message
        message = 3

    def add_message_hotkeystrings(obj): #use on_release: app.add_message_hotkeystrings() to call
        global message
        message = 4

    def add_message_radarstatus(obj): #use on_release: app.add_message_radarstatus() to call
        global message
        message = 5
        
        
    #stopwatch button functions
    def stopwatch_start(obj): #use on_release: app.stopwatch_start() to call
        global swactive
        swactive = 1
    def stopwatch_stop(obj): #use on_release: app.stopwatch_start() to call
        global swactive
        swactive = 0
    def stopwatch_reset(obj): #use on_release: app.stopwatch_start() to call
        global swactive
        global swminute
        global swsecond
        global swtenth
        swactive = 0
        swminute = 0
        swsecond = 0
        swtenth = 0

    #hot key 1 settings functions
    def sethotkey1_SeekUp(obj):
        global hotkey1string
        hotkey1string = "Seek Up"
        #SettingsScreen.hotkey1label.text = "hello"
    def sethotkey1_SeekDown(obj):
        global hotkey1string
        hotkey1string = "Seek Down"
    def sethotkey1_Garage(obj):
        global hotkey1string
        hotkey1string = "Garage"
    def sethotkey1_Radar(obj):
        global hotkey1string
        hotkey1string = "Radar"
    def sethotkey1_CupLights(obj):
        global hotkey1string
        hotkey1string = "Cup Lights"
    def sethotkey1_WindowsUp(obj):
        global hotkey1string
        hotkey1string = "Windows Up"
    def sethotkey1_WindowsDown(obj):
        global hotkey1string
        hotkey1string = "Windows Down"
    def sethotkey1_ScreenToggle(obj):
        global hotkey1string
        hotkey1string = "Screen Toggle"
    def sethotkey1_None(obj):
        global hotkey1string
        hotkey1string = "None"

    #hot key 2 settings functions
    def sethotkey2_SeekUp(obj):
        global hotkey2string
        hotkey2string = "Seek Up"
    def sethotkey2_SeekDown(obj):
        global hotkey2string
        hotkey2string = "Seek Down"
    def sethotkey2_Garage(obj):
        global hotkey2string
        hotkey2string = "Garage"
    def sethotkey2_Radar(obj):
        global hotkey2string
        hotkey2string = "Radar"
    def sethotkey2_CupLights(obj):
        global hotkey2string
        hotkey2string = "Cup Lights"
    def sethotkey2_WindowsUp(obj):
        global hotkey2string
        hotkey2string = "Windows Up"
    def sethotkey2_WindowsDown(obj):
        global hotkey2string
        hotkey2string = "Windows Down"
    def sethotkey2_ScreenToggle(obj):
        global hotkey2string
        hotkey2string = "Screen Toggle"
    def sethotkey2_None(obj):
        global hotkey2string
        hotkey2string = "None"

        

    def shutdown(obj):
        os.system("sudo echo 1 > /sys/class/backlight/rpi_backlight/bl_power") #turns screen off
        os.system("sudo shutdown -h now")

    def reboot(obj):
        os.system("sudo reboot")


    def TurnScreenOn(obj):
        global screenon
        screenon = 1
        os.system("sudo echo 0 > /sys/class/backlight/rpi_backlight/bl_power") #turns screen on

    def TurnScreenOff(obj):
        global screenon
        screenon = 0
        os.system("sudo echo 1 > /sys/class/backlight/rpi_backlight/bl_power") #turns screen off
        
    def changeclocktheme(obj): #themes: Green(1), Blue(2), Red(3), Orange(4), DarkGrey(5), WhiteRed(6), Black(off)(7)
        global clocktheme
        if clocktheme < 8:
            clocktheme += 1
        if clocktheme == 8:
            clocktheme = 1

    def toggletemp(obj): #when called this toggles the main screen temp on and off
        #it does not change dynamically, but is set when button is pressed
        #off by default - press upper right main screen for display
        global TEMPON
        global temp_f_string
        if TEMPON == 1:
            TEMPON = 0
            temp_f_string = " "
            return
        if TEMPON == 0:
            TEMPON = 1
            read_temp()
            return

    def killtemp(obj): #used to kill the temp label when on screens other than main
        global TEMPON
        TEMPON = 0

#____________________________________________________________________
        #GPIO CALLBACKS

        #AUDIO
def seekup_callback(obj): #logic for seekup gpio
    global SEEKUPON
    if SEEKUPON == 0:
        GPIO.output(seekupPin, GPIO.LOW)
        GPIO.output(seekdownPin, GPIO.HIGH)
        SEEKUPON = 1
    else:
        GPIO.output(seekupPin, GPIO.HIGH)
        SEEKUPON = 0

def seekdown_callback(obj): #logic for seekdown gpio
    global SEEKDOWNON
    if SEEKDOWNON == 0:
        GPIO.output(seekdownPin, GPIO.LOW)
        GPIO.output(seekupPin, GPIO.HIGH)
        SEEKDOWNON = 1
    else:
        GPIO.output(seekdownPin, GPIO.HIGH)
        SEEKDOWNON = 0

def aux_callback(obj): #logic for aux gpio
    global AUXON
    if AUXON == 0:
        GPIO.output(auxPin, GPIO.LOW)
        AUXON = 1
    else:
        GPIO.output(auxPin, GPIO.HIGH)
        AUXON = 0

def amfm_callback(obj): #logic for amfm gpio
    global AMFMON
    if AMFMON == 0:
        GPIO.output(amfmPin, GPIO.LOW)
        AMFMON = 1
    else:
        GPIO.output(amfmPin, GPIO.HIGH)
        AMFMON = 0

        #CONTROLS

def garage_callback(obj): #logic for garage gpio
    global GARAGEON
    if GARAGEON == 0:
        GPIO.output(garagePin, GPIO.LOW)
        GARAGEON = 1
    else:
        GPIO.output(garagePin, GPIO.HIGH)
        GARAGEON = 0

def radar_callback(obj): #logic for radar gpio
    global RADARON
    if RADARON == 0:
        GPIO.output(radarPin, GPIO.LOW)
        RADARON = 1
    else:
        GPIO.output(radarPin, GPIO.HIGH)
        RADARON = 0

def leds_callback(obj): #logic for cup holder leds gpio
    global LEDSON
    if LEDSON == 0:
        GPIO.output(ledsPin, GPIO.HIGH)
        LEDSON = 1
    else:
        GPIO.output(ledsPin, GPIO.LOW)
        LEDSON = 0

def windowsup_callback(obj): #logic for windows up gpio
    global WINDOWSUPON
    global WINDOWSDOWNON
    
    if WINDOWSDOWNON == 0:
        
        if WINDOWSUPON == 0:
            GPIO.output(driverwindowupPin, GPIO.LOW)
            GPIO.output(passwindowupPin, GPIO.LOW)
            WINDOWSUPON = 1
            return
        if WINDOWSUPON == 1:
            GPIO.output(driverwindowupPin, GPIO.HIGH)
            GPIO.output(passwindowupPin, GPIO.HIGH)
            WINDOWSUPON = 0
            return

        
def windowsupOFF_callback(obj): #logic to halt the windows
    global WINDOWSUPON
    global WINDOWSDOWNON
    WINDOWSUPON = 0
    GPIO.output(driverwindowupPin, GPIO.HIGH)
    GPIO.output(passwindowupPin, GPIO.HIGH)

def windowsdown_callback(obj): #logic for windows down gpio
    global WINDOWSDOWNON
    global WINDOWSUPON
    
    if WINDOWSUPON == 0:
        
        if WINDOWSDOWNON == 0:
            GPIO.output(driverwindowdownPin, GPIO.LOW)
            GPIO.output(passwindowdownPin, GPIO.LOW)
            WINDOWSDOWNON = 1
            return
        if WINDOWSDOWNON == 1:
            GPIO.output(driverwindowdownPin, GPIO.HIGH)
            GPIO.output(passwindowdownPin, GPIO.HIGH)
            WINDOWSDOWNON = 0
            return

        
def windowsdownOFF_callback(obj): #logic to halt the windows
    global WINDOWSDOWNON
    global WINDOWSUPON
    WINDOWSDOWNON = 0
    GPIO.output(driverwindowdownPin, GPIO.HIGH)
    GPIO.output(passwindowdownPin, GPIO.HIGH)           
    
#_______________________________________________________________

if __name__ =='__main__':
    MainApp().run()

