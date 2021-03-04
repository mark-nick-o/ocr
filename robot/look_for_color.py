#
# look for color a useful set of operations which can help identify
# objects of a certain color
# it might be want to use this if we are getting no ansert from the ocr
# becuase of a noisy background for example
#
import sys
import os
import numpy as np
import cv2

if __name__ == '__main__':
	
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

    if (len(sys.argv) - 1) == 7:
        lower_skin = np.array([int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4])])
        upper_skin = np.array([int(sys.argv[5]),int(sys.argv[6]),int(sys.argv[7])]) 
    else: 
    ## skin color defined
    #    
        lower_skin = np.array([0,50,50])
        upper_skin = np.array([15,255,255]) 
   
    # set to hsv space
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # threshold for hue channel in blue range
    blue_min = np.array([80, 100, 100], np.uint8)
    blue_max = np.array([200, 255, 255], np.uint8)
    threshold_blue_img = cv2.inRange(img_hsv, blue_min, blue_max)
    threshold_blue_img = cv2.cvtColor(threshold_blue_img, cv2.COLOR_GRAY2RGB)
    cv2.imwrite('/mnt/c/linuxmirror/color_blu_1.jpg', threshold_blue_img) 
    
    # threshold for hue channel in green range
    grn_min = np.array([100, 80, 100], np.uint8)
    grn_max = np.array([255, 200, 255], np.uint8)
    threshold_grn_img = cv2.inRange(img_hsv, grn_min, grn_max)
    threshold_grn_img = cv2.cvtColor(threshold_grn_img, cv2.COLOR_GRAY2RGB)
    cv2.imwrite('/mnt/c/linuxmirror/color_green_1.jpg', threshold_grn_img) 

    # threshold for hue channel in red range
    red_min = np.array([100, 100, 80], np.uint8)
    red_max = np.array([255, 255, 200], np.uint8)
    threshold_red_img = cv2.inRange(img_hsv, red_min, red_max)
    threshold_red_img = cv2.cvtColor(threshold_red_img, cv2.COLOR_GRAY2RGB)
    cv2.imwrite('/mnt/c/linuxmirror/color_red_1.jpg', threshold_red_img) 
    
    # threshold on all color
    # get mask of pixels that are in blue range
    mask_inverse = cv2.inRange(img_hsv, blue_min, blue_max)
 
    # inverse mask to get parts that are not blue
    mask = cv2.bitwise_not(mask_inverse)
    #plt.imshow(cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB))
    result = cv2.bitwise_and(img, img, mask = mask)
    cv2.imwrite('/mnt/c/linuxmirror/color_all_2.jpg', result)  
         
    # convert single channel mask back into 3 channels
    mask_rgb = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
 
    # perform bitwise and on mask to obtain cut-out image that is not blue
    masked_upstate = cv2.bitwise_and(img, mask_rgb)
 
    # replace the cut-out parts with white
    masked_replace_white = cv2.addWeighted(masked_upstate, 1, \
                                       cv2.cvtColor(mask_inverse, cv2.COLOR_GRAY2RGB), 1, 0)
    cv2.imwrite('/mnt/c/linuxmirror/color_all_1.jpg', masked_replace_white)    

    ## skin color defined
    #    
    
    # threshold on all color
    # get mask of pixels that are in blue range
    mask = cv2.inRange(img_hsv, lower_skin, upper_skin)
 
    #plt.imshow(cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB))
    result = cv2.bitwise_and(img, img, mask = mask)
    cv2.imwrite('/mnt/c/linuxmirror/color_skin_1.jpg', result)         
