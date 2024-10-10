import cv2
import RPi.GPIO as GPIO
import time

# Setup GPIO
GPIO.setwarnings(False)  
GPIO.setmode(GPIO.BCM)  
motion_pin = 18  
GPIO.setup(motion_pin, GPIO.OUT)  

# Initialize Video Capture
video = cv2.VideoCapture("rtsp://admin:admin123@192.168.18.119/:554/cam/realmonitor?channel=1&subtype=1")
ret, frame1 = video.read()
ret, frame2 = video.read()

while video.isOpened():
    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    
    _, contours, hierarchy = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    motion_detected = False  
    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)

        if cv2.contourArea(contour) < 900:
            continue

        # Draw a rectangle for motion
        cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame1, "Status: {}".format('Movement'), (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        motion_detected = True

    if motion_detected:
        GPIO.output(motion_pin, GPIO.HIGH) 
    else:
        GPIO.output(motion_pin, GPIO.LOW)  


    cv2.imshow("feed", frame1)

    # Exit on 'ESC' key press
    if cv2.waitKey(40) == 27:
        break

    # Prepare the next frames
    frame1 = frame2
    ret, frame2 = video.read()

# Clean up
cv2.destroyAllWindows()
video.release()
GPIO.cleanup()  # Reset GPIO settings