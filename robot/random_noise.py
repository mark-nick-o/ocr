#
# Example of putting random noise into a picture to try to decipher it
#
import cv2
import numpy as np
from matplotlib import pyplot as plt
import os
import sys
import re

#
# split string by delimeter 
#
def split(delimiters, string, maxsplit=0):
    regexPattern = '|'.join(map(re.escape, delimiters))
    return re.split(regexPattern, string, maxsplit)

if __name__ == '__main__':
	
# ========= check the options passed had at least 1 parameter (file) ===
    if (len(sys.argv) - 1) <= 0:
        print("Please pass the filename for the screenshot you want to analyse \n plus 0/1 where 0=left 1=right rotation")
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
        print("using alternate image type as %d" % (SELECT_HSV_IMAGE))
    else:
       ROT_DIRECTION_IMAGE = ROT_DIRECTION_LEFT	              

    # create the output filenames
    fileElements = split('.',fileNam)
    output_file_1  = fileElements[0] + "_random_1.jpg"
    output_file_2  = fileElements[0] + "_random_2.jpg"
    output_file_3 = fileElements[0] + "_random_3.jpg" 
    output_file_4 = fileElements[0] + "_random_4.jpg" 
    output_file_5 = fileElements[0] + "_random_5.jpg" 
    output_file_6 = fileElements[0] + "_random_6.jpg" 
    output_file_7 = fileElements[0] + "_random_7.jpg" 
    output_file_8 = fileElements[0] + "_random_8.jpg"
             
    input_file_path = fileNam

    # read and convert image
    orig = cv2.imread(input_file_path)
    src = cv2.cvtColor(orig, cv2.COLOR_BGR2RGB)

    # apply random noise to the image
    sig=70
    noise=np.random.normal(0,sig,np.shape(src))
    imgnoi=src+np.floor(noise)                                          # Add noise to images
    imgnoi[imgnoi>255]=255                                              # 255 if exceed 255
    imgnoi[imgnoi<0]=0                                                  # 0 if exceed 0
    imgnoi2=imgnoi.astype(np.uint8)                                     # make byte type
    #plt.imshow(imgnoi2)
    plt.imsave(output_file_1, imgnoi2)

    # apply blur to image
    blur2 = cv2.blur(imgnoi2,(10,10))
    plt.imsave(output_file_2, blur2 )

    # apply gauss filter
    gauss2 = cv2.GaussianBlur(imgnoi2,(11,11),1,1)
    gauss3 = cv2.GaussianBlur(blur2,(11,11),1,1)
    # without blur
    plt.imsave(output_file_3, gauss2 )
    # the one with blur
    plt.imsave(output_file_4, gauss3 )

    # apply bilateral filter
    bilat = cv2.bilateralFilter(imgnoi2,25,75,75)
    # to the gauss image
    bilat2 = cv2.bilateralFilter(gauss2,25,75,75)
    # to the random noise image
    plt.imsave(output_file_5, bilat )
    # the one with gauss
    plt.imsave(output_file_6, bilat2 )

    # using gray scaling of either image or the transposed image
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    ret,th1 = cv2.threshold(gray,200,255,cv2.THRESH_BINARY)
    cv2.imwrite(output_file_7, th1)

    gray = cv2.cvtColor(bilat2, cv2.COLOR_BGR2GRAY)
    ret,th1 = cv2.threshold(gray,200,255,cv2.THRESH_BINARY)
    cv2.imwrite(output_file_8, th1)
