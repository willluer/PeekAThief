import RPi.GPIO as GPIO                    #Import GPIO library
import time                                #Import time library
import picamera
from random import choice
from twython import Twython

camera= picamera.PiCamera()
GPIO.setmode(GPIO.BCM)                     #Set GPIO pin numbering 

TRIG = 25
ECHO = 26
x = 0

# Get Twitter keys from the supervisord env
APP_KEY = 'xcc9Mq2LhR5BOAPXlVJ8n1b4d'
APP_SECRET = 'aQTJ4R0g5csC5cyt7VeUhe3mmmkAcWKM1ieHrOhBUSfTwWPBM4'
OAUTH_TOKEN = '850021330955227136-arS8gjUz5oxnIKUS10SiYGKbq5eEMwh'
OAUTH_TOKEN_SECRET = 'LJqpZ1qD7mC55GgyDC9aLsNT7xUBfCc109GXNQpyiKLUg'

t = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

POST_MESSAGES = ["Caught ya!", "Stay out my drawer Humberto", "Humberto wouldn't approve","Big brother's always watching","I'm missing an eye, but I see you better than you see yourself sometimes", "I'm gonna tell your mommy", "Thou shalt not steal - Exodus 20:15", "He who is a partner with a thief, hates his own life. He hears the oath but tells nothing - Proverbs 29:23", "Sometimes its not worth it...", "If you have to lie, cheat, steal, you're just not doing it right - Donald J. Trump", "If you forgive the fox for stealing your chickens, he will take your sheep", "Cheaters never win", "Don't - Bryson Tiller", "Fool me once, shame on you, fool me twice, not gonna happen", "I don't think so...", "Who you are ya trying to fool son!!!!", "Holden Claufield thinks you're a phony", "Derick doesn't like people stealing his snacks", "Pichy doesn't like thieves!"]

print ("Distance measurement in progress")

GPIO.setup(TRIG,GPIO.OUT)                  #Set pin as GPIO out
GPIO.setup(ECHO,GPIO.IN)                   #Set pin as GPIO in

while True:

  GPIO.output(TRIG, False)                 #Set TRIG as LOW
 # print ("Waitng For Sensor To Settle")
  time.sleep(.5)                            #Delay of 2 seconds

  GPIO.output(TRIG, True)                  #Set TRIG as HIGH
  time.sleep(0.00001)                      #Delay of 0.00001 seconds
  GPIO.output(TRIG, False)                 #Set TRIG as LOW

  while GPIO.input(ECHO)==0:               #Check whether the ECHO is LOW
    pulse_start = time.time()              #Saves the last known time of LOW pulse
  
  while GPIO.input(ECHO)==1:               #Check whether the ECHO is HIGH
    pulse_end = time.time()                #Saves the last known time of HIGH pulse

  pulse_duration = pulse_end - pulse_start #Get pulse duration to a variable
  
  distance = pulse_duration * 17150        #Multiply pulse duration by 17150 to get distance
  distance = round(distance, 2)            #Round to two decimal points\
  
  if distance < 50:      #Check whether the distance is within range
    print ("Distance:",distance - 0.5,"cm")
    print ("DRAWER CLOSED")                   #display out of range
    x = 0
  else:
      if x < 10:
            print ("PICTURE TAKEN")
            fileName = 'image_'+str(x)+'.jpg'
            camera.capture(fileName)
            photo = open(fileName,'rb')
            postmsg = choice(POST_MESSAGES)
            t.update_status_with_media(status=postmsg,media=photo)
            x= x+1
