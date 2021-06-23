#
# a simple script to find contours round an object
# ref :- https://axa.biopapyrus.jp/ia/opencv/detect-contours.html
#
import os
import sys
import cv2
import numpy as np
import imutils
import re
    
def split(delimiters, string, maxsplit=0):
    regexPattern = '|'.join(map(re.escape, delimiters))
    return re.split(regexPattern, string, maxsplit)
    
def run_contours(fileName):
	
    # load image, change color spaces, and smoothing
    img = cv2.imread(fileName)
    img_HSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    img_HSV = cv2.GaussianBlur(img_HSV, (9, 9), 3)

    # detect objects
    img_H, img_S, img_V = cv2.split(img_HSV)
    _thre, img_flowers = cv2.threshold(img_H, 140, 255, cv2.THRESH_BINARY)
    # if you want to check the mask file uncomment here ---> cv2.imwrite('/mnt/c/linuxmirror/tulips_mask.jpg', img_flowers)

    # find objects cv3 returns 3 parameters rather than 2 in cv2 and cv4
    #
    if imutils.is_cv3():
        labels, contours, hierarchy = cv2.findContours(img_flowers, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    else:
        contours, hierarchy = cv2.findContours(img_flowers, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    
    for i in range(0, len(contours)):
        if len(contours[i]) > 0:

            # remove small objects
            if cv2.contourArea(contours[i]) < 500:
                continue

            cv2.polylines(img, contours[i], True, (255, 55, 255), 5)

    # save
    fileElements = split('.',fileName)
    newWriteFileName = fileElements[0] + "_boundingbox." + fileElements[1]
    cv2.imwrite(newWriteFileName, img)

if __name__ == '__main__':

    if (len(sys.argv) - 1) <= 0:
        print("please pass the filename for the picture want to analyse")
        sys.exit()
    
    # ------- read in the requested image ---------
    fileNam = "/mnt/c/linuxmirror/" + sys.argv[1]
    if os.path.isfile(fileNam) == False:
	    fileNam = fileNam + ".jpg"
    if os.path.isfile(fileNam) == False:
        print("invalid file name or path %s" % fileNam)	
        sys.exit()
    
    run_contours(fileNam)
