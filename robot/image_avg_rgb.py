import sys
import os
import numpy as np
import cv2

if __name__ == '__main__':
	
    if (len(sys.argv) - 1) <= 0:
        print("please pass the filename for the screenshot you want to analyse it gives an average color for the image R:G:B")
        sys.exit()
    
    # ------- read in the requested iamge ---------
    fileNam = "/mnt/c/linuxmirror/" + sys.argv[1]
    if os.path.isfile(fileNam) == False:
	    fileNam = fileNam + ".jpg"
    if os.path.isfile(fileNam) == False:
        print("invalid file name or path %s" % fileNam)	
        sys.exit()
    img = cv2.imread(fileNam, cv2.IMREAD_UNCHANGED)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # find average per row, assuming image is already in the RGB format.
    # np.average() takes in an axis argument which finds the average across that axis.
    average_color_per_row = np.average(img_rgb, axis=0)
    # find average across average per row
    average_color = np.average(average_color_per_row, axis=0)
    # convert back to uint8
    average_color = np.uint8(average_color)
    print(average_color)
