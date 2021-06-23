#
# Function to warp and rotate an image
#
import cv2
import numpy as np
from matplotlib import pyplot as plt
import os
import sys
import re

# good example files to show effect
#       input_file_path = "/mnt/c/linuxmirror/CW200.jpg" 
#       input_file_path = "/mnt/c/linuxmirror/CW122.jpg" 

#
# split string by delimeter 
#
def split(delimiters, string, maxsplit=0):
    regexPattern = '|'.join(map(re.escape, delimiters))
    return re.split(regexPattern, string, maxsplit)
    
if __name__ == '__main__':

# from google.colab import files
# uploaded_file = files.upload()
# orig = cv2.imread(uploaded_file_name)
	
# ========= check the options passed had at least 1 parameter (file) ===
    if (len(sys.argv) - 1) <= 0:
        print("Please pass the filename for the screenshot you want to analyse plus 0/1 <num> \n where 0=left 1=right rotation \n <num> is angle of extra rotation if needed")
        sys.exit()

# ========= define error return codes from the script ==================
    ERR_NO_FILE = 1                                                     # you may query this with echo $? in shell
    ERR_INVALID_OPTION = 2      
    ERR_NO_AREA_FOUND = 3 
    ERR_NO_TRANSFORM = 4        

    ROT_DIRECTION_LEFT = 0
    ROT_DIRECTION_RIGHT = 1
        
# ======== get the name of the file to check ===========================

    fileNam = "/mnt/c/linuxmirror/" + sys.argv[1]
    if os.path.isfile(fileNam) == False:
	    fileNam = fileNam + ".jpg"
    if os.path.isfile(fileNam) == False:
        print("invalid file name or path %s" % fileNam)	
        sys.exit(ERR_NO_FILE)
        
    if (len(sys.argv) -1) > 1:
        try :            
            ROT_DIRECTION_IMAGE = int(sys.argv[2])
        except :		 
            print("invalid 2nd option must be 1 or 0")
            sys.exit(ERR_INVALID_OPTION)
        print("using alternate image type as %d" % (ROT_DIRECTION_IMAGE))
    else:
       ROT_DIRECTION_IMAGE = ROT_DIRECTION_LEFT	              

    if (len(sys.argv) -1) > 2:
        try :            
            ROTATION_ANGLE = float(sys.argv[3])
        except :		 
            print("invalid 3rd option must be rotation angle number")
            sys.exit(ERR_INVALID_OPTION)
        print("set rotation angle as %f" % (ROTATION_ANGLE))
        EXTRA_ROTATE = 1
    else:
       EXTRA_ROTATE = 0	
       
    # create the output filenames
    fileElements = split('.',fileNam)
    output_file_1  = fileElements[0] + "_warp_1.jpg"
    output_file_2  = fileElements[0] + "_warp_2.jpg"
    output_file_3 = fileElements[0] + "_warp_3.jpg" 
             
    input_file_path = fileNam

    orig = cv2.imread(input_file_path)
    src = cv2.cvtColor(orig, cv2.COLOR_BGR2RGB)

    #
    # interpolation is the interpolation method of pixels when resized, 
    # and cv2. INTER_CUBIC (slow) or cv2. INTER_LINEAR is used, and 
    # when shrinking, cv2. INTER_AREA is used
    #
    height, width = src.shape[:2]
    res = cv2.resize(src,(2*width, 2*height), interpolation = cv2.INTER_CUBIC)
    # ========== if you need to look at them
    #plt.subplot(1,2,1)
    #plt.imshow(src)
    #plt.subplot(1,2,2)
    #plt.imshow(res)

    tx=100
    ty=50
    M = np.float32([[1,0,tx],[0,1,ty]])
    dst = cv2.warpAffine(src,M,(width,height))

    # The image is reduced to 0.6, a matrix M2 rotating 90°
    M2 = cv2.getRotationMatrix2D((int(width/2),int(height/2)),90,0.6)
    rot = cv2.warpAffine(src,M2,(width,height))
    plt.imsave(output_file_1, rot)

    # ============= if google drive 
    #uploaded_file2 = files.upload()
    #uploaded_file_name2 = next(iter(uploaded_file2))
    #orig2 = cv2.imread(uploaded_file_name2)
    orig2 = cv2.imread(input_file_path)
    src2 = cv2.cvtColor(orig2, cv2.COLOR_BGR2RGB)

    # Three pairs are prepared as corresponding points of the input image pts1 
    # and the output image pts2, and the matrix formula M3 of the affine 
    # conversion is calculated
    rows,cols,ch = src2.shape
    #
    # tilt it to the left
    #
    if ROT_DIRECTION_IMAGE == ROT_DIRECTION_LEFT:
        pts1 = np.float32([[50,50],[200,50],[50,200]])
        pts2 = np.float32([[10,100],[200,50],[100,250]])
    else : 
    #
    # tilt it to the right
    #
        pts1 = np.float32([[10,100],[200,50],[100,250]])
        pts2 = np.float32([[50,30],[250,100],[50,200]])

    M3 = cv2.getAffineTransform(pts1,pts2)
    aff = cv2.warpAffine(src2,M3,(cols,rows))
    # image after the affine conversion
    plt.imsave(output_file_2, aff)

    #
    # further rotatation when requested
    #
    if EXTRA_ROTATE == 1:
        if ROT_DIRECTION_IMAGE == ROT_DIRECTION_LEFT:
            M2 = cv2.getRotationMatrix2D((int(width/2),int(height/2)),-ROTATION_ANGLE,1.1)
            rot = cv2.warpAffine(aff, M2, (width,height))
        else :
            M2 = cv2.getRotationMatrix2D((int(width/2),int(height/2)),ROTATION_ANGLE,1.1)
            rot = cv2.warpAffine(aff, M2, (width,height))

        plt.imsave(output_file_3, rot)
