import numpy as np
import cv2
import imutils
import datetime

camera     = cv2.VideoCapture(0)
#camera    = cv2.VideoCapture('Output.avi')
fgbg       = cv2.createBackgroundSubtractorMOG2()
fourcc     = cv2.VideoWriter_fourcc(*'XVID')
out        = cv2.VideoWriter('video.avi',fourcc, 20.0, (640,480))
firstFrame = None
while True:
    ret, frame = camera.read()
    text       = 'Unoccupied'
    if not ret:
        break;
    ##1 Method 1
    fgmask = fgbg.apply(frame)
    ##2 Method 2
    #frame      = imutils.resize(frame,width=500)
    #gray       = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #gray       = cv2.GaussianBlur(gray,(21,21),0)
    #if firstFrame is None:
    #    firstFrame = gray
    #    continue
    #frameDelta = cv2.absdiff(firstFrame, gray)
    #thresh     = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
    #thresh     = cv2.dilate(thresh, None, iterations=2)
    #(_,cnts2, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #cv2.imshow('Baldy stuff', thresh)
    #cv2.imshow('BG stuff', fgmask)
    (_, cnts1, _) = cv2.findContours(fgmask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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
    #cv2.imshow("Thresh", thresh)
    #cv2.imshow("Frame Delta", frameDelta)
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key is pressed, break from the lop
    if key == ord("q"):
        break

    # cleanup the camera and close any open windows
camera.release()
out.release()
cv2.destroyAllWindows()
