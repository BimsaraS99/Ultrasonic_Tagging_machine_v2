import cv2

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print("Unable to open webcam")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Unable to read frame from webcam")
        break

    cv2.imshow("Webcam", frame)
    cv2.waitKey(1)

cap.release()
cv2.destroyAllWindows()
