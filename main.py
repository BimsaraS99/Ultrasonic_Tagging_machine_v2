import cv2
import numpy as np

# Load the input image
image = cv2.imread('A:/Internship MAS/23.04.2023/Fabric_Images/fk1.jpg')

# Set the border size and color
border_size = 10
border_color = [255, 255, 255]  # White color

# Add the border to the image
bordered_image = cv2.copyMakeBorder(image, border_size, border_size, border_size, border_size, cv2.BORDER_CONSTANT, value=border_color)

# Write the output image
cv2.imshow('output.jpg', bordered_image)
cv2.waitKey(0)
