import cv2
import numpy as np
from PIL import Image
import math

"""
This is the naive rotation using minAreaRect. This did not work due to inability to account for hallways and spillover
"""

def fit_room_rectangle(image_path):
    img = Image.open(image_path).convert("RGBA")
    img_np = np.array(img)
    alpha = img_np[:, :, 3]
    mask = (alpha > 0).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
    cleaned = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    largest = max(contours, key=cv2.contourArea)
    rect = cv2.minAreaRect(largest)
    box = cv2.boxPoints(rect)
    box = np.intp(box)

    angle = rect[2]
    if rect[1][0] < rect[1][1]:
        angle += 90

    return img_np, box, angle

def rotate_image(image_np, angle):
    h, w = image_np.shape[:2]
    center = (w // 2, h // 2)
    rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        image_np, rot_mat, (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0, 0)
    )
    return rotated

img_np, box, angle = fit_room_rectangle("blueprint_edited.png")
rotated = rotate_image(img_np, angle)

debug = img_np.copy()
cv2.drawContours(debug, [box], 0, (0, 255, 0, 255), 3)

cv2.imwrite("debug_rectangle_2.png", cv2.cvtColor(debug, cv2.COLOR_RGBA2BGRA))
cv2.imwrite("rotated_2.png", cv2.cvtColor(rotated, cv2.COLOR_RGBA2BGRA))

print("rotation angle:", angle)
