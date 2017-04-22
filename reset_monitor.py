#!/usr/bin/python

#
# Feeder Tweeter (http://feedertweeter.net/)
# Copyright Manifold 2013+. All rights reserved.
# Author Chad Auld (cauld@wearemanifold.com)
# Licensed under the BSD License.
# https://bitbucket.org/cauld/feedertweeter/
#

'''
reset_monitor.py: 
This script supports the external reboot/shutdown
button found on the exterior of the feeder's enclosure.
'''

import RPi.GPIO as GPIO
import time
import os

RED_LED = 10
SWITCH_PIN = 16
RESET_TIMER_COUNT = 0 # Tracks the button hold time

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(RED_LED, GPIO.OUT)
GPIO.setup(SWITCH_PIN, GPIO.IN)

def indicate_reset_command(flashcount):
    for x in range (0, flashcount):
        GPIO.output(RED_LED, True)
        time.sleep(.25)
        GPIO.output(RED_LED, False)
        time.sleep(.25)

def system_reboot():
    print "Reboot requested..."
    indicate_reset_command(3)
    os.system("sudo shutdown -r now")
    
def system_shutdown():
    print "Shutdown requested..."
    indicate_reset_command(5)
    os.system("sudo shutdown -hP now")
    
while True:
    if ( GPIO.input(SWITCH_PIN) == False ):
        # If they press and release we'll end up here
        if (RESET_TIMER_COUNT >= 0 and RESET_TIMER_COUNT < 2):
            # Anything less than 2 is just a bump so reset the counter
            RESET_TIMER_COUNT = 0
        elif (RESET_TIMER_COUNT >= 2 and RESET_TIMER_COUNT <= 4):
            # Short hold, do a reboot
            system_reboot()
            break
        else:
            # Long hold, do a shutdown
            system_shutdown()
            break
    else:
        RESET_TIMER_COUNT = RESET_TIMER_COUNT + 1
        
        # If they press and hold we'll end up here
        if (RESET_TIMER_COUNT >= 5):
            system_shutdown()
            break
    
    time.sleep(1)
