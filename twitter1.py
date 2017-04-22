import os
import time
from random import choice
from twython import Twython
from fsmonitor import FSMonitor

# Camera captures directory
CAMERA_CAPTURES_DIR = "/home/pi/Desktop/Peeka"

# A variety of possible post message so we don't always repeat the same thing
POST_MESSAGES = ["It's feeding time!", "Chow's on!", "Bon appétit!", "Come and get it!", 
        "Seeds? Seeds AGAIN?", "Let's eat!", "Strapping on ye olde feedbag", 
        "A banquet awaits us, friend"]

# Get Twitter keys from the supervisord env
APP_KEY = 'xcc9Mq2LhR5BOAPXlVJ8n1b4d'
APP_SECRET = 'aQTJ4R0g5csC5cyt7VeUhe3mmmkAcWKM1ieHrOhBUSfTwWPBM4'
OAUTH_TOKEN = '850021330955227136-arS8gjUz5oxnIKUS10SiYGKbq5eEMwh'
OAUTH_TOKEN_SECRET = 'LJqpZ1qD7mC55GgyDC9aLsNT7xUBfCc109GXNQpyiKLUg'

t = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

# Used to post status updates with bird images as new images are detected
def postNewMessage(fileName):
    print ("Uploading new post with image...")
    fullFilePath = CAMERA_CAPTURES_DIR + fileName
    
    # Grab a random post message
    postmsg = choice(POST_MESSAGES)
    
    try:
        photo = photo = open(fullFilePath, 'rb')
        t.update_status_with_media(status=postmsg, media=photo)
    except:
        print ("eror")

    # Once the image has been posted we can remove it (twitter is the archive)
    print ("Post created, removing local image...")
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

