import sys
import os
import numpy as np
import cv2

if __name__ == '__main__':
	
    if (len(sys.argv) - 1) <= 0:
        print("please pass the filename for the screenshot you want to analyse")
        sys.exit()

    if (len(sys.argv) - 1) == 4:
        scale_delta = int(sys.argv[2])
        scale_min = int(sys.argv[3])
        scale_max = int(sys.argv[4])
    else: 
        scale_delta = 10                                                # % by which we change size per iteration
        scale_min = 20                                                  # starting lowest % scale change
        scale_max = 150                                                 # finishing highes % scale change
    scale_percent = scale_min                                           # % of original scale you want start the scale at smallest change in size to the original
    iterNum = 1                                                         # file number or iteration count
    
    # ------- read in the requested iamge ---------
    fileNam = "/mnt/c/linuxmirror/" + sys.argv[1]
    if os.path.isfile(fileNam) == False:
        fileNam = fileNam + ".jpg"
    if os.path.isfile(fileNam) == False:
        print("invalid file name or path %s" % fileNam)	
        sys.exit()
    img = cv2.imread(fileNam, cv2.IMREAD_UNCHANGED)
    
    while scale_percent < scale_max:
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        rSizNam = "/mnt/c/linuxmirror/resize" + str(iterNum) + ".jpg"
        print("writing %s" % rSizNam)
        cv2.imwrite(rSizNam, resized)
        scale_percent = scale_percent + scale_delta                     # iterate from scale min to max 
        iterNum += 1
