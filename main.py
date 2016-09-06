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
from kivy.uix.switch import Switch
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
from kivy.uix.scatter import Scatter
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.carousel import Carousel
from kivy.uix.image import AsyncImage


import RPi.GPIO as GPIO
import sys
import datetime
import time
import os
import subprocess
import glob
import math
import obd
import serial

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


HotKey1Pin = 12
HotKey2Pin = 6

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

global TempProbePresent #1 if temp probe is connected, 0 if not
TempProbePresent = 0

if TempProbePresent == 1:
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')
 
    base_dir = '/sys/bus/w1/devices/'
    device_folder = glob.glob(base_dir + '28*')[0]
    device_file = device_folder + '/w1_slave'

global temp_f #make this var global for use in messages
temp_f = 0

global TEMPON #var for displaying cabin temp widget
TEMPON = 0


global OBDON #var for displaying obd gauges 
OBDVAR = 0
#0 - OFF
#1 - Digital Speed
#2 - Digital Tach
#3 - Graphic
#4 - Coolant Temp
#5 - Intake Temp
#6 - Engine Load

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

# window debug vars
global DRIVERUPON
DRIVERUPON = 0
global DRIVERDOWNON
DRIVERDOWNON = 0
global PASSENGERUPON
PASSENGERUPON = 0
global PASSENGERDOWNON
PASSENGERDOWNON = 0

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
hotkey1string = "None"

global hotkey2string
hotkey2string = "None"

global screenon
screenon = 1

global windowuptime #time it takes front windows to rise
windowuptime = 7

global windowdowntime #time it takes front windows to open
windowdowntime = 6

global clocktheme
clocktheme = 2

global launch_start_time
launch_start_time = 0

global animation_start_time
animation_start_time = 0

global time_second_mod
time_second_mod = 0

#OBD Global vars
global OBDconnection

global OBDconnection
OBDconnection = 0 #connection is off by default

global cmd_RPM
global cmd_SPEED
global cmd_CoolantTemp
global cmd_IntakeTemp
global cmd_Load

global maxRPM
maxRPM = 0

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
class DayGaugeClockScreen(Screen):
    pass
class NightGaugeClockScreen(Screen):
    pass
class WormsClockScreen(Screen):
    pass
class InfoClockScreen(Screen):
    pass
class PhotoClockScreen(Screen):
    pass
class TestAppScreen(Screen):
    pass

class GPSScreen(Screen):
    pass

class StopwatchScreen(Screen):
    pass

class DiagnosticsScreen(Screen):
    pass

class SystemDebugScreen(Screen):
    pass
class WindowDebugScreen(Screen):
    pass

class LaunchControlSetupScreen(Screen):
    pass
class LaunchControlScreen(Screen):
    pass

class PhotosScreen(Screen):
    pass

class GaugeSelectScreen(Screen):
    pass
class OBDDigitalSpeedoScreen(Screen):
    pass
class OBDDigitalTachScreen(Screen):
    pass
class OBDGraphicTachScreen(Screen):
    pass
class OBDCoolantScreen(Screen):
    pass
class OBDIntakeTempScreen(Screen):
    pass
class OBDLoadScreen(Screen):
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
        
        global time_second_mod
        time_second_mod = int(float(time_second_mod))+1
        if time_second_mod > 10000000: #doesnt allow this var to get too big
            time_second_mod = 0

        time_now = time_hour+":"+time_minute #create sting format (hour:minute)

        if clock == 1: #default - on main screens - top center
            self.font_size = 40 #50 for center
            self.pos = (345, 216) #0, 200 for center
            self.text = time_now
            
        if clock == 0: #shows nothing
            self.font_size = 60
            self.pos = (0,190)
            self.text = " "

        if clock == 2: #top left - larger - for info clock
            self.font_size = 140
            self.text = time_now
            self.pos = (-200,150)

        if clock == 3: #center - for worm clock
            self.font_size = 60
            self.pos = (0,36)
            self.text = time_now

        if clock == 4: #top right - for menu screens
            self.font_size = 40 #40
            self.pos = (345, 216) #212
            self.text = time_now
          

        #VARIABLE PRINTER
            #to use - comment out the normal clock == 1 if, and choose a type of var and uncomment

        #if clock == 1:
            #self.font_size = 30
            #self.pos = (0,190)
            #self.text = "%d" %time.hour #+ "%d" %WINDOWSDOWNON #for numbers
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
            self.pos = (0,70)
            #self.color = (1.0, 1.0, 1.0)
            
        if message == 3: # used for displaying the date on the info clock page
            self.text = dateinfo
            self.font_size = 60
            self.pos = (0,0)
            #self.color = (1.0, 1.0, 1.0)

        if message == 4:  #used for displaying the set hotkey labels

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
            self.pos = (270,245)


            
class CabinTempWidget(Label): #Cabin Temperature class - will display cabin temp in F on main screen only
    
    def update(self, *args):

        global clocktheme

        temp_f_string = str(temp_f)

        if int(float(animation_start_time))+5 <= int(float(time_second_mod)): #animation is delayed for better asthetics       
            if TEMPON == 1:
                if clocktheme == 2: # if analog clock is black, temp display is updated dynamically
                    #comment out next line for dev work - no temp sensor connected
                    if TempProbePresent == 1:
                            read_temp()     # If clock is shown, it goes really slow when updated dynamically
                            self.text = temp_f_string + u'\N{DEGREE SIGN}'
                    if TempProbePresent == 0:
                            self.text = "--" + u'\N{DEGREE SIGN}'
                if clocktheme != 2:
                    self.text = " "
            if TEMPON == 0: 
                self.text = " "
        self.font_size = 30
        self.pos = (354,140)

class OBDGaugeWidget(Label): #OBD Gauge class - will update and display obd data
    
    def update(self, *args):

        global clocktheme
        global response_RPM_int_adjusted
        global response_SPEED_int_adjusted
        global maxRPM
        global animation_time_start
       

              #comment out next section between breaks for dev work - no OBD connected
        #_____________________________________________________________________________________
        if int(float(animation_start_time))+5 <= int(float(time_second_mod)): #animation is delayed for better asthetics
            
            if OBDVAR == 0: #code for no OBD stuff
                self.text = " "

            if OBDVAR == 1: #code for OBD Digital Speedo
                response_SPEED = connection.query(cmd_SPEED) # send the command, and parse the response
                    
                response_SPEED_string = str(response_SPEED.value) #change value into a string for comparing to "None"
                    
                if response_SPEED_string != 'None': #only proceed if string value is not None

                    response_SPEED_int = int(response_SPEED.value) #change the var type to int

                    if response_SPEED_int == 0: #to avoid the formula
                        response_SPEED_int_adjusted = 0
                        self.text = "0"
                            
                    if response_SPEED_int == 1: #to avoid the formula
                        response_SPEED_int_adjusted = 1
                        self.text = "1"
                            
                    if response_SPEED_int == 2: #to avoid the formula
                        response_SPEED_int_adjusted = 1
                        self.text = "1"

                    if response_SPEED_int > 2: #start to apply the formula to speed
                        response_SPEED_int_adjusted = math.floor(((response_SPEED_int)*(.6278))-.664) #adjusts number according to formula and rounds down to nearesr whole MPH - sets new adjusted int
                        response_SPEED_string_adjusted = str(response_SPEED_int_adjusted) #sets string
                        self.text = response_SPEED_string_adjusted.strip()[:-2] #set text

            if OBDVAR == 2: #code for OBD Digital Tach
                response_RPM = connection.query(cmd_RPM) # send the command, and parse the response
                    
                response_RPM_string = str(response_RPM.value) #change value into a string for comparing to "None"
                    
                if response_RPM_string != 'None': #only proceed if string value is not None

                    response_RPM_int = int(response_RPM.value) #set int value
                    response_RPM_int_adjusted = math.floor(response_RPM_int) #round down to nearest whole RPM
                    if response_RPM_int_adjusted > maxRPM:
                        maxRPM = response_RPM_int_adjusted
                    maxRPM_string = str(maxRPM)
                    maxRPM_string = maxRPM_string.strip()[:-2] #strip .0 at the end of string
                    response_RPM_string = str(response_RPM_int_adjusted) # set string value
                    response_RPM_string = response_RPM_string.strip()[:-2] #strip .0 at the end of string
                    self.text = response_RPM_string + '\n' + maxRPM_string #set text - testing max RPM

            if OBDVAR == 3: #code for OBD graphical Tach
                self.text = " "
                global analog
                analog = 8


            if OBDVAR == 4: #code for OBD Coolant Temp
                response_CoolantTemp = connection.query(cmd_CoolantTemp) # send the command, and parse the response
                    
                response_CoolantTemp_string = str(response_CoolantTemp.value) #change value into a string for comparing to "None"
                    
                if response_CoolantTemp_string != 'None': #only proceed if string value is not None

                    response_CoolantTemp_int = int(response_CoolantTemp.value)* 9.0 / 5.0 + 32.0 #set int value - change to farenheit
                    response_CoolantTemp_int_adjusted = math.floor(response_CoolantTemp_int) #round down to nearest whole RPM
                    response_CoolantTemp_string = str(response_CoolantTemp_int_adjusted) # set string value
                    response_CoolantTemp_string = response_CoolantTemp_string.strip()[:-2] #strip .0 at the end of string
                    self.text = response_CoolantTemp_string + u'\N{DEGREE SIGN}'#set text

            if OBDVAR == 5: #code for OBD Intake Temp
                response_IntakeTemp = connection.query(cmd_IntakeTemp) # send the command, and parse the response
                    
                response_IntakeTemp_string = str(response_IntakeTemp.value) #change value into a string for comparing to "None"
                    
                if response_IntakeTemp_string != 'None': #only proceed if string value is not None

                    response_IntakeTemp_int = int(response_IntakeTemp.value)* 9.0 / 5.0 + 32.0 #set int value - change to farenheit
                    response_IntakeTemp_int_adjusted = math.floor(response_IntakeTemp_int) #round down to nearest whole RPM
                    response_IntakeTemp_string = str(response_IntakeTemp_int_adjusted) # set string value
                    response_IntakeTemp_string = response_IntakeTemp_string.strip()[:-2] #strip .0 at the end of string
                    self.text = response_IntakeTemp_string + u'\N{DEGREE SIGN}'#set text
                    
            if OBDVAR == 6: #code for OBD Engine Load
                response_Load = connection.query(cmd_Load) # send the command, and parse the response
                    
                response_Load_string = str(response_Load.value) #change value into a string for comparing to "None"
                    
                if response_Load_string != 'None': #only proceed if string value is not None

                    response_Load_int = int(response_Load.value)*2 + 20 #set int value - set to lb-ft + 20 for fun
                    response_Load_int_adjusted = math.floor(response_Load_int) #round down to nearest whole RPM
                    response_Load_string = str(response_Load_int_adjusted) # set string value
                    response_Load_string = response_Load_string.strip()[:-2] #strip .0 at the end of string
                    self.text = response_Load_string + ' lb-ft'#set text

        self.font_size = 100
        self.pos = (0,0)
        
        #_____________________________________________________________________________________
            
        

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
        global launch_time_start
        global time_second
        global response_RPM_int_adjusted
        
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

            if analog == 1: #stock Red analog clock on mainscreen(default), theme can be changed by tapping clock 
                if clocktheme == 1: #Red
                    Color(0.714, 0.11, 0.11) #seconds
                    Line(points=[self.center_x, self.center_y, self.center_x+0.8*self.r*sin(pi/30*time.second), self.center_y+0.8*self.r*cos(pi/30*time.second)], width=1, cap="round")
                    Color(0.773, 0.156, 0.156) #minutes
                    Line(points=[self.center_x, self.center_y, self.center_x+0.7*self.r*sin(pi/30*time.minute), self.center_y+0.7*self.r*cos(pi/30*time.minute)], width=2, cap="round")
                    Color(0.824, 0.184, 0.184) #hours
                    th = time.hour*60 + time.minute
                    Line(points=[self.center_x, self.center_y, self.center_x+0.5*self.r*sin(pi/360*th), self.center_y+0.5*self.r*cos(pi/360*th)], width=3, cap="round")
                    

                if clocktheme == 2: #Black
                    Color(0.2, 0.5, 0.2, 0.0)
                    Line(points=[self.center_x, self.center_y, self.center_x+0.8*self.r*sin(pi/30*time.second), self.center_y+0.8*self.r*cos(pi/30*time.second)], width=1, cap="round")
                    Color(0.3, 0.6, 0.3, 0.0)
                    Line(points=[self.center_x, self.center_y, self.center_x+0.7*self.r*sin(pi/30*time.minute), self.center_y+0.7*self.r*cos(pi/30*time.minute)], width=2, cap="round")
                    Color(0.4, 0.7, 0.4, 0.0)
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
 
            if analog == 3:     #red hands for sport watch    
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

            if analog == 5:    #red longer hands for gauge watch        
                Color(1.0, 0.0, 0.0, 0.9)
                Line(points=[x, y, x+0.8*self.r*sin(pi/30*time.second), y+0.8*self.r*cos(pi/30*time.second)], width=1, cap="round")
                Color(1.0, 0.0, 0.0, 0.8)
                Line(points=[x, y, x+0.7*self.r*sin(pi/30*time.minute), y+0.7*self.r*cos(pi/30*time.minute)], width=2, cap="round")
                Color(1.0, 0.0, 0.0, 0.7)
                th = time.hour*60 + time.minute
                Line(points=[x, y, x+0.5*self.r*sin(pi/360*th), y+0.5*self.r*cos(pi/360*th)], width=3, cap="round")

            if analog == 6:    #circular worm hands - custom clock by Joel Zeller       
                Color(1.0, 0.0, 0.0, 0.9)
                Line(circle=(x, y, 170, 0, self.r*time.second/30), width=10)
                Color(0.0, 1.0, 0.0, 0.8)
                Line(circle=(x, y, 140, 0, self.r*time.minute/30), width=10)
                Color(0.0, 0.0, 1.0, 0.7)
                time_hour_mod = time.hour
                if time.hour > 12:
                    time_hour_mod = time.hour-12
                Line(circle=(x, y, 110, 0, self.r*time_hour_mod/6), width=10)

            if analog == 7:    #clock used for launch control animation

                #pre-stage dots
                if int(float(launch_start_time))+30 <= int(float(time_second_mod)):
                                                # this is in miliseconds
                    Color(1.0, 1.0, 0.4, 0.2)
                    Line(circle=(x-70, y+155, 0, 0, 0), width=25)
                    Line(circle=(x-70+20, y+155, 0, 0, 0), width=25)
                if int(float(launch_start_time))+50 <= int(float(time_second_mod)):
                    Color(1.0, 1.0, 0.4, 0.2)
                    Line(circle=(x+40, y+155, 0, 0, 0), width=25)
                    Line(circle=(x+40+20, y+155, 0, 0, 0), width=25)

                #stage dots 
                if int(float(launch_start_time))+70 <= int(float(time_second_mod)):
                                                # this is in miliseconds
                    Color(1.0, 1.0, 0.4, 0.2)
                    Line(circle=(x-70, y+90, 0, 0, 0), width=25)
                    Line(circle=(x-70+20, y+90, 0, 0, 0), width=25)
                if int(float(launch_start_time))+90 <= int(float(time_second_mod)):
                    Color(1.0, 1.0, 0.4, 0.2)
                    Line(circle=(x+40, y+90, 0, 0, 0), width=25)
                    Line(circle=(x+40+20, y+90, 0, 0, 0), width=25)

                #first row
                if int(float(launch_start_time))+100 <= int(float(time_second_mod)):
                    Color(1.0, 1.0, 0.4, 0.2)
                    Line(circle=(x-70, y+45, 0, 0, 0), width=50)
                    Line(circle=(x+70, y+45, 0, 0, 0), width=50)

                #second row
                if int(float(launch_start_time))+105 <= int(float(time_second_mod)):
                    Color(1.0, 1.0, 0.4, 0.2)
                    Line(circle=(x-71, y-20, 0, 0, 0), width=52)
                    Line(circle=(x+70, y-20, 0, 0, 0), width=52)

                #third row
                if int(float(launch_start_time))+110 <= int(float(time_second_mod)):
                    Color(1.0, 1.0, 0.4, 0.2)
                    Line(circle=(x-73, y-85, 0, 0, 0), width=54)
                    Line(circle=(x+70, y-85, 0, 0, 0), width=54)

                #GO
                if int(float(launch_start_time))+115 <= int(float(time_second_mod)):
                    Color(0.1, 0.9, 0.1, 0.3)
                    Line(circle=(x-79, y-160, 0, 0, 0), width=60)
                    Line(circle=(x+70, y-160, 0, 0, 0), width=60)

                    Line(circle=(x-400, y+204, 0, 0, 0), width=300)
                    Line(circle=(x+400, y+204, 0, 0, 0), width=300)
                    GPIO.output(ledsPin, GPIO.HIGH)

                #Turn off LEDS
                if int(float(launch_start_time))+200 <= int(float(time_second_mod)):
                    GPIO.output(ledsPin, GPIO.LOW)    


            if analog == 8: #Race tach - graphical tach in OBD gauges screen
                response_RPM = connection.query(cmd_RPM) # send the command, and parse the response
                
                response_RPM_string = str(response_RPM.value) #change value into a string for comparing to "None"
                
                if response_RPM_string != 'None': #only proceed if string value is not None

                    response_RPM_int = int(response_RPM.value) #set int value
                    response_RPM_int_adjusted = math.floor(response_RPM_int) #round down to nearest whole RPM
                    response_RPM_string = str(response_RPM_int_adjusted) # set string value
                    response_RPM_string = response_RPM_string.strip()[:-2] #string .0 at the end of string
                    self.text = response_RPM_string #set text
                    
                RPM_CUR = response_RPM_int_adjusted
                Color(0.8, 0.0, 0.0)
                Line(points=[self.center_x, y, self.center_x+0.95*(self.r*sin((pi/5000*RPM_CUR)+pi)), y+0.95*(self.r*cos((pi/5000*RPM_CUR)+pi))], width=3, cap="round")
                Color(0.0, 0.0, 0.0)
                Line(points=[self.center_x, y, self.center_x+0.15*(self.r*sin((pi/5000*RPM_CUR)+pi)), y+0.15*(self.r*cos((pi/5000*RPM_CUR)+pi))], width=6, cap="round")
                Line(points=[self.center_x, y, self.center_x-0.15*(self.r*sin((pi/5000*RPM_CUR)+pi)), y-0.15*(self.r*cos((pi/5000*RPM_CUR)+pi))], width=6, cap="round")
                if response_RPM_int_adjusted > 3500: #REDLINE SET - to be changed into changable variable
                #if 5000 > 4000:
                    Color(0.8, 0.0, 0.0)
                    Line(circle=[x-300, y, 0, 0, 0], width=50)

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
        obdgaugewidget = OBDGaugeWidget() #sets the gauge widget in the middle of the screen
        
       
        Clock.schedule_interval(clockwidget.update, .1) #updates the main menu clock

        Clock.schedule_interval(analogclock.ticks.update_clock, .1) #updates the analog clock

        Clock.schedule_interval(messagewidget.update, .104556) #updates the message display

        #Clock.schedule_once(cabintempwidget.update) #call once to get initial temp
        Clock.schedule_interval(cabintempwidget.update, .1) #updates the temp every 10th second

        Clock.schedule_interval(obdgaugewidget.update, .1) #updates the temp every 10th second
        
        #add the widgets
        
        root.add_widget(KVFILE) #adds the main GUI
        
        root.add_widget(clockwidget) #main digital clock
        root.add_widget(analogclock) #analog clock
        root.add_widget(messagewidget) #adds message widget

        root.add_widget(cabintempwidget) #adds temp widget
        root.add_widget(obdgaugewidget) #adds obd gauge widget

        return root
    
    def animate(self, instance):
        animation = Animation(pos=(100, 100), t='out_bounce')
        animation += Animation(pos=(200, 100), t='out_bounce')
        animation &= Animation(size=(500, 500))
        animation += Animation(size=(100, 50))

        animation.start(instance)

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

    # following 6 functions serve purpose to debug windows
    def driverup_callback_schedge(obj):
        Clock.schedule_once(driverup_callback) #called once - setup to only activate when button is down
    def driverstop_callback_schedge(obj):
        Clock.schedule_once(driverstop_callback) #called once - setup to only activate when button is down
    def driverdown_callback_schedge(obj):
        Clock.schedule_once(driverdown_callback) #called once - setup to only activate when button is down
    def passengerup_callback_schedge(obj):
        Clock.schedule_once(passengerup_callback) #called once - setup to only activate when button is down
    def passengerstop_callback_schedge(obj):
        Clock.schedule_once(passengerstop_callback) #called once - setup to only activate when button is down
    def passengerdown_callback_schedge(obj):
        Clock.schedule_once(passengerdown_callback) #called once - setup to only activate when button is down
    def allwindowsstop_callback_schedge(obj):
        Clock.schedule_once(allwindowsstop_callback) #called once - setup to only activate when button is down

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
    def add_wormsizeclock(obj): #use on_release: app.add_wormsizeclock() to call
        global clock
        clock = 3
    def add_menuclock(obj): #use on_release: app.add_menuclock() to call
        global clock
        clock = 4

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
    def add_daygaugeanalog(obj): #use on_release: app.add_daygaugeanalog() to call
        global analog
        analog = 5
    def add_nightgaugeanalog(obj): #use on_release: app.add_nightgaugeanalog() to call
        global analog
        analog = 5
    def add_wormanalog(obj): #use on_release: app.add_wormanalog() to call
        global analog
        analog = 6
    def add_launchanalog(obj): #use on_release: app.add_launchanalog() to call - used to create the lights on the xmas tree drag lights
        global analog
        global time_second_mod
        global launch_start_time
        analog = 7
        launch_start_time = int(float(time_second_mod)) #sets a reference time for launch control timing

    #OBD themes
    def add_graphicaltach(obj): #use on_release
        global analog
        analog = 8

        
       
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
        
    def changeclocktheme(obj): #themes: Green(1), Off(2) - flips thru screens when tapping home analog clock
        global clocktheme
        global animation_start_time
        #animation_start_time = int(float(time_second_mod)) #sets a reference time for animations
        if clocktheme < 3:
            clocktheme += 1
        if clocktheme == 2:
            animation_start_time = int(float(time_second_mod)) #sets a reference time for animations
        if clocktheme == 3:
            clocktheme = 1
        
    def toggletemp(obj): #when called this toggles the main screen temp on and off
        #it does not change dynamically, but is set when button is pressed
        #off by default - press upper right main screen for display
        global TEMPON
        global temp_f_string
        global TempProbePresent
        global animation_start_time
        if TEMPON == 1:
            TEMPON = 0
            temp_f_string = " "
            return
        if TEMPON == 0:
            animation_start_time = int(float(time_second_mod)) #sets a reference time for animations
            TEMPON = 1
            if TempProbePresent == 1:
                read_temp()
            return

    def killtemp(obj): #used to kill the temp label when on screens other than main
        global TEMPON
        TEMPON = 0

    def addtemp(obj): #used to kill the temp label when on screens other than main
        global TEMPON
        global animation_start_time
        TEMPON = 1
        animation_start_time = int(float(time_second_mod)) #sets a reference time for animations

    def connect_OBD(obj): #sets value to one so connection code only runs once
        global OBDconnection
        OBDconnection = 1

    def kill_OBDVAR(obj): #used to kill the OBD label when on screens other than main
        global OBDVAR
        OBDVAR = 0

    def add_OBDVAR_SPEED(obj): #used to change the OBD label to other types of data
        global OBDVAR
        global time_second_mod
        global animation_start_time
        OBDVAR = 1
        animation_start_time = int(float(time_second_mod)) #sets a reference time for animations
        
    def add_OBDVAR_RPM(obj): #used to change the OBD label to other types of data
        global OBDVAR
        global time_second_mod
        global animation_start_time
        OBDVAR = 2
        animation_start_time = int(float(time_second_mod)) #sets a reference time for animations
    def add_OBDVAR_GRAPHICAL_RPM(obj): #used to change the OBD label to other types of data
        global OBDVAR
        global time_second_mod
        global animation_start_time
        OBDVAR = 3
        animation_start_time = int(float(time_second_mod)) #sets a reference time for animations
    def add_OBDVAR_COOLANT_TEMP(obj): #used to change the OBD label to other types of data
        global OBDVAR
        global time_second_mod
        global animation_start_time
        OBDVAR = 4
        animation_start_time = int(float(time_second_mod)) #sets a reference time for animations
    def add_OBDVAR_INTAKE_TEMP(obj): #used to change the OBD label to other types of data
        global OBDVAR
        global time_second_mod
        global animation_start_time
        OBDVAR = 5
        animation_start_time = int(float(time_second_mod)) #sets a reference time for animations
    def add_OBDVAR_LOAD(obj): #used to change the OBD label to other types of data
        global OBDVAR
        global time_second_mod
        global animation_start_time
        OBDVAR = 6
        animation_start_time = int(float(time_second_mod)) #sets a reference time for animations

    #_________________________________________________________________

    #Function to setup OBD stuff
    def setup_OBD(obj):
        global connection
        global cmd_RPM
        global cmd_SPEED
        global cmd_CoolantTemp
        global cmd_IntakeTemp
        global cmd_Load
        global OBDconnection

        if OBDconnection == 0:
        
            os.system('sudo rfcomm bind /dev/rfcomm1 00:1D:A5:16:3E:ED')
            connection = obd.OBD() # auto-connects to USB or RF port

            cmd_RPM = obd.commands.RPM # select RPM OBD command (sensor)
            cmd_SPEED = obd.commands.SPEED # select SPEED OBD command (sensor)
            cmd_CoolantTemp = obd.commands.COOLANT_TEMP # select CoolantTemp OBD command (sensor)
            cmd_IntakeTemp = obd.commands.INTAKE_TEMP # select IntakeTemp OBD command (sensor)
            cmd_Load = obd.commands.ENGINE_LOAD # select EngineLoad OBD command (sensor)
    
    #_________________________________________________________________

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

    # callback functions for window debugging

def driverup_callback(obj): #logic for driver up gpio
    global DRIVERUPON
    if DRIVERUPON == 0:
        GPIO.output(driverwindowupPin, GPIO.LOW)
        DRIVERUPON = 1
    else:
        GPIO.output(driverwindowupPin, GPIO.HIGH)
        DRIVERUPON = 0

def driverstop_callback(obj): #logic for driver window emergency stop
    global WINDOWSDOWNON
    global WINDOWSUPON
    WINDOWSDOWNON = 0
    WINDOWSUPON = 0
    GPIO.output(driverwindowupPin, GPIO.HIGH)
    GPIO.output(driverwindowdownPin, GPIO.HIGH)

def driverdown_callback(obj): #logic for driver down gpio
    global DRIVERDOWNON
    if DRIVERDOWNON == 0:
        GPIO.output(driverwindowdownPin, GPIO.LOW)
        DRIVERDOWNON = 1
    else:
        GPIO.output(driverwindowdownPin, GPIO.HIGH)
        DRIVERDOWNON = 0

def passengerup_callback(obj): #logic for passenger up gpio
    global PASSENGERUPON
    if PASSENGERUPON == 0:
        GPIO.output(passwindowupPin, GPIO.LOW)
        PASSENGERUPON = 1
    else:
        GPIO.output(passwindowupPin, GPIO.HIGH)
        PASSENGERUPON = 0

def passengerstop_callback(obj): #logic for passenger window emergency stop
    global WINDOWSDOWNON
    global WINDOWSUPON
    WINDOWSDOWNON = 0
    WINDOWSUPON = 0
    GPIO.output(passwindowupPin, GPIO.HIGH)
    GPIO.output(passwindowdownPin, GPIO.HIGH)

def passengerdown_callback(obj): #logic for passenger down gpio
    global PASSENGERDOWNON
    if PASSENGERDOWNON == 0:
        GPIO.output(passwindowdownPin, GPIO.LOW)
        PASSENGERDOWNON = 1
    else:
        GPIO.output(passwindowdownPin, GPIO.HIGH)
        PASSENGERDOWNON = 0

def allwindowsstop_callback(obj): #logic for all windows emergency stop
    global WINDOWSDOWNON
    global WINDOWSUPON
    WINDOWSDOWNON = 0
    WINDOWSUPON = 0
    GPIO.output(passwindowupPin, GPIO.HIGH)
    GPIO.output(passwindowdownPin, GPIO.HIGH)
    GPIO.output(driverwindowupPin, GPIO.HIGH)
    GPIO.output(driverwindowdownPin, GPIO.HIGH)

    
#_______________________________________________________________

if __name__ =='__main__':
    MainApp().run()

