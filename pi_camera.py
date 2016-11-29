#!/usr/bin/env python
import numpy as np
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
from fractions import Fraction


camera            = PiCamera()
camera.resolution =(1280,720)
camera.framerate  = 12
rawCapture        = PiRGBArray(camera)
#camera    = cv2.VideoCapture('Output.avi')
#camera = PiCamera(resolution=(1280, 720), framerate=30)
# Set ISO to the desired value
#camera.iso = 100
# Wait for the automatic gain control to settle
##sleep(2)
# Now fix the values
#camera.shutter_speed = camera.exposure_speed
#camera.exposure_mode = 'off'
#g = camera.awb_gains
#camera.awb_mode = 'off'
#camera.awb_gains = g
# Finally, take several photos with the fixed settings
#camera.capture_sequence(['image%02d.jpg' % i for i in range(10)])
time.sleep(0.1)
for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
  image = frame.array
  cv2.imshow("Frame",image)
  key = cv2.waitKey(1) & 0xFF
  rawCapture.truncate(0)
  if key == ord("q"):
    break

'''

# Time lapse videos

def wait():
    # Calculate the delay to the start of the next hour
    next_hour = (datetime.now() + timedelta(hour=1)).replace(
        minute=0, second=0, microsecond=0)
    delay = (next_hour - datetime.now()).seconds
    sleep(delay)
camera = PiCamera()
camera.start_preview()
wait()
for filename in camera.capture_continuous('img{timestamp:%Y-%m-%d-%H-%M}.jpg'):
    print('Captured %s' % filename)
    wait()

# Low light

# Set a framerate of 1/6fps, then set shutter
# speed to 6s and ISO to 800
camera = PiCamera(resolution=(1280, 720), framerate=Fraction(1, 6))
camera.shutter_speed = 6000000
camera.iso = 800
# Give the camera a good long time to set gains and
# measure AWB (you may wish to use fixed AWB instead)
sleep(30)
camera.exposure_mode = 'off'
# Finally, capture an image with a 6s exposure. Due
# to mode switching on the still port, this will take
# longer than 6 seconds
camera.capture('dark.jpg')

'''

