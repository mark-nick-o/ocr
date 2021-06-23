#
# Example python script to split label into 2 parts and read the curved 
# label as 2 texts 
#
# You can try for example CW102.jpg in the dataset the co-ordinates have been
# set for that picture to extract the curved "Ivy House Farm" label
# 
# You have to either write these co-ordinates for every image or set it to 
# be the general area in your vision
#
# ref :- https://atatat.hatenablog.com/entry/opencv9_perspective2
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

    img = plt.imread(input_file_path)
    # use CV instead to read 
    # orig2 = cv2.imread(input_file_path)
    # img = cv2.cvtColor(orig2, cv2.COLOR_BGR2RGB)

    # create the output filenames
    fileElements = split('.',input_file_path)
    output_file_path_left  = fileElements[0] + "_trap_left." + fileElements[1]
    output_file_path_right  = fileElements[0] + "_trap_right." + fileElements[1]
    output_file_path1 = fileElements[0] + "_trap_left_rs." + fileElements[1]
    output_file_path2 = fileElements[0] + "_trap_right_rs." + fileElements[1]
    
    # co-ordinates for right hand picture cut and shear trapezoid
    p1 = np.array([510,590])                                            # x1,y1 
    p2 = np.array([590,505])                                            # x2,y2
    p3 = np.array([538,609])                                            # x3,y3 
    p4 = np.array([597,558])                                            # x4,y4	
    o_width = np.linalg.norm(p2 - p1)
    o_width=int(np.floor(o_width))
    o_height = np.linalg.norm(p3 - p1)
    o_height=int(np.floor(o_height))

    ori_cor = np.float32([p1, p2, p3, p4])
    dst_cor=np.float32([[0, 0],[o_width, 0],[0, o_height],[o_width, o_height]])

    M = cv2.getPerspectiveTransform(ori_cor, dst_cor)
    cor_src = cv2.warpPerspective(img, M,(o_width, o_height))
    plt.imsave(output_file_path_left, cor_src)

    # use CV instead to write file
    # cv2.imwrite(output_file_path_left, cor_src)
    
    # if you want to use bottle unwrap the image must be square so we re-size here
    res = cv2.resize(cor_src,(500, 500), interpolation = cv2.INTER_CUBIC)
    plt.imsave(output_file_path1, res)

    # use CV instead to write file
    # cv2.imwrite(output_file_path1, cor_src)
        
    # co-ordinates for left hand picture cut and shear trapezoid
    p1 = np.array([586,516])                                            # x1,y1
    p2 = np.array([697,561])                                            # x2,y2
    p3 = np.array([593,566])                                            # x3,y3
    p4 = np.array([658,614])                                            # x4,y4

    o_width = np.linalg.norm(p2 - p1)
    o_width=int(np.floor(o_width))
    o_height = np.linalg.norm(p3 - p1)
    o_height=int(np.floor(o_height))

    ori_cor = np.float32([p1, p2, p3, p4])
    dst_cor=np.float32([[0, 0],[o_width, 0],[0, o_height],[o_width, o_height]])

    M = cv2.getPerspectiveTransform(ori_cor, dst_cor)
    cor_src = cv2.warpPerspective(img, M,(o_width, o_height))
    plt.imsave(output_file_path_right, cor_src)

    # use CV instead to write file
    # cv2.imwrite(output_file_path_right, cor_src)

    # if you want to use bottle unwrap the image must be square so we re-size here
    res = cv2.resize(cor_src,(500, 500), interpolation = cv2.INTER_CUBIC)
    plt.imsave(output_file_path2, res)

    # use CV instead to write file
    # cv2.imwrite(output_file_path2, cor_src)
    
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
