import os
import cv2
import numpy as np
import math
from coordinate_adjustments import adjust_coordinates

fabric_name = "home_shape"
saved_image_path = f"./saving_information/{fabric_name}/fabric_image.jpg"
new_image_path = "A:/Internship MAS/23.04.2023/Fabric_Images/IMG_20230503_204734.jpg"
white_count_list = list()


def detect_fabric_location(img_pass):
    gray_img = cv2.cvtColor(img_pass, cv2.COLOR_BGR2GRAY)
    thresh_img = cv2.threshold(gray_img, 127, 255, cv2.THRESH_OTSU)[1]
    contours, _ = cv2.findContours(thresh_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largest_contour = max(contours, key=cv2.contourArea)

    moments = cv2.moments(largest_contour)
    mid_x = int(moments['m10'] / moments['m00'])
    mid_y = int(moments['m01'] / moments['m00'])

    return largest_contour, (mid_x, mid_y)


def find_largest_contour(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_OTSU)
    cv2.waiteKey(0)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largest_contour = max(contours, key=cv2.contourArea)
    return largest_contour


def crop_square_from_image(image, midpoint, square_size):
    x = midpoint[0] - (square_size // 2)
    y = midpoint[1] - (square_size // 2)

    cropped_image = image[y:y + square_size, x:x + square_size]
    return cropped_image


def get_largest_contour_image(img):
    image = img
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_OTSU)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    largest_contour = max(contours, key=cv2.contourArea)

    mask = np.zeros_like(gray)
    cv2.drawContours(mask, [largest_contour], 0, 255, -1)

    return mask


def rotate_image(img_to_rotate, angle):
    image = img_to_rotate
    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_image = cv2.warpAffine(image, matrix, (width, height))

    return rotated_image


def find_angle_of_new_image(cropped_new_img, cropped_old_img):
    for i in range(0, 360):
        rot_img = rotate_image(cropped_new_img, i)
        result_xor = cv2.bitwise_xor(cropped_old_img, rot_img)
        white_count = np.count_nonzero(result_xor)
        white_count_list.append(white_count)

    return white_count_list.index(min(white_count_list)), min(white_count_list),


def read_coordinates(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    coordinates = []
    for line in lines:
        x, y = map(int, line.strip()[1:-1].split(','))
        coordinates.append((x, y))
    return coordinates


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


def draw_circles_on_image(img, coords):
    h, w = img.shape[:2]
    for x_rel, y_rel in coords:
        x_abs = int((int(x_rel) * 1) + h / 2)
        y_abs = int((int(y_rel) * -1) + h / 2)
        cv2.circle(img, (x_abs, y_abs), 3, (0, 0, 0), -1)

    return img


def gcode_making(rot_xy, midpoint, image):
    g_codes = []
    for x_rel, y_rel in rot_xy:
        x_abs = int((int(x_rel) * 1) + midpoint[0])
        y_abs = int((int(y_rel) * -1) + midpoint[1])
        cv2.circle(image, (x_abs, y_abs), 3, (0, 0, 0), -1)
        text = f"({x_abs}, {y_abs})"
        cv2.putText(image, text, (x_abs + 5, y_abs - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 0), 1)
        g_codes.append((x_abs, y_abs))

    return image, g_codes


# ---------------------------------------------------------------------------------------------------------------------


saved_image = cv2.imread(saved_image_path)
new_image = cv2.imread(new_image_path)

h, w, _ = new_image.shape
h_n, w_n, _ = saved_image.shape

new_h = int((9 / 16) * 1200)
new_image = cv2.resize(new_image, (1200, new_h), interpolation=cv2.INTER_LINEAR)
normal_image = new_image.copy()
fabric, mid_point = detect_fabric_location(new_image)

cropped_old_image = saved_image.copy()
old_first_image = cropped_old_image

cropped_new_image = crop_square_from_image(new_image, mid_point, h_n)
new_first_image = cropped_new_image

cropped_old_image = get_largest_contour_image(cropped_old_image)
cropped_new_image = get_largest_contour_image(cropped_new_image)

angle_of_the_image, white_px_count = find_angle_of_new_image(cropped_new_image, cropped_old_image)

xy_coordinates = read_coordinates(f"./saving_information/{fabric_name}/positions.txt")

rotated_coordinates = rotate_coordinate_list(xy_coordinates, -angle_of_the_image)
new_rot_coordinates = adjust_coordinates(cropped_new_image, cropped_old_image, angle_of_the_image, xy_coordinates,
                                         rotated_coordinates)

final_image, sending_codes = gcode_making(rotated_coordinates, mid_point, normal_image)

draw_circles_on_image(old_first_image, xy_coordinates)
draw_circles_on_image(new_first_image, rotated_coordinates)

cv2.imshow("old_first_image", old_first_image)
cv2.imshow("new_first_image", new_first_image)
# cv2.imshow("final image", final_image)

cv2.waitKey(0)
cv2.destroyAllWindows()
