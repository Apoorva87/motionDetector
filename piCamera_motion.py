#!/usr/bin/env python
import numpy as np
import cv2
import imutils
import datetime
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
from fractions import Fraction


camera            = PiCamera()
camera.resolution =(1280,720)
camera.framerate  = 12
rawCapture        = PiRGBArray(camera)
time.sleep(0.1)

fgbg       = cv2.BackgroundSubtractorMOG2()
fourcc     = cv2.cv.CV_FOURCC(*'XVID')
out        = cv2.VideoWriter('video1.avi',fourcc, 20.0, (640,480))

for image in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
    frame      = image.array
    text       = 'Unoccupied'
    fgmask = fgbg.apply(frame)
    (cnts1, _) = cv2.findContours(fgmask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in cnts1:
        #print("area ",cv2.contourArea(c))
        if cv2.contourArea(c) < 1000:
            continue
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)
        text = "Occupied"
    # draw the text and timestamp on the frame
    cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

    # show the frame and record if the user presses a key
    cv2.imshow("Security Feed", frame)
    if text == 'Occupied':
      out.write(frame)
    res, temp = cv2.imencode('.jpg',frame)
    #cv2.imshow("Thresh", thresh)
    #cv2.imshow("Frame Delta", frameDelta)
    key = cv2.waitKey(1) & 0xFF
    rawCapture.truncate(0)

    # if the `q` key is pressed, break from the lop
    if key == ord("q"):
        break

    # cleanup the camera and close any open windows
camera.release()
out.release()
cv2.destroyAllWindows()

