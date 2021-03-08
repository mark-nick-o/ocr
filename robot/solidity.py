# based upon code from https://www.oit.ac.jp/is/nishiguchi-lab/?OpenCV-Python+%E6%BC%94%E7%BF%92
# coding: UTF-8
#
#    tutorial_RockScissorPaper.py
#    Read the image, convert it to the HSV color system, extract the skin color area and display it
#    Allow the slider to adjust the range of H, S, V
#    Fill in the defects by expansion / contraction processing
#
import os
import sys
import cv2
import numpy as np
 
# Rock-paper-scissors judgment threshold for solidity
ROCK_MAX = 1.0   # Upper threshold for judging
ROCK_MIN = 0.8   # Lower threshold for judging
 
SCISSOR_MAX = 0.8 # Upper threshold for judging
SCISSOR_MIN = 0.7 # Lower threshold for judging
 
PAPER_MAX = 0.7   # Upper threshold for judging
PAPER_MIN = 0.6   # Lower threshold for judging
 
# Values ​​for each lower and upper limit of the HSV color system
H_MIN = 0   # minimum degree 
H_MAX= 180  # Degree (assumed to go around at 180 degrees)
S_MIN = 0   # Representing 0.0 <-> 1.0 with 0 <-> 255
S_MAX = 255 # Representing 0.0 <-> 1.0 with 0 <-> 255
V_MIN = 0   # Representing 0.0 <-> 1.0 with 0 <-> 255
V_MAX = 255 # Representing 0.0 <-> 1.0 with 0 <-> 255
 
# Initial value of each variable
hMin = H_MIN
hMax = H_MAX
sMin = S_MIN
sMax = S_MAX
vMin = V_MIN
vMax = V_MAX
 
# frame name
WIN_NAME ='frame'
 
# Callback function when the slider is called
def setHMin(val):
# Add global when referencing a global variable from within a function
    global hMin
    hMin = val
 
def setHMax(val):
    global hMax
    hMax = val
 
def setSMin(val):
    global sMin
    sMin = val
 
def setSMax(val):
    global sMax
    sMax = val
 
def setVMin(val):
    global vMin
    vMin = val
 
def setVMax(val):
    global vMax
    vMax = val
 

#    Generate a mask image where the pixels corresponding to the skin-colored pixels are 255 and the pixels that are not are 0.
def extractSkinMask(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Define skin color range in HSV space
    # 0 <= hue <= 15, 50 <= saturation <= 255, 50 <= value <= 255
    lower_skin = np.array([hMin,sMin,vMin])    
    upper_skin = np.array([hMax,sMax,vMax])
    # Threshold for extracting only blue objects from HSV images
    mask = cv2.inRange(hsv, lower_skin, upper_skin)
    return mask

#    Complementing missing areas by expansion / contraction processing
def interpolate(mask):
    kernel = np.ones((5,5),np.uint8)
    # Expansion process
    dilation = cv2.dilate(mask, kernel, iterations = 2)
    # Reduction processing
    mask = cv2.erode(dilation, kernel, iterations = 2)

    return mask

# Find the area with the maximum number of pixels from some areas
# Argument: Binary image with several blobs
# Return value: Number of pixels included in the area, image of only the area with the maximum number of pixels
def getMaximumBlob(mask):
    # Labeling process
    # The argument is a binary image with a background of 0 and an object other than 0.
    # The return value is the number of objects, the background is 0, the label image with the value of 1 or more 
    # objects, each outline, the position of the center of gravity of each object.
    nlabels, labelimg, contours, CoGs = cv2.connectedComponentsWithStats(mask)

    if nlabels > 0:
        maxLabel = 0
        maxSize = 0
        for nlabel in range(1,nlabels):
            x,y,w,h,size = contours[nlabel]
            xg,yg = CoGs[nlabel]
            if maxSize < size:
                maxSize = size
                maxLabel = nlabel
        # Set the pixel value with the label representing the maximum area to 255 (white)
        mask[labelimg == maxLabel] = 255
        # Set all other areas to 0 (black)
        mask[labelimg != maxLabel] = 0

        return maxSize, mask
    else:
        return maxSize, mask

# Find the polygon (convex hull) that circumscribes the region
# Argument: Binary image containing only one blob
# Return value: Number of pixels in the polygon, list of points representing the corners of the polygon, 
# list of points on the outline of the original area
def getConvexHull(mask):

    # Detect contour
    #image, contours, hierarchy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    # no longer returns image after verison 3.2
    (major, minor, _) = cv2.__version__.split(".")
    if (int(major) == 3 and int(minor) > 2) or (int(major) >= 4):
        #contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours, hierarchy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
        #contours, hierarchy = cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    else:
        image, contours, hierarchy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    hull = cv2.convexHull(contours[0], returnPoints = True)
    hullSize = cv2.contourArea(hull)
    return hullSize, hull, contours[0]

# Rock-paper-scissors hand judgment based on 
# Solidity (ratio of contour area to area of ​​convex hull (smallest circumscribed polygon surrounding the area))
# Argument: Number of pixels included in the blob
# Return value: Number of pixels contained in the circumscribed polygon of the blob
def decide(handBlob, handHull):
    choice = -1
    solidity = 0

    if handHull != 0:
        solidity = handBlob / handHull
        if ROCK_MIN <= solidity and solidity <= ROCK_MAX:
            choice = 0
        elif SCISSOR_MIN <= solidity and solidity <= SCISSOR_MAX:
            choice = 1
        elif PAPER_MIN <= solidity and solidity <= PAPER_MAX:
            choice = 2
        else:
            choice = -1
 
    return choice, solidity
 
def tutorial_RockScissorPaper():
   
    if (len(sys.argv) - 1) <= 0:
        print("please pass the filename for the screenshot you want to analyse")
        sys.exit()
        
    # ------- read in the requested iamge ---------
    fileNam = "/mnt/c/linuxmirror/" + sys.argv[1]
    if os.path.isfile(fileNam) == False:
	    fileNam = fileNam + ".jpg"
    if os.path.isfile(fileNam) == False:
        print("invalid file name or path %s" % fileNam)	
        sys.exit()
    img = cv2.imread(fileNam, cv2.IMREAD_UNCHANGED)

    # set up from arguments if they were specified 
    if (len(sys.argv) - 1) == 7:
        if int(sys.argv[2]) >= H_MIN:
            setHMin(int(sys.argv[2]))   
        if int(sys.argv[3]) <= H_MAX:
            setHMax(int(sys.argv[3]))   
        if int(sys.argv[4]) >= S_MIN:
            setSMin(int(sys.argv[4]))   
        if int(sys.argv[5]) <= S_MAX:
            setSMin(int(sys.argv[5])) 
        if int(sys.argv[6]) >= V_MIN:
            setSMin(int(sys.argv[6]))   
        if int(sys.argv[7]) <= V_MAX:
            setSMin(int(sys.argv[7]))    
    
    # extract from the iamge the mask
    mask = extractSkinMask(img)
    mask = interpolate(mask)
    maxSize, maxBlob = getMaximumBlob(mask)
    print(maxBlob)
    hullSize, hull, contour = getConvexHull(maxBlob)
    img = cv2.drawContours(img, contour, -1, (255, 255,0), 3)

    # Drawing: Pass a list with only one hull list as the second argument
    img = cv2.drawContours(img, [hull], 0, (0, 255, 0), 2)

    # Judgment
    choice, solidity = decide(maxSize, hullSize)
    
    if choice == 0:
        print("Rock: solidity = ", solidity)
    elif choice == 1:
        print("Scissors: solidity = ", solidity)           
    elif choice == 2:
        print("Paper: solidity = ", solidity)
    else:
        print("Unknown: solidity = ", solidity)
        
    equi_diameter = np.sqrt(4*maxSize/np.pi)
    print("equivalent diameter %d" % equi_diameter)
    
    cv2.imwrite('/mnt/c/linuxmirror/rock0.jpg', img)   
    
    # -------- count the objects ---------------------------------------
    # get binary image and apply Gaussian blur
    objects = cv2.imread(fileNam, cv2.IMREAD_UNCHANGED)
    objects_gray = cv2.cvtColor(objects, cv2.COLOR_BGR2GRAY)
    objects_preprocessed = cv2.GaussianBlur(objects_gray, (5, 5), 0)
 
    # get binary image options are :  THRESH_BINARY THRESH_TRUNC or THRESH_TOZERO
    _, objects_binary = cv2.threshold(objects_preprocessed, 130, 255, cv2.THRESH_BINARY)

    # invert image to get objects
    objects_binary = cv2.bitwise_not(objects_binary)

    # find contours
    objects_contours, _ = cv2.findContours(objects_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
 
    # make copy of image
    objects_and_contours = np.copy(objects)
 
    # find contours of large enough area
    min_coin_area = 60
    large_contours = [cnt for cnt in objects_contours if cv2.contourArea(cnt) > min_coin_area]
 
    # draw contours
    cv2.drawContours(objects_and_contours, large_contours, -1, (255,0,0))
 
    # print number of contours
    print('number of objects: %d' % len(large_contours))  
    cv2.imwrite('/mnt/c/linuxmirror/rock1.jpg', objects_and_contours)  

if __name__ == '__main__':

    tutorial_RockScissorPaper()
