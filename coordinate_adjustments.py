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
    old_converted_coordinates = []

    for coordinate in org_coordinates:
        x_abs, y_abs = int((int(coordinate[0]) * 1) + center), int((int(coordinate[1]) * -1) + center)
        old_converted_coordinates.append((x_abs, y_abs))

    offset_values = find_offset_number(old, old_converted_coordinates)
    coordinate_angles = calculate_angles(center, center, old_converted_coordinates)
    corner_angles_old = calculate_angles(center, center, corners_old)
    corner_angles_new = calculate_angles(center, center, corners_new)

    updated_coordinates = find_new_coordinates(new, offset_values, corner_angles_old, corner_angles_new,
                                               coordinate_angles, old_converted_coordinates)

    cv2.circle(new, updated_coordinates[0], 1, (0, 0, 0), thickness=2)
    newest_coordinates = reset_coordinates(updated_coordinates, center, angle)

    for corner_new, corner_old in zip(corners_new, corners_old):
        cv2.circle(new, corner_new, 1, (0, 255, 0), -1)
        cv2.circle(old, corner_old, 1, (0, 255, 0), -1)

    concatenated_image = cv2.hconcat([old, new])
    cv2.imshow('Images with corners', concatenated_image)

    print("org - ", org_coordinates)
    print("updated - ", newest_coordinates)

    return newest_coordinates


def reset_coordinates(coordinates, center, angle):
    new_coordinates = []
    for coordinate in coordinates:
        x = coordinate[0] - center
        y = center - coordinate[1]
        new_coordinates.append((x, y))
    new_coordinates = rotate_coordinate_list(new_coordinates, -angle)
    return new_coordinates


def rotate_coordinate_list(coords, angle_degrees):
    def rotate_coordinates(x, y, angle):
        angle = math.radians(angle)
        sin = math.sin(angle)
        cos = math.cos(angle)
        new_x = x * cos - y * sin
        new_y = x * sin + y * cos

        return new_x, new_y

    rotated_coords = []
    for x, y in coords:
        new_x, new_y = rotate_coordinates(x, y, angle_degrees)
        rotated_coords.append((new_x, new_y))

    return rotated_coords


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


def calculate_angles(cx, cy, xys):
    angles = []
    for x, y in xys:
        angle = math.atan2(y-cy, x-cx) * 180 / math.pi
        angles.append(angle)
    return angles


def find_nearest_angle(main_angle, angle_list):
    angle_array = np.array(angle_list)
    angle_diff = angle_array - main_angle
    angle_diff_abs = np.abs(angle_diff)
    nearest_index = np.argmin(angle_diff_abs)
    nearest_angle = angle_list[nearest_index]
    angle_diff_nearest = angle_diff[nearest_index]

    return nearest_angle, nearest_index, angle_diff_nearest


def draw_line_from_center(image, angle_degrees):
    height, width = image.shape[:2]

    center_x = int(width / 2)
    center_y = int(height / 2)
    center_point = (center_x, center_y)

    angle_radians = math.radians(angle_degrees)

    line_length = int(min(width, height))
    end_x = center_x + int(line_length * math.cos(angle_radians))
    end_y = center_y - int(line_length * math.sin(angle_radians))
    endpoint = (end_x, end_y)

    image_with_line = cv2.line(image, center_point, endpoint, (255, 255, 255), 1)

    return (center_x, center_y), (end_x, end_y)


def find_coinciding_coordinates(coords, start_point, end_point):
    coinciding_coords = []
    for coord in coords:
        x1, y1 = start_point
        x2, y2 = end_point
        x3, y3 = coord
        distance = np.abs((y2-y1)*x3 - (x2-x1)*y3 + x2*y1 - y2*x1) / np.sqrt((y2-y1)**2 + (x2-x1)**2)
        if distance < 1:
            coinciding_coords.append(coord)
    return coinciding_coords


def find_nearest_coordinate(coord_list, main_coord):
    distances = []
    for i, coord in enumerate(coord_list):
        dist = np.sqrt((coord[0] - main_coord[0])**2 + (coord[1] - main_coord[1])**2)
        distances.append(dist)

    nearest_index = np.argmin(distances)
    nearest_coord = coord_list[nearest_index]

    return nearest_coord


def find_new_coordinates(image, offset_values, corner_ang_old, corner_ang_new, coordinate_ang, old_coordinate):
    updated_coordinates, counter = [], 0
    for offset_value in offset_values:
        height, width = image.shape
        image_resize = resize_image(image, offset_value/100)
        image_resize = cv2.resize(add_border(image_resize, (0, 0, 0), width), (height, width))

        blank_image = np.zeros((height, width), dtype=np.uint8)
        contour, _ = cv2.findContours(image_resize, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(blank_image, contour, -1, (255, 255, 255), 1)

        nearest_angle, nearest_an_index, difference = find_nearest_angle(coordinate_ang[counter], corner_ang_old)
        new_coordinate_angle = corner_ang_new[nearest_an_index] - difference

        white_pixels = np.where(blank_image == 255)
        white_pixels = list(zip(white_pixels[1], white_pixels[0]))
        center_xy, end_xy = draw_line_from_center(blank_image, -new_coordinate_angle)

        up_coordinates = find_coinciding_coordinates(white_pixels, center_xy, end_xy)
        up_coordinates = find_nearest_coordinate(up_coordinates, old_coordinate[counter])
        updated_coordinates.append(up_coordinates)
        counter += 1

        cv2.circle(blank_image, (128, 370), 1, (255, 255, 255), thickness=2)

        #print("nearest an - ", nearest_angle, nearest_an_index, difference, new_coordinate_angle)
        #print("print - ", old_coordinate)
        #print("coincide", up_coordinates)
        cv2.imshow("reig", blank_image)

    return updated_coordinates
