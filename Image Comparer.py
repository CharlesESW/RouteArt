import cv2
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np



# read image 1
img1 = cv2.imread('panda.png')
img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)

# resize second image to match first image
h, w = img1.shape
image = Image.open('panda1.png')
new_image = image.resize((w, h))
new_image.save('panda1.png')

# read image 2
img2 = cv2.imread('panda1.png')
img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

#sift
sift = cv2.SIFT_create()

keypoints_1, descriptors_1 = sift.detectAndCompute(img1,None)
keypoints_2, descriptors_2 = sift.detectAndCompute(img2,None)

# defines mean square error
def mse(img1, img2):
   h, w = img1.shape
   diff = cv2.subtract(img1, img2)
   err = np.sum(diff)
   mse = err/(float(h*w))
   return mse, diff


#feature matching
bf = cv2.BFMatcher(cv2.NORM_L1, crossCheck=True)

matches = bf.match(descriptors_1,descriptors_2)
matches = sorted(matches, key = lambda x:x.distance)

img3 = cv2.drawMatches(img1, keypoints_1, img2, keypoints_2, matches[:50], img2, flags=2)
error, diff = mse(img1, img2)

# outputting the data calculated
print("Image matching difference between the two images:",error)
plt.imshow(img3),plt.show()
