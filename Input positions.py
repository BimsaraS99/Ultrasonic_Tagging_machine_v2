import os
import cv2

read_image_path = "A:/Internship MAS/23.04.2023/Fabric_Images/IMG_20230503_204704.jpg"
fabric_name = "home_shape"
path_to_save = "./saving_information/"
counter = 0


def detect_fabric_location(img_pass):
    gray_img = cv2.cvtColor(img_pass, cv2.COLOR_BGR2GRAY)
    thresh_img = cv2.threshold(gray_img, 127, 255, cv2.THRESH_OTSU)[1]
    cv2.imshow('Cropped Image', thresh_img)
    contours, _ = cv2.findContours(thresh_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largest_contour = max(contours, key=cv2.contourArea)

    moments = cv2.moments(largest_contour)
    mid_x = int(moments['m10'] / moments['m00'])
    mid_y = int(moments['m01'] / moments['m00'])

    return largest_contour, (mid_x, mid_y)


def on_mouse_click(event, x, y, flags, param):
    global counter
    if event == cv2.EVENT_LBUTTONDOWN:
        fabric_contour, mid_point_fabric = detect_fabric_location(fabric_image)
        if cv2.pointPolygonTest(fabric_contour, (x, y), False) >= 0:
            counter = counter + 1
            with open(f'./saving_information/{fabric_name}/positions.txt', 'a') as f:
                f.write(f'{(x - mid_point_fabric[0], mid_point_fabric[1] - y)}\n')

            cv2.circle(fabric_image, (x, y), 2, (0, 0, 0), -1)
            print((x - mid_point_fabric[0], mid_point_fabric[1] - y))
            cv2.imshow('Cropped Image', fabric_image)


def save_data(image_name, image):
    with open(f'./saving_information/{fabric_name}/positions.txt', 'w') as f:
        f.write('')
    path = os.path.join(path_to_save, image_name)
    os.makedirs(path, exist_ok=True)
    cv2.imwrite(os.path.join(path, 'fabric_image.jpg'), image)


def crop_square_from_image(image, midpoint, square_size):
    x = midpoint[0] - (square_size // 2)
    y = midpoint[1] - (square_size // 2)

    cropped_image = image[y:y+square_size, x:x+square_size]
    return cropped_image
# -------------------------------------------------------------------------------------------------


img = cv2.imread(read_image_path)
h, w, _ = img.shape

new_h = int((9/16) * 1200)
resized_img = cv2.resize(img, (1200, new_h), interpolation=cv2.INTER_LINEAR)
normal_image = resized_img.copy()

fabric, mid_point = detect_fabric_location(resized_img)

X, Y, W, H = cv2.boundingRect(fabric)
cv2.rectangle(resized_img, (X, Y), (X+W, Y+H), (0, 0, 255), 2)
cv2.imshow('Resized Image with Contour Detection', resized_img)
cv2.waitKey(0)
input_ = input("Is detected fabric correct - ")

if input_ == "yes":
    fabric_image = crop_square_from_image(normal_image, mid_point, (max(X, Y, W, H)+50))
    save_data(fabric_name, fabric_image)
    cv2.imshow('Cropped Image', fabric_image)
    cv2.setMouseCallback("Cropped Image", on_mouse_click)

cv2.waitKey(0)
