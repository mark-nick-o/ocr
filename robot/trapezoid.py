#
# Example python script to get sign from photo as label
#
# You can try for example test_sign.png in the dataset the co-ordinates have been
# set for that picture to extract the sign
# 
# You have to either write these co-ordinates for every image or set it to 
# be the general area in your vision
#
# ref:- https://atatat.hatenablog.com/entry/opencv8_perspective
#
import os
import sys
import cv2
import numpy as np
import math
from matplotlib import pyplot as plt
import re
 
# Ratio adjustment
w_ratio = 1.1
 
def split(delimiters, string, maxsplit=0):
    regexPattern = '|'.join(map(re.escape, delimiters))
    return re.split(regexPattern, string, maxsplit)

def run_trapezoid(input_file_path):

    orig2 = cv2.imread(input_file_path)
    img = cv2.cvtColor(orig2, cv2.COLOR_BGR2RGB)

    # create the output filenames
    fileElements = split('.',input_file_path)
    output_file_path  = fileElements[0] + "_trap." + fileElements[1]
    output_file_path1 = fileElements[0] + "_trap_square." + fileElements[1]

    #    Read the 4 co-ordinates defining the region to pull out of picture
    #
    #    x1,y1              x2,y2
    #
    #    x3,y3              x4,y4
    #
    p1 = np.array([46,159])                                             # x1,y1 Upper left
    p2 = np.array([421,64])                                             # x2,y2 Upper right
    p3 = np.array([38,246])                                             # x3,y3 Bottom Left
    p4 = np.array([428,174])                                            # x4,y4 Bottom Right
    
    o_width = np.linalg.norm(p2 - p1)
    o_width=int(np.floor(o_width))
    o_height = np.linalg.norm(p3 - p1)
    o_height=int(np.floor(o_height))

    ori_cor = np.float32([p1, p2, p3, p4])
    dst_cor=np.float32([[0, 0],[o_width, 0],[0, o_height],[o_width, o_height]])

    M = cv2.getPerspectiveTransform(ori_cor, dst_cor)
    cor_src = cv2.warpPerspective(img, M,(o_width, o_height))
    cv2.imwrite(output_file_path, cor_src)

    # if you want to use bottle unwrap the image must be square so we re-size here
    res = cv2.resize(cor_src,(500, 500), interpolation = cv2.INTER_CUBIC)
    cv2.imwrite(output_file_path1, res)

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
    
    run_trapezoid(fileNam)
