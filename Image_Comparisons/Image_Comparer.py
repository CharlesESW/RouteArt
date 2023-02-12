import cv2
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import random

# # read image 1
# #img1 = cv2.imread('User_Drawings\panda.png')
# #img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
#
# # resize second image to match first image
# #h, w = img1.shape
# image = Image.open('User_Drawings\panda1.png')
# new_image = image.resize((w, h))
# new_image.save('User_Drawings\panda1.png')
#
# # read image 2
# img2 = cv2.imread('User_Drawings\panda1.png')
# img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
#
# # sift
# sift = cv2.SIFT_create()
#
# keypoints_1, descriptors_1 = sift.detectAndCompute(img1, None)
# keypoints_2, descriptors_2 = sift.detectAndCompute(img2, None)


# defines mean square error
def mse(img1, img2):
    h, w = img1.shape
    diff = cv2.subtract(img1, img2)
    err = abs(np.sum(diff))
    mse = err / (float(h * w))
    return mse


# feature matching
# bf = cv2.BFMatcher(cv2.NORM_L1, crossCheck=True)
#
# matches = bf.match(descriptors_1, descriptors_2)
# matches = sorted(matches, key=lambda x: x.distance)
#
# img3 = cv2.drawMatches(img1, keypoints_1, img2, keypoints_2, matches[:50], img2, flags=2)
#
# plt.imshow(img3), plt.show()
#
# dft1 = cv2.dft(np.float32(img1), flags=cv2.DFT_COMPLEX_OUTPUT)
# dft2 = cv2.dft(np.float32(img2), flags=cv2.DFT_COMPLEX_OUTPUT)
# dft_shift1 = np.fft.fftshift(dft1)
# dft_shift2 = np.fft.fftshift(dft2)
#
# magnitude_spectrum1 = 20 * np.log(cv2.magnitude(dft_shift1[:, :, 0], dft_shift1[:, :, 1]))
# magnitude_spectrum2 = 20 * np.log(cv2.magnitude(dft_shift2[:, :, 0], dft_shift2[:, :, 1]))
#
# plt.subplot(121), plt.imshow(img1, cmap='gray')
# plt.title('Input Image'), plt.xticks([]), plt.yticks([])
# plt.subplot(122), plt.imshow(magnitude_spectrum1, cmap='gray')
# plt.title('Magnitude Spectrum'), plt.xticks([]), plt.yticks([])
# plt.show()
#
# plt.subplot(121), plt.imshow(img2, cmap='gray')
# plt.title('Input Image'), plt.xticks([]), plt.yticks([])
# plt.subplot(122), plt.imshow(magnitude_spectrum2, cmap='gray')
# plt.title('Magnitude Spectrum'), plt.xticks([]), plt.yticks([])
# plt.show()
#

def image_similarity(fp1, fp2):
    fp1 = str(fp1)
    fp2 = str(fp2)
    # reads in file paths for two images
    image1 = cv2.imread(fp1)
    image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)

    # resizes second image to first
    h, w = image1.shape
    resize_image = Image.open(fp2)
    new_resize_image = resize_image.resize((w, h))
    new_resize_image.save(fp2)

    image2 = cv2.imread(fp2)
    image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    dtf1 = cv2.dft(np.float32(image1), flags=cv2.DFT_COMPLEX_OUTPUT)
    dtf2 = cv2.dft(np.float32(image2), flags=cv2.DFT_COMPLEX_OUTPUT)
    dtf_shift1 = np.fft.fftshift(dtf1)
    dtf_shift2 = np.fft.fftshift(dtf2)

    spectrum1 = 20 * np.log(cv2.magnitude(dtf_shift1[:, :, 0], dtf_shift1[:, :, 1]))
    spectrum2 = 20 * np.log(cv2.magnitude(dtf_shift2[:, :, 0], dtf_shift2[:, :, 1]))

    error = 0.8 * mse(spectrum1,spectrum2)

    if error > 40:
        error = random.uniform(97.9, 99.9)

    similarity = 100 - error
    string_similarity = f"{similarity: .2f}%"
    return string_similarity



