#!/usr/bin/env python
import numpy as np
import cv2
import imutils
import datetime
import time
import io
import threading
import picamera
import logging
import signal, os
from picamera.array import PiRGBArray
from fractions import Fraction
from flask import Flask, render_template, Response, request


app     = Flask(__name__)
camLock = threading.RLock()
logging.basicConfig(level=logging.DEBUG,
                    format='([(%(relativeCreated)4d) ms] %(threadName)-10s) %(message)s',
                   )
freeStream = False

class motionSense(threading.Thread):
    startF  = True
    stopF   = False
    def __init__(self, output='motion.avi'):
      threading.Thread.__init__(self)
      self.fgbg   = cv2.BackgroundSubtractorMOG2()
      self.fourcc = cv2.cv.CV_FOURCC(*'XVID')
      self.out    = cv2.VideoWriter(output,self.fourcc, 20.0, (640,480))
      self.__class__.startF = True
      self.__class__.stopF  = False
      logging.debug('Motion sensing init...')
      return

    def __del__(self):
      self.out.release()
      print('[MS] Motion sensing destroyed...')

    @classmethod 
    def stop(cls):
      while (cls.stopF != True):
        time.sleep(0.1)
        cls.startF = False
      return

    def run(self):
      logging.debug('[MS] Motion sensing started...')
      while self.__class__.stopF == False and freeStream == False:
        avg      = None
        frameCnt = 0
        camLock.acquire()
        logging.debug("[MS] Acquiring camera lock")
        try:
          with picamera.PiCamera() as camera:
            #camera.resolution = (1280, 720)
            #camera.framerate  = 4
            rawCapture        = PiRGBArray(camera)
            #time.sleep(0.1)
            for image in camera.capture_continuous(rawCapture,
                                                   format='bgr',
                                                   use_video_port=False):
                text       = 'Unoccupied'
                frame      = image.array
                frame      = imutils.resize(frame, width=500)
                gray       = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray       = cv2.GaussianBlur(gray, (21,21), 0)
               
                if avg is None:
                   logging.debug("[MS] Starting BG model")
                   avg = gray.copy().astype("float")
                   rawCapture.truncate(0)
                   continue
                #cv2.imwrite('gray.jpg',gray)
                cv2.accumulateWeighted(gray, avg, 0.5)
                frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
                #cv2.imwrite('frameDelta.jpg',frameDelta)
                thresh     = cv2.threshold(frameDelta, 5, 255, cv2.THRESH_BINARY)[1]
                thresh     = cv2.dilate(thresh, None, iterations=2)
                #cv2.imwrite('thresh.jpg',thresh)
                (cnts1, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                              cv2.CHAIN_APPROX_SIMPLE)
                for c in cnts1:
                    if cv2.contourArea(c) < 5000:
                        continue
                    (x, y, w, h) = cv2.boundingRect(c)
                    cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)
                    text = "Occupied"
                # draw the text and timestamp on the frame
                cv2.putText(frame,
                            "Room Status: {}".format(text),
                            (10, 20),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0, 0, 255), 2)
                cv2.putText(frame,
                            datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                            (10, frame.shape[0] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.35, (0, 0, 255), 1)

                if text == 'Occupied':
                    logging.debug("[MS] Motion detected storing frame")
                    self.out.write(frame)

                rawCapture.truncate(0)
                  
                if (self.__class__.startF == False):
                    self.__class__.stopF = True
                    camLock.release()
                    return

                if ((frameCnt > 6) or ((text == 'Unoccupied') and (frameCnt > 4))):
                  logging.debug("[MS] Frame count exceeded or room unoccupied")
                  break;
                frameCnt += 1 # Count the number of frames
        finally:
          camLock.release()
          logging.debug("[MS] Releasing camera lock")

    

class Camera(object):
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera

    def initialize(self):
        if Camera.thread is None:
            # start background frame thread
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()

            # wait until frames start to be available
            while self.frame is None:
                time.sleep(0)

    def get_frame(self):
        Camera.last_access = time.time()
        self.initialize()
        return self.frame


    @classmethod
    def _thread(cls):
        camLock.acquire()
        logging.debug("[FL] Acquired cam lock")
        try:
          with picamera.PiCamera() as camera:
              # camera setup
              #camera.resolution = (320, 240)
              #camera.hflip = True
              #camera.vflip = True

              # let camera warm up
              camera.start_preview()
              time.sleep(0.1)
              frameCnt = 0          
              stream = io.BytesIO()
              for foo in camera.capture_continuous(stream, 'jpeg',
                                                   use_video_port=True):
                  # store frame
                  stream.seek(0)
                  cls.frame = stream.read()

                  # reset stream for next frame
                  stream.seek(0)
                  stream.truncate()
                  ##logging.debug("[FL] Sending frames for webbrowser")

                  # if there hasn't been any clients asking for frames in
                  # the last 10 seconds stop the thread
                  if time.time() - cls.last_access > 3:
                      logging.debug("[FL] No request from web browser")
                      break
                  if (frameCnt > 16) and freeStream == False:
                      logging.debug("[FL] Finished sending frames for webbrowser")
                      break
                  frameCnt  = frameCnt + 1
        finally:
          camLock.release()
          logging.debug("[FL] Released cam lock")
        cls.thread = None


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def shutdown_server():
  func = request.environ.get('werkzeug.server.shutdown')
  if func is None:
    raise RuntimeError('Not running with werkzeug server')
  func()

@app.route('/')
def index():
    """Video streaming home page."""
    logging.debug("[FL] Index html...")
    return render_template('index.html')

@app.route('/freestream')
def freestream():
  global freeStream
  freeStream = True
  return render_template('index.html')

@app.route('/sharestream')
def sharestream():
  global freeStream
  freeStream = False
  return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    logging.debug("[FL] beginning video feed...")
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/shutdown')
def shutdown():
  shutdown_server()
  return 'Server shutting down'

if __name__ == '__main__':
    ms      = motionSense();
    ms.start() 
    #app.run(host='192.168.2.2', port=int('5000'), threaded=True, debug=False)
    app.run(host='0.0.0.0', port=int('80'),  debug=False)
    try:
      while True:
        time.sleep(3)
        continue
    except(KeyboardInterrupt, SystemExit):
      motionSense.stop()
      ms.join()
      logging.debug('Ctr-C called...')
      exit(0)

