# CoPilot-InfotainmentSystem
Raspberry Pi Carputer Kivy Code

Usage:
***You will need clock.kv, main.kv, main.py, and the data folder placed in a directory on your pi - mine are located at /home/pi/CoPilot***

Setup to autorun on boot like I do or just run main.py

Recommended Hardware - 
 - Raspberry Pi 3
 - Real Time Clock
 - Temperature Probe
 - Bluetooth OBDII dongle for car (for use with performance pages)
 - Leds (Look in code for which GPIO is used)
 - Two push buttons for Hotkeys (Look in code for which GPIO is used)
 
 To view current temp:
 - Make sure "TempProbePresent" variable in code is set to 1 - if not, temp will be "--"
 - Tap under time on home screen and bubble will float unto screen showing temp - tap again to hide
 
 Email me at joelzeller25@hotmail.com with any questions :)
