import cv2
import numpy as np

INPUT_IMAGE = "blueprint.png"
OUTPUT_IMAGE = "final_room_rectangle.png"


def rotate_image(img, angle):
    h, w = img.shape[:2]
    center = (w / 2, h / 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_NEAREST)
    return rotated, M


def largest_rectangle_in_mask(mask):
    h, w = mask.shape
    heights = np.zeros(w, dtype=int)
    best_area = 0
    best_rect = None
    for row in range(h):
        for col in range(w):
            if mask[row, col] > 0:
                heights[col] += 1
            else:
                heights[col] = 0

        # histogram max rectangle optimization
        stack = []
        for col in range(w + 1):
            curr = heights[col] if col < w else 0

            while stack and heights[stack[-1]] > curr:
                height = heights[stack.pop()]
                width = col if not stack else col - stack[-1] - 1
                area = height * width

                if area > best_area:
                    best_area = area
                    x = stack[-1] + 1 if stack else 0
                    y = row - height + 1
                    best_rect = (x, y, x + width, y + height)

            stack.append(col)

    return best_rect


def best_rotated_rectangle(mask):
    best = None
    best_area = 0
    best_angle = 0

    for angle in np.linspace(-90, 90, 181):
        rotated, _ = rotate_image(mask, angle)
        rect = largest_rectangle_in_mask(rotated)
        if rect is None:
            continue
        x1, y1, x2, y2 = rect
        area = (x2 - x1) * (y2 - y1)
        if area > best_area:
            best_area = area
            best = rect
            best_angle = angle
    return best, best_angle

def rotate_full_image(img, angle):
    h, w = img.shape[:2]
    center = (w / 2, h / 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        img,
        M,
        (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0, 0) 
    )
    return rotated



img = cv2.imread(INPUT_IMAGE, cv2.IMREAD_UNCHANGED)

if img.shape[2] == 4:
    mask = (img[:, :, 3] > 0).astype(np.uint8) * 255
else:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mask = (gray > 0).astype(np.uint8) * 255

(rect, angle) = best_rotated_rectangle(mask)

x1, y1, x2, y2 = rect

rot_img, _ = rotate_image(img, angle)

cv2.rectangle(rot_img, (x1, y1), (x2, y2), (0, 255, 0, 255), 3)

cv2.imwrite(OUTPUT_IMAGE, rot_img)

print("output:", OUTPUT_IMAGE)
print("rotation angle:", angle)

aligned_img = rotate_full_image(img, 15)

cv2.imwrite("aligned_room.png", aligned_img)
