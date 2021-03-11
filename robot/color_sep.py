#
# use skimage library to extract a particular color from the image
#
# python $0 : this file $1 : color
#
# very good at splitting out vegetation and colored rubbish on conveyor
#
#

#library imports
import sys
import os
import numpy as np
from skimage.io import imread, imshow, imsave
from skimage.color import rgb2gray
from skimage.color import rgb2hsv
import matplotlib.pyplot as plt
from skimage.filters import threshold_otsu

if __name__ == '__main__':
	
    if (len(sys.argv) - 1) <= 0:
        print("please pass the filename for the screenshot you want to analyse 2nd arg can be colorMask : green yelow orangewhite blue red redwhite yellowgreen, if no 2nd arg default green")
        sys.exit()
    
    # ------- read in the requested iamge ---------
    fileNam = "/mnt/c/linuxmirror/" + sys.argv[1]
    if os.path.isfile(fileNam) == False:
	    fileNam = fileNam + ".jpg"
    if os.path.isfile(fileNam) == False:
        print("invalid file name or path %s" % fileNam)	
        sys.exit()
        
    cube = imread(fileNam)
    cube_gray = rgb2gray(cube)
    #imshow(cube_gray)

    # uncomment if you want to look at plot
    #
    #thresh_list = [0.2, 0.3, 0.4, 0.5]
    #fig, ax = plt.subplots(1,4, figsize=(10,10))
    #for i in range(4):
    #    im = ax[i].imshow(cube_gray < thresh_list[i], cmap='gray')
    #    ax[i].set_title(thresh_list[i])
    #plt.show()

    thresh = threshold_otsu(cube_gray)
    cube_binary_otsu2  = cube_gray < thresh
    #imshow(cube_binary_otsu2)
    path_img_target = os.path.join('/mnt/c/linuxmirror/', 'col_sep_o.jpg')
    #diff = diff.astype(np.uint8)
    imsave(path_img_target, cube_binary_otsu2)

    # --------------------- segment the red green and blue -------------
    #        red
    red = cube[:, :, 0] - cube_gray*255
    red2 = np.where(red > 0, red, 0)
    thresh = threshold_otsu(red2)
    red_binary_otsu  = red2 > thresh
    #       green
    green = cube[:, :, 1] - cube_gray*255
    green2 = np.where(green > 0, green, 0)
    thresh = threshold_otsu(green2)
    green_binary_otsu  = green2 > thresh
    #       blue
    blue = cube[:, :, 2] - cube_gray*255
    blue2 = np.where(blue > 0, blue, 0)
    thresh = threshold_otsu(blue2)
    blue_binary_otsu  = blue2 > thresh
    fig,ax = plt.subplots(1,3,figsize=(10,10))
    ax[0].imshow(red_binary_otsu,cmap='gray')
    ax[0].set_title('Reds')
    path_img_target = os.path.join('/mnt/c/linuxmirror/', 'col_sep_r.jpg')
    #diff = diff.astype(np.uint8)
    imsave(path_img_target, red_binary_otsu)
    ax[1].imshow(green_binary_otsu,cmap='gray')
    ax[1].set_title('Greens')
    path_img_target = os.path.join('/mnt/c/linuxmirror/', 'col_sep_g.jpg')
    #diff = diff.astype(np.uint8)
    imsave(path_img_target, green_binary_otsu)
    ax[2].imshow(blue_binary_otsu,cmap='gray')
    ax[2].set_title('Blues')
    path_img_target = os.path.join('/mnt/c/linuxmirror/', 'col_sep_b.jpg')
    #diff = diff.astype(np.uint8)
    imsave(path_img_target, blue_binary_otsu)

    # --------- change to hsv space from rgb using skimage -------------
    cube_hsv = rgb2hsv(cube)

    if (len(sys.argv) - 1) == 2:
        if not sys.argv[2].lower().find("yellowgreen") == -1:           # order by derivative then exact color
            # yellow/green mask 
            lower_mask = cube_hsv[:,:,0] > 0.20
            upper_mask = cube_hsv[:,:,0] < 0.30
        elif not sys.argv[2].lower().find("allgreen") == -1:
            # very light green mask 
            lower_mask = cube_hsv[:,:,0] > 0.10
            upper_mask = cube_hsv[:,:,0] < 0.40
        elif not sys.argv[2].lower().find("green") == -1:
            # green mask hue range for green (widen band for lighter)
            lower_mask = cube_hsv[:,:,0] > 0.30
            upper_mask = cube_hsv[:,:,0] < 0.40
        elif not sys.argv[2].lower().find("yellow") == -1:
            # yellow mask hue range for yellow
            lower_mask = cube_hsv[:,:,0] > 0.10
            upper_mask = cube_hsv[:,:,0] < 0.20
        elif not sys.argv[2].lower().find("orangewhite") == -1:
            # orange/white mask 
            lower_mask = cube_hsv[:,:,0] > 0.0
            upper_mask = cube_hsv[:,:,0] < 0.20
        elif not sys.argv[2].lower().find("blue") == -1:
            # blue mask 
            lower_mask = cube_hsv[:,:,0] > 0.50
            upper_mask = cube_hsv[:,:,0] < 0.60
        elif not sys.argv[2].lower().find("orange") == -1:
            # orange mask 
            lower_mask = cube_hsv[:,:,0] > 0.05
            upper_mask = cube_hsv[:,:,0] < 0.10
        elif not sys.argv[2].lower().find("redwhite") == -1:            
            # red/white mask 
            lower_mask = cube_hsv[:,:,0] > 0.0 
            upper_mask = cube_hsv[:,:,0] < 0.05 
        elif not sys.argv[2].lower().find("red") == -1:
            # red magenta mask 
            lower_mask = cube_hsv[:,:,0] > 0.80
            upper_mask = cube_hsv[:,:,0] < 1.0
        else:
            #green mask hue range for green (widen band for lighter)
            lower_mask = cube_hsv[:,:,0] > 0.30
            upper_mask = cube_hsv[:,:,0] < 0.40
    else:
        #green mask hue range for green (widen band for lighter)
        lower_mask = cube_hsv[:,:,0] > 0.30
        upper_mask = cube_hsv[:,:,0] < 0.40		
                    
    hue_img = cube_hsv[:, :, 0]                                         # hue channel
    value_img = cube_hsv[:, :, 2]                                       # value channel
    mask = upper_mask*lower_mask
    #plt.imshow(mask)
    path_img_target = os.path.join('/mnt/c/linuxmirror/', 'col_sep_2.jpg')
    #diff = diff.astype(np.uint8)
    imsave(path_img_target, mask)

    red = cube[:,:,0]*mask
    green = cube[:,:,1]*mask
    blue = cube[:,:,2]*mask
    cube_masked = np.dstack((red,green,blue))
    #imshow(cube_masked)
    path_img_target = os.path.join('/mnt/c/linuxmirror/', 'col_sep_1.jpg')
    #diff = diff.astype(np.uint8)
    imsave(path_img_target, cube_masked)

    # -------- do a mask on hue and value in HSV space -----------------
    if (len(sys.argv) - 1) == 4:
        hue_threshold = int(sys.argv[3])
        value_threshold = int(sys.argv[4])
    else:    		
        hue_threshold = 0.04
        value_threshold = 0.1
    binary_img = (hue_img > hue_threshold) | (value_img < value_threshold)
    path_img_target = os.path.join('/mnt/c/linuxmirror/', 'col_sep_3.jpg')
    #diff = diff.astype(np.uint8)
    imsave(path_img_target, binary_img)
