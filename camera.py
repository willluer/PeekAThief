#!/usr/bin/python

#
# Feeder Tweeter (http://feedertweeter.net/)
# Copyright Manifold 2013+. All rights reserved.
# Author Chad Auld (cauld@wearemanifold.com)
# Licensed under the BSD License.
# https://bitbucket.org/cauld/feedertweeter/
#

'''
camera.py: 
This script handles the feeder's motion detection 
and image capturing.
'''

import os
import datetime
import time
import RPi.GPIO as GPIO

# GPIO Setup
# Avoid these, used by SleepyPi
#15 (GPIO 22)
#16 (GPIO 24)
#22 (GPIO 25)

GREEN_LED = 8
GREEN_RED = 10
GPIO_PIR = 23
GPIO_PHOTOCELL = 12
GPIO_PING_TRIGGER = 19
GPIO_PING_ECHO = 13
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(GREEN_LED, GPIO.OUT) # The green LED indicates the feeder is active
GPIO.setup(GPIO_PING_TRIGGER,GPIO.OUT)
GPIO.setup(GPIO_PING_ECHO,GPIO.IN)
GPIO.setup(GPIO_PIR, GPIO.IN)
GPIO.setup(GPIO_PHOTOCELL, GPIO.IN)

PING_MAX_TRIES = 50 # Used to break from the occasional PING sensor stall
PING_DISTANCE_TO_WALL = 14.0 # How far away is the primary target?
TIME_BETWEEN_MOTION_CHECKS = 60
STARTUP_MOTION_SKIPPED = False # Prevent false positives during init
FEEDERTWEETER_HOME_DIR = '/home/pi/feedertweeter/'
MIN_RCLIGHT_READING = 250 # Minimum acceptable light level

# Detects motion with the PIR sensor (this is the primary trigger)
def motionDetectedByPIR():
    if (GPIO.input(GPIO_PIR) == True):
        return True
    else:
        return False

'''
The PIR's motion detection mechanism is overly sensitive to changes in heat. We'll
use the PING sensor to double check the findings of PIR. PING is sensitive to wind
which is why we can't only use PING.
''' 
def motionDetectedByPing():
    response = False
    
    print "PIR detects motion, double checking with the PING sensor..."
    
    '''
    PING accuracy is just ok and sometimes triggers a false positive, but rarely
    ever triggers more that 1 in a row. Therefore, we want to see 2 triggers in a row
    before assuming there is actually movement.
    '''
    ping_motion_count = 0
    while (ping_motion_count < 2):
        d = calculateDistanceToWall()
        
        #print d

        '''
        The PING sensor stalls occasionally. A return signal is not caught.
        We force a break and treat as no motion detected and carry on...
        '''
        if (d > 0):
            if (d < PING_DISTANCE_TO_WALL):
                ping_motion_count = ping_motion_count + 1
                if (ping_motion_count == 2):
                    print "PING has confirmed motion..."
                    response = True
                    break
                else:
                    # Let the module setting for a moment after a positive result
                    time.sleep(0.5)
            else:
                print "PING doesn't agree, no motion..."
                response = False
                break
        else:
            # Leave the count alone, ignore this iteration and try again
            print "Sonar stalled, wait for next attempt..."
            
    return response

def takephoto():
    '''
    Write the file to the current directory and then move to captures dir when complete.
    There is a monitor on the captures dir and we don't want it grabbing the file before 
    the write is complete.
    '''
    fname = "photo_" + datetime.datetime.now().strftime("%m_%d_%Y_%H%M%S") + ".jpg"
    source = FEEDERTWEETER_HOME_DIR + fname
    destination = FEEDERTWEETER_HOME_DIR + 'captures/' + fname
    
    # Say cheese!
    os.system("raspistill -t 1000 -o " + source + " -n")
    os.rename(source, destination)
    
'''
Used to measure the distance to our primary target using the 
PING ultradistance sensor.

Credit: Matt Hawkins - http://goo.gl/nZUiYg
'''
def calculateDistanceToWall():
    # Send 10us pulse to trigger
    GPIO.output(GPIO_PING_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_PING_TRIGGER, False)
    start = time.time()
    stop = time.time()
    
    current_try=0
    
    while GPIO.input(GPIO_PING_ECHO)==0 and (current_try<PING_MAX_TRIES):
        current_try = current_try + 1
        start = time.time()

    while GPIO.input(GPIO_PING_ECHO)==1:
      stop = time.time()

    # Calculate pulse length
    elapsed = stop-start

    # Distance pulse travelled in that time is time
    # multiplied by the speed of sound (cm/s)
    distance = elapsed * 34000

    # That was the distance there and back so halve the value
    distance = distance / 2
    
    return distance
    
'''
Our photocell capacitor acts like a bucket and the resistor is like a thin pipe. 
To fill a bucket up with a very thin pipe takes enough time that you 
can figure out how wide the pipe is by timing how long it takes to 
fill the bucket up halfway.

Credit: Adafruit - http://goo.gl/A3geuW
'''
def RCtime():
    reading = 0
    GPIO.setup(GPIO_PHOTOCELL, GPIO.OUT)
    GPIO.output(GPIO_PHOTOCELL, GPIO.LOW)
    time.sleep(0.1)

    GPIO.setup(GPIO_PHOTOCELL, GPIO.IN)
    # This takes about 1 millisecond per loop cycle
    while (GPIO.input(GPIO_PHOTOCELL) == GPIO.LOW):
            reading += 1
    return reading

'''
Photocells (and therefore the RCtime method) are not super precision measurement devices.
The measurements vary slightly with each reading and sometimes reports a random low 
value. While not perfect, it is good enough for our purposes with a little help. To 
improve accuracy of the reading we take 6 sample RC time readings, toss the lowest, and 
avg the remaining 5. Alternatively you could use a digital lux sensor.
'''
def getAvgRCtime():
    readings = []
    
    i = 0
    for i in range(0,6):
        reading = RCtime()
        readings.append(reading)
        i += 1
        
    readings.remove(min(readings)) # Helps prevent random outliers
    avgReading = sum(readings) / float(len(readings))
    
    return avgReading

######## MAIN #########

GPIO.output(GREEN_LED, True) # Indicate the feeder is now active

while True:
    # We require confirmation of motion from 2 seperate sensors to work around false positives
    # noted in the project timeline - http://feedertweeter.net/about
    if (motionDetectedByPIR() == True and motionDetectedByPing() == True):
        if (STARTUP_MOTION_SKIPPED == False):
            # When first enabling motion detection it often sends an immediate detection 
            # signal, we can discard this
            STARTUP_MOTION_SKIPPED = True
        else:
            print "Motion detected, checking light levels..."
            
            # OK we do have confirmed motion, but do we have enough daylight for a good picture?
            avgRcReading = getAvgRCtime()
            if (avgRcReading <= MIN_RCLIGHT_READING):
                print "We have enough light, taking picture..."
                takephoto()
                print "Picture taken..."
            
                # We don't want a ton of pictures from the same bird so wait a while before checking again
                # and flush any activity triggered during that time
                print "Pausing motion detection..."
                time.sleep(TIME_BETWEEN_MOTION_CHECKS)
                print "Resuming motion detection..."
            else:
                print "Sorry, too dark for a good photo!"
    else:
        print "No motion detected"
        time.sleep(1)
