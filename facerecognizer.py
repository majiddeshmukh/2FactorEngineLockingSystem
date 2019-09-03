import cv2
import numpy as np
import os
import RPi.GPIO as GPIO
import time
import serial
port= "/dev/ttyACM0"
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18, GPIO.OUT)
recognizer = cv2.face.createLBPHFaceRecognizer()
recognizer.load('trainer/trainer.yml')
cascadePath = "Cascades/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath);
font = cv2.FONT_HERSHEY_SIMPLEX
servoPIN = 17
GPIO.setup(servoPIN, GPIO.OUT)
p = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz

def engineunlocker():
    
    
    
    p.start(2.5) # Initialization
    try:
      while True:
        p.ChangeDutyCycle(5)
        time.sleep(0.5)
        p.ChangeDutyCycle(7.5)
        time.sleep(0.5)
        alcoholcheck()
    except KeyboardInterrupt:
      p.stop()
      GPIO.cleanup()

def alcoholcheck():
    s1=serial.Serial(port,115200)
    s1.flushInput()

    while True:
        if s1.inWaiting()>0:
            inputValue= s1.readline()
            res = [int(i) for i in inputValue.split() if i.isdigit()]
            print(str(res))
            for i in res:
                 if i<200:
                     print("Engine Unlocked! Drive Safely")
                     engineunlocker()
                 else:
                     print("You are not in a condition to drive!")
                     exit()



#iniciate id counter
id = 0
# names related to ids: example ==> Marcelo: id=1,  etc
names = ['None', 'Majid', 'Pratiksha', '', '', ''] 
# Initialize and start realtime video capture
cam = cv2.VideoCapture(0)
cam.set(3, 640) # set video widht
cam.set(4, 480) # set video height
# Define min window size to be recognized as a face
minW = 0.1*cam.get(3)
minH = 0.1*cam.get(4)
while True:
    ret, img =cam.read()
   # img = cv2.flip(img, -1) # Flip vertically
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    
    faces = faceCascade.detectMultiScale( 
        gray,
        scaleFactor = 1.2,
        minNeighbors = 5,
        minSize = (int(minW), int(minH)),
       )
    for(x,y,w,h) in faces:
        cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
        id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
        # Check if confidence is less them 100 ==> "0" is perfect match 
        if (confidence < 100):
            id = names[id]
            confidence = "  {0}%".format(round(100 - confidence))
            print("Welcome! " +id)
            time.sleep(3)
            cam.release()
            cv2.destroyAllWindows()
            alcoholcheck()
        else:
            id = "unknown"
            confidence = "  {0}%".format(round(100 - confidence))
            GPIO.output(18,GPIO.LOW)
        
        cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
        cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)  
    
    cv2.imshow('camera',img) 
    k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
    if k == 27:
        break

# Do a bit of cleanup
print("\n [INFO] Exiting Program and cleanup stuff")
cam.release()
cv2.destroyAllWindows()




