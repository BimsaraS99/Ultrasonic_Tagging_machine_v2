import cv2
import numpy as np

# Load the image and convert it to grayscale
image = cv2.imread("A:/Internship MAS/23.04.2023/Fabric_Images/fk1.jpg")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Threshold the image to obtain a binary image
_, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

# Find contours in the binary image
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Create a blank image with the same dimensions as the input image
blank_image = np.zeros_like(image)


cv2.drawContours(blank_image, contours, -1, (255, 255, 255), 1)

# Display the result
cv2.imshow('Result', blank_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
