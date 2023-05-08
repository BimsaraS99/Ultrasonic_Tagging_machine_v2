import cv2
import numpy as np


def adjust_coordinates(new, old, angle, org_coordinates, rot_coordinates):
    corners_new = cv2.goodFeaturesToTrack(cv2.GaussianBlur(new, (9, 9), 0), 20, 0.2, 20)
    corners_old = cv2.goodFeaturesToTrack(cv2.GaussianBlur(old, (9, 9), 0), 20, 0.2, 20)

    for corner in corners_new:
        x, y = map(int, corner.ravel())
        cv2.circle(new, (x, y), 5, (0, 255, 0), -1)

    for corner in corners_old:
        x, y = map(int, corner.ravel())
        cv2.circle(old, (x, y), 5, (0, 255, 0), -1)

    concatenated_image = cv2.hconcat([old, new])
    cv2.imshow('Images with corners', concatenated_image)

    return org_coordinates
