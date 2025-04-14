import cv2
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
import numpy as np
import math

cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=1) # just one hand for image

classifier = Classifier("model/keras_model.h5", "model/labels.txt") # load the model

offset = 20 # used for correcting the image crop

imgSize = 300 # size of the image to be used for the model

text = ""  # Store the text input
current_letter = ""  # Store the current letter to be confirmed
last_prediction = ""  # Store the last prediction to avoid duplicates
prediction_cooldown = 0  # Cooldown counter to avoid rapid predictions
letter_ready = False  # Flag to indicate if a letter is ready to be confirmed

labels = ['A', 'B', 'C', 'D', 'del', 'E', 'F', 'G', 'H', 'I', 'J',
          'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
          'U', 'V', 'W', 'X', 'Y', 'Z','space'] # labels for the model 

while True:
    success, img = cap.read()
    imgOutput = img.copy() # copy of the original image
    hands, img = detector.findHands(img)

    # Create a black area at the bottom for text
    height, width = imgOutput.shape[:2]
    cv2.rectangle(imgOutput, (0, height-100), (width, height), (0, 0, 0), -1)
    
    # Display the current text
    cv2.putText(imgOutput, f"Text: {text}", (10, height-60), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Display instructions
    cv2.putText(imgOutput, "Press SPACE to confirm letter", (10, height-30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # if there's a hand in frame
    if hands:
        hand = hands[0]
        x, y, w, h = hand['bbox'] # get bounding box dimensions

        # just a white image
        imgWhite = np.ones((imgSize,imgSize,3),np.uint8)*255

        # Get the cropped hand image
        imgCrop = img[y-offset : y + h + offset,x - offset : x + w + offset]

        # Check if the crop is valid
        if imgCrop.size == 0:
            cv2.putText(imgOutput, "Please position your hand properly", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.imshow("Image",imgOutput)
            key = cv2.waitKey(1)
            if key == ord("q"):
                break
            continue

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
            prediction, index = classifier.getPrediction(imgWhite,draw=False) # get the prediction and the index
            print(prediction, index) # print the prediction and the index

            # Handle letter detection with cooldown
            if prediction_cooldown <= 0:
                detected_letter = labels[index]
                if detected_letter != last_prediction:
                    current_letter = detected_letter
                    last_prediction = detected_letter
                    letter_ready = True
                    prediction_cooldown = 15

            prediction_cooldown = max(0, prediction_cooldown - 1)

        # if there's a change in width
        else:
            k = imgSize/w
            hcalculated = math.ceil(k*h)
            imgResize = cv2.resize(imgCrop,(imgSize, hcalculated))
            imgResizeShape = imgResize.shape
            hGap = math.ceil((imgSize - hcalculated)/2)

            imgWhite[hGap:hcalculated+hGap, :  ] = imgResize
            prediction, index = classifier.getPrediction(imgWhite,draw=False)

            # Handle letter detection with cooldown
            if prediction_cooldown <= 0:
                detected_letter = labels[index]
                if detected_letter != last_prediction:
                    current_letter = detected_letter
                    last_prediction = detected_letter
                    letter_ready = True
                    prediction_cooldown = 15

            prediction_cooldown = max(0, prediction_cooldown - 1)

        # Draw the bounding box and current letter
        cv2.rectangle(imgOutput, (x - offset, y - offset - 50), (x - offset + 90, y -offset - 50 + 50), (51, 51, 153), cv2.FILLED)
        cv2.putText(imgOutput, current_letter, (x, y-26), cv2.FONT_HERSHEY_COMPLEX, 1.7, (255, 255, 255), 2)
        cv2.rectangle(imgOutput, (x - offset, y - offset), (x + w + offset, y + h + offset), (153, 51, 51), 4)

        # If a letter is ready to be confirmed, show a visual indicator
        if letter_ready:
            cv2.putText(imgOutput, "Ready to confirm!", (width-300, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow("ImageCrop",imgCrop)
        cv2.imshow("ImageWhite",imgWhite)


    cv2.imshow("Image",imgOutput) # show the original image with the bounding box
    key = cv2.waitKey(1)

    # "q" to quit the program
    if key == ord("q"):
        break
    elif key == ord("c"):  # Clear text when 'c' is pressed
        text = ""
    elif key == 32 and letter_ready:  # Spacebar pressed and letter is ready
        if current_letter == 'space':
            text += " "
        elif current_letter == 'del':
            text = text[:-1] if text else ""
        else:
            text += current_letter
        letter_ready = False
        current_letter = ""

cap.release()
cv2.destroyAllWindows()


