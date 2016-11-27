import cv2

img = cv2.imread('C:/Users/Andromeda/Pictures/Capture.png')
def imageOpen():
    cv2.imshow("source",img)
    cv2.waitKey(0)

cap = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))
imageOpen()
while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
      #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
      # Display the resulting frame
      #cv2.imshow('frame',gray)
      cv2.imshow('frame',frame)
      out.write(frame)
      if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    else:
        break
# When everything done, release the capture
cap.release()
out.release()
cv2.destroyAllWindows()
