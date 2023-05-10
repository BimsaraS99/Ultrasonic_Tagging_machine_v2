import cv2
import math
import numpy as np


def adjust_coordinates(new, old, angle, org_coordinates):
    center = new.shape[0] // 2
    new = rotate_image(new, angle)
    corners_new = cv2.goodFeaturesToTrack(cv2.GaussianBlur(new, (9, 9), 0), 20, 0.2, 20)
    corners_old = cv2.goodFeaturesToTrack(cv2.GaussianBlur(old, (9, 9), 0), 20, 0.2, 20)
    new_c, old_c = [], []

    for corner in corners_new:
        x, y = map(int, corner.ravel())
        new_c.append((x, y))
    for corner in corners_old:
        x, y = map(int, corner.ravel())
        old_c.append((x, y))

    corners_new, corners_old = match_coordinates(new_c, old_c, 25)
    old_converted_coordinates, old_converted_distance, old_angles = [], [], []

    for coordinate in org_coordinates:
        x_abs, y_abs = int((int(coordinate[0]) * 1) + center), int((int(coordinate[1]) * -1) + center)
        old_converted_coordinates.append((x_abs, y_abs))
        dist_list, angles = distances_to_coordinates((x_abs, y_abs), corners_old)
        old_converted_distance.append(dist_list)
        old_angles.append(angles)
    offset_values = find_offset_number(old, old_converted_coordinates)

    print("offset value - ", offset_values)
    print("old_dist - ", old_converted_distance)
    print("corner new - ", corners_new)
    print("corner old - ", corners_old)
    print("angles - ", old_angles)

    for corner_new, corner_old in zip(corners_new, corners_old):
        cv2.circle(new, corner_new, 1, (0, 255, 0), -1)
        cv2.circle(old, corner_old, 1, (0, 255, 0), -1)

    concatenated_image = cv2.hconcat([old, new])
    cv2.imshow('Images with corners', concatenated_image)

    return org_coordinates


def rotate_image(img_to_rotate, angle):
    image = img_to_rotate
    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_image = cv2.warpAffine(image, matrix, (width, height))

    return rotated_image


def match_coordinates(coords1, coords2, threshold=15):
    matched_coords1 = []
    matched_coords2 = []
    for coord1 in coords1:
        closest_distance = float('inf')
        closest_coord2 = None
        for coord2 in coords2:
            distance = ((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)**0.5
            if distance < closest_distance:
                closest_distance = distance
                closest_coord2 = coord2
        if closest_distance <= threshold:
            matched_coords1.append(coord1)
            matched_coords2.append(closest_coord2)

    return matched_coords1, matched_coords2


def distances_to_coordinates(pt, coord_list):
    distances = []
    angles = []
    for coord in coord_list:
        dx = coord[0] - pt[0]  # Calculate x distance
        dy = coord[1] - pt[1]  # Calculate y distance
        distance = math.sqrt(dx**2 + dy**2)  # Calculate Euclidean distance
        angle_rad = math.atan2(dy, dx)  # Calculate angle in radians
        angle_deg = math.degrees(angle_rad)  # Convert angle to degrees
        distances.append(distance)
        angles.append(angle_deg)

    return distances, angles


def draw_line_at_angle(img, start_x, start_y, angle_deg, line_length, thickness, color):
    angle_rad = math.radians(angle_deg)  # Convert angle to radians
    end_x = int(start_x + line_length * math.cos(angle_rad))
    end_y = int(start_y + line_length * math.sin(angle_rad))

    cv2.line(img, (start_x, start_y), (end_x, end_y), color, thickness)

    return img


def resize_image(image, scale_factor):
    height, width = image.shape[:2]
    new_height = int(height * scale_factor)
    new_width = int(width * scale_factor)
    resized_image = cv2.resize(image, (new_width, new_height))

    return resized_image


def add_border(image, border_color, size):
    height, width = image.shape
    border_size = (size - width) // 2
    bordered_image = cv2.copyMakeBorder(image, border_size, border_size, border_size, border_size,
                                        cv2.BORDER_CONSTANT, value=border_color)
    return bordered_image


def find_offset_number(image, x_and_y):
    height, width = image.shape
    offset_values = [0 for _ in x_and_y]
    for i in range(100, 1, -1):
        new_image = resize_image(image, (i/100))
        resize_new = cv2.resize(add_border(new_image, (0, 0, 0), width), (height, width))
        result_xor = cv2.bitwise_xor(resize_new, image)

        counter = 0
        for point in x_and_y:
            pixel_value = result_xor[point[1], point[0]]
            if pixel_value > 50 and offset_values[counter] == 0:
                offset_values[counter] = i
            counter += 1

    return offset_values
