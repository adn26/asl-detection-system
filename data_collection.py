import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import math
import time

cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=1) # just one hand for image

offset = 20 # used for correcting the image crop

imgSize = 300

folder = "data/D" # folder to save the images to (we change this for each letter)

counter = 0

while True:
    success, img = cap.read()
    hands, img = detector.findHands(img)

    # if there's a hand in frame
    if hands:
        hand = hands[0]
        x, y, w, h = hand['bbox'] # get bounding box dimensions

        # just a white image
        imgWhite = np.ones((imgSize,imgSize,3),np.uint8)*255

        # Get the cropped hand image
        imgCrop = img[y-offset : y + h + offset,x - offset : x + w + offset]

        aspectratio = h/w

        # making the crop more efficient for better results
        if aspectratio > 1:
            k = imgSize/h
            wcalculated = math.ceil(k*w)
            imgResize = cv2.resize(imgCrop,(wcalculated,imgSize))
            imgResizeShape = imgResize.shape
            wGap = math.ceil((imgSize - wcalculated)/2)

            # putting resized image inside imgWhite matrix (overlay)
            imgWhite[ : , wGap:wcalculated+wGap] = imgResize

        # if there's a change in width
        else:
            k = imgSize/w
            hcalculated = math.ceil(k*h)
            imgResize = cv2.resize(imgCrop,(imgSize, hcalculated))
            imgResizeShape = imgResize.shape
            hGap = math.ceil((imgSize - hcalculated)/2)

            imgWhite[hGap:hcalculated+hGap, :  ] = imgResize


        cv2.imshow("ImageCrop",imgCrop)
        cv2.imshow("ImageWhite",imgWhite)


    cv2.imshow("Image",img)
    key = cv2.waitKey(1)

    if key == ord("s"):
        counter += 1
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg',imgWhite)
        print(counter)

    # "q" to quit the program
    if key == ord("q"):
        break


