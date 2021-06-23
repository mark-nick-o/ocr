#
# ref : https://atatat.hatenablog.com/entry/opencv9_perspective2
# ref : https://qiita.com/mix_dvd/items/5674f26af467098842f0
#
# Perform trapezoid correction processing
# coordinates are automatically extracted from the image using contour extraction.
#
# warning this does not always produce all the co-ordinates so sometimes
# you must use display co-ordinates and use the trapezoid functions
#
# a working example picture file in the folder is mixdvd1.jpeg
#
import os
import sys
import cv2
import numpy as np
from matplotlib import pyplot as plt
import imutils
import re
from IPython.display import display, Image

#
# split string by delimeter 
#
def split(delimiters, string, maxsplit=0):
    regexPattern = '|'.join(map(re.escape, delimiters))
    return re.split(regexPattern, string, maxsplit)
    
#
# use to display image if you want 
#
def display_cv_image(image, format='.png'):
    decoded_bytes = cv2.imencode(format, image)[1].tobytes()
    display(Image(data=decoded_bytes))

if __name__ == '__main__':
	
# ========= check the options passed had at least 1 parameter (file) ===
    if (len(sys.argv) - 1) <= 0:
        print("Please pass the filename for the screenshot you want to analyse \n plus 0/1 where 0=grayscale 1=HSV image used")
        sys.exit(ERR_NO_FILE)

# ========= define error return codes from the script ==================
    ERR_NO_FILE = 1                                                     # you may query this with echo $? in shell
    ERR_INVALID_OPTION = 2      
    ERR_NO_AREA_FOUND = 3 
    ERR_NO_TRANSFORM = 4        
    
# ======== get the name of the file to check ===========================
    fileNam = "/mnt/c/linuxmirror/" + sys.argv[1]
    if os.path.isfile(fileNam) == False:
	    fileNam = fileNam + ".jpg"
    if os.path.isfile(fileNam) == False:
        print("invalid file name or path %s" % fileNam)	
        sys.exit(ERR_NO_FILE)
    if (len(sys.argv) -1) > 1:
        try :            
            SELECT_HSV_IMAGE = int(sys.argv[2])
        except :		 
            print("invalid 2nd option must be 1 or 0")
            sys.exit(ERR_INVALID_OPTION)
        print("using alternate image type as %d" % (SELECT_HSV_IMAGE))
    else:
       SELECT_HSV_IMAGE = 0	              


    # create the output filenames
    fileElements = split('.',fileNam)
    output_file_con_gray  = fileElements[0] + "_con_gray." + fileElements[1]
    output_file_contours  = fileElements[0] + "_contours." + fileElements[1]
    output_file_con_out1 = fileElements[0] + "_con_out1." + fileElements[1]
    output_file_con_out2 = fileElements[0] + "_con_out2." + fileElements[1]
    output_file_con_out3 = fileElements[0] + "_con_out3." + fileElements[1]
        
# ======= read the input file ==========================================
    img = cv2.imread(fileNam, cv2.IMREAD_UNCHANGED)
    src = cv2.imread(fileNam, cv2.IMREAD_UNCHANGED)

# ======== convert to greyscale ========================================
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# ======= Binarization =================================================
    ret,th1 = cv2.threshold(gray,200,255,cv2.THRESH_BINARY)
    cv2.imwrite(output_file_con_gray, th1)

# ======== this is an alternative which will use an HSV iamge instead
    img_HSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    img_HSV = cv2.GaussianBlur(img_HSV, (9, 9), 3)
    img_H, img_S, img_V = cv2.split(img_HSV)
    _thre, hsv_image = cv2.threshold(img_H, 140, 255, cv2.THRESH_BINARY)

# ======== Contour extraction ==========================================

    contours = cv2.findContours(th1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[1] if imutils.is_cv3() else contours[0]  

    # find contours works with 3 retruns in cv3 otherwise 2 (methods are same
    # depends which you like)
    #
    if SELECT_HSV_IMAGE != 0:
        if imutils.is_cv3():
            image, contours, hierarchy = cv2.findContours(hsv_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        else:
            contours, hierarchy = cv2.findContours(hsv_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)	
    else:
        contours = cv2.findContours(th1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[1] if imutils.is_cv3() else contours[0]
          			          
    # Select only those with a large area
    areas = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 10000:
        #if area > 100: <------------          if you want a smaller one
           epsilon = 0.1*cv2.arcLength(cnt,True)
           approx = cv2.approxPolyDP(cnt,epsilon,True)
           areas.append(approx)

    cv2.drawContours(img,areas,-1,(0,255,0),3)
    cv2.imwrite(output_file_contours, img)
    #display_cv_image(img)

    try:
        pt1ind=np.argmin(areas[0],axis=0)[0][0]
    except :
        print("no area found")
        sys.exit(ERR_NO_AREA_FOUND)

    pt1=areas[0][pt1ind]                                                # upper left co-ordinate x.y
    pt2ind=np.argmin(areas[0],axis=0)[0][1]
    pt2=areas[0][pt2ind]                                                # upper right co-ordinate x.y
    pt3ind=np.argmax(areas[0],axis=0)[0][1]
    pt3=areas[0][pt3ind]                                                # lower left co-ordinate x.y
    pt4ind=np.argmax(areas[0],axis=0)[0][0]
    pt4=areas[0][pt4ind]                                                # lower right co-ordinate x.y
    pts = np.float32(np.array([pt1,pt2,pt3,pt4]))
    o_width = np.linalg.norm(pt2 - pt1)
    o_width=int(np.floor(o_width))
    o_height = np.linalg.norm(pt3 - pt1)
    o_height=int(np.floor(o_height))
    dst_cor=np.float32([[0,0],[o_width,0],[0, o_height],[o_width, o_height]])

    try :
        M = cv2.getPerspectiveTransform(pts,dst_cor)
    except :
        print("error processing Transform")
        sys.exit(ERR_NO_TRANSFORM)       
    dst = cv2.warpPerspective(src,M,(o_width,o_height))
    cv2.imwrite(output_file_con_out1, dst)
        
    dst2 = cv2.warpPerspective(th1,M,(o_width,o_height))
    cv2.imwrite(output_file_con_out2, dst2)
        
    # Projection conversion
    # Converts each point in the frame to the corresponding coordinates.

    dst = []
    pts1 = np.float32(areas[0])
    pts2 = np.float32([[600,300],[600,0],[0,0],[0,300]])
    try :
        M = cv2.getPerspectiveTransform(pts1,pts2)
    except :
        print("error processing Transform")
        sys.exit(ERR_NO_TRANSFORM)
    dst = cv2.warpPerspective(img,M,(600,300))
    #display_cv_image(dst)
    cv2.imwrite(output_file_con_out3, dst)


# ======================================================================
#
# to run the ocr on the output image array to return a text seen 
#
# import pyocr
# from PIL import Image
# tools = pyocr.get_available_tools()
# tool = tools[0]
# print(tool.image_to_string(Image.fromarray(dst), lang="jpn"))
