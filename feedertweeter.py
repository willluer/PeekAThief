#!/usr/bin/python
# coding=utf-8

#
# Feeder Tweeter (http://feedertweeter.net/)
# Copyright Manifold 2013+. All rights reserved.
# Author Chad Auld (cauld@wearemanifold.com)
# Licensed under the BSD License.
# https://bitbucket.org/cauld/feedertweeter/
#

'''
feedertweeter.py: 
This script watches for new bird pictures to be captured and 
then posts them to Twitter.
'''

import os
import time
from random import choice
from twython import Twython
from fsmonitor import FSMonitor

# Camera captures directory
CAMERA_CAPTURES_DIR = "/home/pi/feedertweeter/captures/"

# A variety of possible post message so we don't always repeat the same thing
POST_MESSAGES = ["It's feeding time!", "Chow's on!", "Bon appétit!", "Come and get it!", 
        "Seeds? Seeds AGAIN?", "Let's eat!", "Strapping on ye olde feedbag", 
        "A banquet awaits us, friend"]

# Get Twitter keys from the supervisord env
APP_KEY = os.getenv('FEEDERTWEETER_APP_KEY')
APP_SECRET = os.getenv('FEEDERTWEETER_APP_SECRET')
OAUTH_TOKEN = os.getenv('FEEDERTWEETER_OAUTH_TOKEN')
OAUTH_TOKEN_SECRET = os.getenv('FEEDERTWEETER_OAUTH_TOKEN_SECRET')

t = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

# Used to post status updates with bird images as new images are detected
def postNewMessage(fileName):
    print "Uploading new post with image..."
    fullFilePath = CAMERA_CAPTURES_DIR + fileName
    
    # Grab a random post message
    postmsg = choice(POST_MESSAGES)
    
    try:
        photo = photo = open(fullFilePath, 'rb')
        t.update_status_with_media(status=postmsg, media=photo)
    except Exception,msg:
        print msg

    # Once the image has been posted we can remove it (twitter is the archive)
    print "Post created, removing local image..."
    os.remove(fullFilePath)

######## MAIN #########

# Images are captured and placed in the "captures" directory as the 
# camera.py script detects movement.  We monitor the "captures" 
# directory for new files and process when detected.
m = FSMonitor()
watch = m.add_dir_watch(CAMERA_CAPTURES_DIR)

while True:
    for evt in m.read_events():
        # The FSMonitor evt.action_name we care about is "move to" (the file 
        # is created in another dir and moved as a whole)
        # Note: the evt.name will be the name of the new file
        if evt.action_name == 'move to':
            time.sleep(10) # Let the full file be written before continuing...
            postNewMessage(evt.name)
