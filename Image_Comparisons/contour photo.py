import numpy as np

import cv2

img = cv2.imread('User_Drawings/panda.png', 0)

result_fill = np.ones(img.shape, np.uint8) * 255
result_borders = np.zeros(img.shape, np.uint8)

# the '[:-1]' is used to skip the contour at the outer border of the image
contours = cv2.findContours(img, cv2.RETR_LIST,
                            cv2.CHAIN_APPROX_SIMPLE)[0][:-1]

# fill spaces between contours by setting thickness to -1
cv2.drawContours(result_fill, contours, -1, 0, -1)
cv2.drawContours(result_borders, contours, -1, 255, 1)

# xor the filled result and the borders to recreate the original image
result = result_fill ^ result_borders

# prints True: the result is now exactly the same as the original
print(np.array_equal(result, img))

cv2.imwrite('User_Drawings/contours.png', result)
