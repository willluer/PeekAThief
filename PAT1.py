import RPi.GPIO as GPIO                    #Import GPIO library
import time                                #Import time library
import picamera
camera= picamera.PiCamera()
GPIO.setmode(GPIO.BCM)                     #Set GPIO pin numbering 

TRIG = 18                                  #Associate pin 23 to TRIG
ECHO = 19                                  #Associate pin 24 to ECHO
TRIG1 = 25
ECHO1 = 26
x = 0

print ("Distance measurement in progress")

GPIO.setup(TRIG,GPIO.OUT)                  #Set pin as GPIO out
GPIO.setup(ECHO,GPIO.IN)                   #Set pin as GPIO in
GPIO.setup(TRIG1,GPIO.OUT)                  #Set pin as GPIO out
GPIO.setup(ECHO1,GPIO.IN)                   #Set pin as GPIO in

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


  GPIO.output(TRIG1, False)                 #Set TRIG as LOW
  #print ("Waitng For Sensor To Settle")
  time.sleep(.5)                            #Delay of 2 seconds

  GPIO.output(TRIG1, True)                  #Set TRIG as HIGH
  time.sleep(0.00001)                      #Delay of 0.00001 seconds
  GPIO.output(TRIG1, False)                 #Set TRIG as LOW

  while GPIO.input(ECHO1)==0:               #Check whether the ECHO is LOW
    pulse_start1 = time.time()              #Saves the last known time of LOW pulse
  
  while GPIO.input(ECHO1)==1:               #Check whether the ECHO is HIGH
    pulse_end1 = time.time()                #Saves the last known time of HIGH pulse 

  pulse_duration = pulse_end - pulse_start #Get pulse duration to a variable
  pulse_duration1 = pulse_end1- pulse_start1 #Get pulse duration to a variable
  
  distance = pulse_duration * 17150        #Multiply pulse duration by 17150 to get distance
  distance = round(distance, 2)            #Round to two decimal points\

  distance1 = pulse_duration1 * 17150        #Multiply pulse duration by 17150 to get distance
  distance1 = round(distance1, 2)            #Round to two decimal points\
  

  if distance < 50  and distance1 < 50 :      #Check whether the distance is within range
    print ("Distance:",distance - 0.5,"cm")
    print ("Distance1:",distance1 - 0.5,"cm")
    print ("DRAWER CLOSED")                   #display out of range
  else:
    print ("PICTURE TAKEN")
    camera.capture('image_'+str(x)+'.jpg')
    x= x+1
    if x > 10:
      distance < 50  and distance1 < 50
      time.sleep(10) 
      x=0
    
    
