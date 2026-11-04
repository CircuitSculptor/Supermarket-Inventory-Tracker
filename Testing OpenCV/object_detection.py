import cv2
from matplotlib import pyplot as plt

img = cv2.imread('assets\\recognize_stop_sign\\image.jpg')

img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
plt.imshow(img_rgb)
plt.show()

stop_cascade = cv2.CascadeClassifier('assets\\recognize_stop_sign\\stop_data.xml')

found = stop_cascade.detectMultiScale(img_gray, minSize=(20, 20))

for (x, y, w, h) in found:
    cv2.rectangle(img_rgb, (x, y), (x + w, y + h), (0, 255, 0), 5)

plt.imshow(img_rgb)
plt.show()

# It appears that the raw image is displayed with plt.imgshow(img_rgb) but
# then the script ends on cv2 has no attribute 'CascadeClassifier'
# I will revisit this code later

# TODO: Fix CascadeClassifier issue
