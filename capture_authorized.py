# capture_authorized.py
import cv2

cap = cv2.VideoCapture(0)
ok, frame = cap.read()
cap.release()

if not ok:
    raise RuntimeError("Could not read webcam")

cv2.imwrite("authorized.jpg", frame)
print("Saved authorized.jpg")

