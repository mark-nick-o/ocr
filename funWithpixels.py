#
# This script is fun with pixels open cv demo
#
# either to look for something in the picture
# extend or swap the colour
# or run random effects on stills or video for visual art
# look for motion
#
#
#
import cv2
import numpy as np
import math
import random

from scipy.ndimage import gaussian_filter
from scipy import ndimage

# ======= Adjust gamma =================================================
#
# this function from
# https://github.com/ZlodeiBaal/BirdProject/blob/51d4793f68eaba33dd598699a1f7637d1b379523/SqNet/Train.py
#
def adjust_gamma(image, gamma=1.0):
    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")

    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)
    
# ======= Random noize effect ==========================================
#
# this function from
# https://github.com/ZlodeiBaal/BirdProject/blob/51d4793f68eaba33dd598699a1f7637d1b379523/SqNet/Train.py
#
def AddNoize(i):
    R = random.randint(0, 1)
    if (R==1):
        i=np.fliplr(i)#random mirroring
    R = random.randint(0, 1)
    if (R==1):
        R = random.randint(-10, 10)
        i= ndimage.interpolation.rotate(i,R)#random rotation
    R = random.randint(0, 1)
    if (R==1):
        crop_left=random.randint(0,15)
        crop_right = random.randint(1, 15)
        crop_top = random.randint(0, 15)
        crop_bot = random.randint(1, 15)
        i=i[crop_left:-crop_right,crop_top:-crop_bot,:] #Randomcrop
    #Next code is VERY SLOW becoase it use Python to change brightness
    #need to optimase it, but i have no time yet:)
    R = random.randint(0, 2)
    if (R==2): #Random brightness in R channel
        d = random.random()+1
        i[:, :, 0] = adjust_gamma(i[:,:,0],d)
    R = random.randint(0, 2)
    if (R==2): #Random brightness in G channel
        d = random.random()+1
        i[:, :, 1] = adjust_gamma(i[:, :, 1], d)
    R = random.randint(0, 2)
    if (R==2): #Random brightness in B channel
        d = random.random()+1
        i[:, :, 2] = adjust_gamma(i[:, :, 2], d)
    #misc.imsave("test.jpg",i)
    return i

# ======= Edging =======================================================    
#
# modified the kirsch function to max out 
#
def kirschMyfun(image):
    val = image.shape
    m = val[0]
    n = val[1]
    step = 1
    ps = np.array(image)
    kirsch = np.zeros([m, n, 3], dtype=np.uint8)
    for x in range(0, m-2):
        for y in range(0, n-2):
            p1 = ps[y * step, x]
            p2 = ps[y * step, (x + 1)]
            p3 = ps[y * step, (x + 2)]
            p4 = ps[(y + 1) * step, x]
            p5 = ps[(y + 1) * step, (x + 1)]
            p6 = ps[(y + 1) * step, (x + 2)]
            p7 = ps[(y + 2) * step, x]
            p8 = ps[(y + 2) * step, (x + 1)]
            p9 = ps[(y + 2) * step, (x + 2)]
	        # obtain (I + 1, j + 1) gray around nine points
            a = abs(-5.0 * p1-5.0 * p2-5.0 * p3 + 3.0 * p4 +
                    3.0 * p6 + 3.0 * p7 + 3.0 * p8 + 3.0 * p9)
            # calculate the gradient value of 4 directions
            b = abs(3.0 * p1-5.0 * p2-5.0 * p3 + 3.0 * p4 -
                    5.0 * p6 + 3.0 * p7 + 3.0 * p8 + 3.0 * p9)
            c = abs(3.0 * p1 + 3.0 * p2-5.0 * p3 + 3.0 * p4 -
                    5.0 * p6 + 3.0 * p7 + 3.0 * p8-5.0 * p9)
            d = abs(3.0 * p1 + 3.0 * p2 + 3.0 * p3 + 3.0 *
                    p4-5.0 * p6 + 3.0 * p7-5.0 * p8-5.0 * p9)
	        # take the maximum value in each direction as the edge strength (confused cant see what is going on ?)
	        # do the max for each channel
	        # blue channel
            a[..., 0] = max(a[..., 0].max(), b[..., 0].max())
            a[..., 0] = max(a[..., 0].max(), c[..., 0].max())
            a[..., 0] = max(a[..., 0].max(), d[..., 0].max())
            if a[..., 0] > 127:
                a[..., 0] = 255
            else:
                a[...,0] = 0
            # green channel
            a[..., 1] = max(a[..., 1].max(), b[..., 1].max())
            a[..., 1] = max(a[..., 1].max(), c[..., 1].max())
            a[..., 1] = max(a[..., 1].max(), d[..., 1].max())
            if a[..., 1] > 127:
                a[..., 1] = 255
            else:
                a[...,1] = 0 
            # red channel
            a[..., 2] = max(a[..., 2].max(), b[..., 2].max())
            a[..., 2] = max(a[..., 2].max(), c[..., 2].max())
            a[..., 2] = max(a[..., 2].max(), d[..., 2].max())
            if a[..., 2] > 127:
                a[..., 2] = 255
            else:
                a[...,2] = 0
            kirsch[(y + 1) * step, (x + 1)] = a
    return kirsch   

# ======= Play with color ==============================================
#
# a function for looking at 3 pixels and taking either a max or a min
# it kinda helps look at motion
#
# mode : selects what you do
#        0 does nothing
#        bit 1 enables either max or min selection on blue channel
#        bit 2 on is max off is min value of 3 adjacent pixels
#        bit 3 on takes max min color values (color max)
#        this bit pattern repeats for green and blue channels respectively
#
def myColorfun(image, mode):
    val = image.shape
    m = val[0]
    n = val[1]
    step = 1
    ps = np.array(image)
    changedBytes = np.zeros([m, n, 3], dtype=np.uint8)
    for x in range(1, m-2):
        for y in range(1, n-2):
	        # obtain (I + 1, j + 1) gray around nine points
            a = ps[y -1 , x -1]
            # calculate the gradient value of 4 directions
            b = ps[y , x]
            c = ps[y +1, x +1]
	        # take the maximum value in each direction as the edge strength (confused cant see what is going on ?)
	        # do the max for each channel
	        # blue channel
            if mode & 1:
                if mode & 2:
                    a[..., 0] = max(a[..., 0].max(), b[..., 0].max())
                    a[..., 0] = max(a[..., 0].max(), c[..., 0].max())
                else:
                    a[..., 0] = min(a[..., 0].min(), b[..., 0].min())
                    a[..., 0] = min(a[..., 0].min(), c[..., 0].min())	
            else:				
                a[..., 0] = b[..., 0]
            if mode & 4:
                if a[..., 0] > 127:
                    a[..., 0] = 255
                else:
                    a[...,0] = 0
            # green channel
            if mode & 8:
                if mode & 16:
                    a[..., 1] = max(a[..., 1].max(), b[..., 1].max())
                    a[..., 1] = max(a[..., 1].max(), c[..., 1].max())
                else:
                    a[..., 1] = min(a[..., 1].min(), b[..., 1].min())
                    a[..., 1] = min(a[..., 1].min(), c[..., 1].min())	
            else:				
                a[..., 1] = b[..., 1]
            if mode & 32:
                if a[..., 1] > 127:
                    a[..., 1] = 255
                else:
                    a[...,1] = 0
            # red channel
            if mode & 64:
                if mode & 128:
                    a[..., 2] = max(a[..., 2].max(), b[..., 2].max())
                    a[..., 2] = max(a[..., 2].max(), c[..., 2].max())
                else:
                    a[..., 2] = min(a[..., 2].min(), b[..., 2].min())
                    a[..., 2] = min(a[..., 2].min(), c[..., 2].min())	
            else:				
                a[..., 2] = b[..., 2]
            if mode & 256:
                if a[..., 2] > 127:
                    a[..., 2] = 255
                else:
                    a[...,2] = 0
            changedBytes[y, x] = a
    return changedBytes  

#
# now bias those signals on thresholds
#
# mode : selects what you do
#        0 does nothing
#        bit 1 enables either max or min selection on blue channel
#        bit 2 on is max off is min value of 3 adjacent pixels
#        bit 3 on takes max min color values (color max)
#        this bit pattern repeats for green and blue channels respectively
#
def myColorfunThresholds(image, mode, blueThres, greenThres, redThres, blueBias, greenBias, redBias):
    val = image.shape
    m = val[0]
    n = val[1]
    step = 1
    ps = np.array(image)
    changedBytes = np.zeros([m, n, 3], dtype=np.uint8)
    for x in range(1, m-2):
        for y in range(1, n-2):
	        # obtain (I + 1, j + 1) gray around nine points
            a = ps[y -1 , x -1]
            # calculate the gradient value of 4 directions
            b = ps[y , x]
            c = ps[y +1, x +1]
	        # take the maximum value in each direction as the edge strength (confused cant see what is going on ?)
	        # do the max for each channel
	        # blue channel
            if mode & 1:
                if mode & 2:
                    a[..., 0] = max(a[..., 0].max(), b[..., 0].max()) * blueBias
                    a[..., 0] = max(a[..., 0].max(), c[..., 0].max()) * blueBias
                else:
                    a[..., 0] = min(a[..., 0].min(), b[..., 0].min()) * blueBias
                    a[..., 0] = min(a[..., 0].min(), c[..., 0].min()) * blueBias	
            else:				
                a[..., 0] = b[..., 0] * blueBias
            if mode & 512 and a[..., 0] > 255:
                a[..., 0] = 255    
            if mode & 4:
                if a[..., 0] > blueThres:
                    a[..., 0] = 255
                else:
                    a[...,0] = 0
            # green channel
            if mode & 8:
                if mode & 16:
                    a[..., 1] = max(a[..., 1].max(), b[..., 1].max()) * greenBias
                    a[..., 1] = max(a[..., 1].max(), c[..., 1].max()) * greenBias
                else:
                    a[..., 1] = min(a[..., 1].min(), b[..., 1].min()) * greenBias
                    a[..., 1] = min(a[..., 1].min(), c[..., 1].min()) * greenBias	
            else:				
                a[..., 1] = b[..., 1] * greenBias
            if mode & 1024 and a[..., 1] > 255:
                a[..., 1] = 255 
            if mode & 32:
                if a[..., 1] > greenThres:
                    a[..., 1] = 255
                else:
                    a[...,1] = 0
            # red channel
            if mode & 64:
                if mode & 128:
                    a[..., 2] = max(a[..., 2].max(), b[..., 2].max()) * redBias
                    a[..., 2] = max(a[..., 2].max(), c[..., 2].max()) * redBias
                else:
                    a[..., 2] = min(a[..., 2].min(), b[..., 2].min()) * redBias
                    a[..., 2] = min(a[..., 2].min(), c[..., 2].min()) * redBias	
            else:				
                a[..., 2] = b[..., 2] * redBias
            if mode & 1024 and a[..., 2] > 255:
                a[..., 2] = 255 
            if mode & 256:
                if a[..., 2] > redThres:
                    a[..., 2] = 255
                else:
                    a[...,2] = 0
            changedBytes[y, x] = a
    return changedBytes

#
# bias a another color when a given color is above a threshold
#
def myColorfunBiaserUp(image, mode, blueThres, greenThres, redThres, blueBias, greenBias, redBias):
    val = image.shape
    print(val)
    m = val[0]
    n = val[1]
    step = 1
    ps = np.array(image)
    changedBytes = np.zeros([m, n, 3], dtype=np.uint8)
    for x in range(0, m-2):
        for y in range(0, n-2):
            a = ps[x , y]
	        # blue channel
            if mode & 1:			
                a[..., 0] = a[..., 0] * blueBias
            if mode & 512 and a[..., 0] > 255:
                a[..., 0] = 255  
            if mode & 2 and a[..., 0] > blueThres:
                a[..., 2] = a[..., 2] * redBias    
            if mode & 4 and a[..., 0] > blueThres:
                a[..., 1] = a[..., 1] * greenBias                   
            # green channel	
            if mode & 8:			
                a[..., 1] = a[..., 1] * greenBias
            if mode & 1024 and a[..., 1] > 255:
                a[..., 1] = 255 
            if mode & 16 and a[..., 1] > greenThres:
                a[..., 2] = a[..., 2] * redBias  
            if mode & 32 and a[..., 1] > greenThres:
                a[..., 0] = a[..., 0] * blueBias                   
            # red channel
            if mode & 64:				
                a[..., 2] = a[..., 2] * redBias
            if mode & 1024 and a[..., 2] > 255:
                a[..., 2] = 255 
            if mode & 128 and a[..., 2] > redThres:
                a[..., 1] = a[..., 1] * greenBias
            if mode & 256 and a[..., 2] > redThres:
                a[..., 0] = a[..., 0] * blueBias                   
            changedBytes[x, y] = a
    return changedBytes
   
#
#
# bias a another color when a given color is below a threshold
# this inverts y and x width and height so make the image sysmetric first
#
#
def myColorfunBiaserDwn(image, mode, blueThres, greenThres, redThres, blueBias, greenBias, redBias):
    val = image.shape
    m = val[0]
    n = val[1]
    step = 1
    ps = np.array(image)
    changedBytes = np.zeros([m, n, 3], dtype=np.uint8)
    for x in range(0, m-1):
        for y in range(0, n-1):
            a = ps[x , y]
	        # blue channel
            if mode & 1:			
                a[..., 0] = a[..., 0] * blueBias
            if mode & 512 and a[..., 0] > 255:
                a[..., 0] = 255  
            if mode & 2 and a[..., 0] < blueThres:
                a[..., 2] = a[..., 2] * redBias   
            if mode & 4 and a[..., 0] < blueThres:
                a[..., 1] = a[..., 1] * greenBias                   
            # green channel	
            if mode & 8:			
                a[..., 1] = a[..., 1] * greenBias
            if mode & 1024 and a[..., 1] > 255:
                a[..., 1] = 255 
            if mode & 16 and a[..., 1] < greenThres:
                a[..., 2] = a[..., 2] * redBias  
            if mode & 32 and a[..., 1] < greenThres:
                a[..., 0] = a[..., 0] * blueBias                   
            # red channel
            if mode & 64:				
                a[..., 2] = a[..., 2] * redBias
            if mode & 1024 and a[..., 2] > 255:
                a[..., 2] = 255 
            if mode & 128 and a[..., 2] < redThres:
                a[..., 1] = a[..., 1] * greenBias
            if mode & 256 and a[..., 2] < redThres:
                a[..., 0] = a[..., 0] * blueBias                   
            changedBytes[x, y] = a
    return changedBytes

#
# swap channels
# this inverts y and x width and height so make the image sysmetric first
#
def myColorfunChanSwap(image, mode, blueThres, greenThres, redThres):
    val = image.shape
    m = val[0]
    n = val[1]
    step = 1
    ps = np.array(image)
    changedBytes = np.zeros([m, n, 3], dtype=np.uint8)
    for x in range(0, m-1):
        for y in range(0, n-1):
            a = ps[x , y]
	        # blue channel
            if mode & 1:			
                a[..., 0] = a[..., 1]                                   # make blue the green
            if mode & 2:
                a[..., 0] = a[..., 2]                                   # make blue the red                  
            # green channel	
            if mode & 4:			
                a[..., 1] = a[..., 0]                                   # make green blue
            if mode & 8:
                a[..., 1] = a[..., 2]                                   # make green red                  
            # red channel
            if mode & 16:				
                a[..., 2] = a[..., 0]                                   # make red blue 
            if mode & 32:
                a[..., 2] = a[..., 0]                                   # make red green 
            # now some unusual ones
            if mode & 64 and a[..., 2] < redThres:                      # red less than value change it to blue channel
                a[..., 2] = a[..., 0] 
            elif mode & 64 and a[..., 2] > redThres:
                a[..., 2] = a[..., 1]                                   # red greater than value change it to green channel
            if mode & 128 and a[..., 1] < greenThres:                   # green less than value change it to blue channel
                a[..., 1] = a[..., 0] 
            elif mode & 128 and a[..., 1] > greenThres:
                a[..., 1] = a[..., 2]                                   # green greater than value change it to red channel
            if mode & 256 and a[..., 0] < blueThres:                    # blue less than value change it to red channel
                a[..., 0] = a[..., 1] 
            elif mode & 256 and a[..., 0] > blueThres:
                a[..., 0] = a[..., 2]                                   # blue greater than value change it to red channel
            changedBytes[x, y] = a
    return changedBytes
                       
# ======== fun in manipulating pictures ================================

im = cv2.imread('/mnt/c/linuxmirror/rescue.jpeg')
imge = cv2.resize(im,(100,100))
# all bits are set highlights all areas of turbulence in sea
resc = myColorfun(imge,511)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/rescol.jpg', resc)
# now look for the man only saturate the blue and green channels only
resc = myColorfun(imge,36)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/rescolman.jpg', resc)
# set the max function to all 3 channels no saturation
resc = myColorfun(imge,73)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/rescol1.jpg', resc)
# set the min function to all 3 channels no saturation
resc = myColorfun(imge,219)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/rescol2.jpg', resc)
resc = myColorfunThresholds(imge, 292, 127, 127, 127, 1.5, 1.5, 0.7)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/rescol3.jpg', resc)
resc = myColorfunThresholds(imge, 292, 127, 127, 127, 1.01, 1.01, 0.7)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/rescol4.jpg', resc)
resc = myColorfunThresholds(imge, 0, 127, 127, 127, 0.0, 1.9, 0.0)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/rescol5.jpg', resc)
resc = myColorfunThresholds(imge, 0, 127, 127, 127, 1.0, 0.0, 2.0)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/rescol6.jpg', resc)
# when we limit the max pixel value to 255 it doesnt seem to care 
# kept in case a pixel value > 255 causes amy issue
# set the bits to enable the feature as before
resc = myColorfunThresholds(imge, 3584, 127, 127, 127, 0.0, 1.9, 0.0)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/rescol7.jpg', resc)
resc = myColorfunThresholds(imge, 292, 127, 60, 127, 1.0, 1.0, 1.0)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/rescol8.jpg', resc)
# only look at reds for example 
resc = myColorfunThresholds(imge, 292, 255, 255, 150, 1.0, 1.0, 1.0)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/rescol9.jpg', resc)
#
# now look at a colorful image and just tweak the color map
#
im = cv2.imread('/mnt/c/linuxmirror/pic1.jpg')
imge = cv2.resize(im,(100,100))
# reduce the ammount of red
resc = myColorfunThresholds(imge, 0, 127, 127, 127, 1.0, 1.0, 0.6)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic2.jpg', resc)
# reduced blue increased green
resc = myColorfunThresholds(imge, 0, 127, 127, 127, 0.1, 1.2, 1.0)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic3.jpg', resc)
# very green
resc = myColorfunThresholds(imge, 0, 127, 127, 127, 0.1, 1.2, 0.1)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic4.jpg', resc)
# green and blue
resc = myColorfunThresholds(imge, 0, 127, 127, 127, 0.4, 1.0, 0.1)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic5.jpg', resc)
# green and blue and some more red (overrall reduction is darker)
resc = myColorfunThresholds(imge, 0, 127, 127, 127, 0.4, 0.7, 0.4)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic6.jpg', resc)
# green and blue and red (overrall increase is lighter)
resc = myColorfunThresholds(imge, 0, 127, 127, 127, 1.1, 1.6, 1.3)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic7.jpg', resc)
# bias more green where we have blue over the threshold
resc = myColorfunBiaserUp(imge, 4, 127, 127, 127, 0.4, 2.2, 1.0)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic8.jpg', resc)
resc = myColorfunBiaserUp(imge, (4+1+8+64), 127, 127, 127, 0.6, 1.9, 1.1)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic9.jpg', resc)
# where we have red reduce sightly and decrease the blue
resc = myColorfunBiaserUp(imge, (260+1+8+64), 127, 127, 127, 0.6, 1.4, 0.8)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic10.jpg', resc)
# as above more reactive on threshold
resc = myColorfunBiaserUp(imge, (260+1+8+64), 75, 75, 75, 0.6, 1.4, 0.8)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic11.jpg', resc)
# now use down limit
resc = myColorfunBiaserDwn(imge, 260, 75, 75, 75, 0.6, 1.4, 0.8)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic12.jpg', resc)
# now use down limit
resc = myColorfunBiaserDwn(imge, 438, 100, 100, 100, 1.1, 1.1, 1.1)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic13.jpg', resc)
resc = myColorfunBiaserDwn(imge, 6, 100, 100, 100, 5, 5, 5)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic14.jpg', resc)
# channel swap fun
resc = myColorfunChanSwap(imge, 64, 100, 100, 100)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic15.jpg', resc)
resc = myColorfunChanSwap(imge, 256, 150, 150, 150)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic16.jpg', resc)
resc = myColorfunChanSwap(imge, 128, 170, 170, 170)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic17.jpg', resc)
resc = myColorfunChanSwap(imge, (20), 170, 170, 170)                    # all blue is black and white
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic18.jpg', resc)
resc = myColorfunChanSwap(imge, (16+2), 170, 170, 170)                  # bgr -> rgb
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic19.jpg', resc)
resc = myColorfunChanSwap(imge, (4+1), 170, 170, 170)                   # bgr -> gbr
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic20.jpg', resc)
resc2 = myColorfunBiaserDwn(resc, (8+64), 100, 100, 100, 1.0, 1.1, 0.5) # drop some red out of it. 
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic21.jpg', resc2)
#
# example using hsv space and modifying
#
imgeRGB = cv2.cvtColor(imge, cv2.COLOR_BGR2RGB)
hsv_1 = cv2.cvtColor(imgeRGB, cv2.COLOR_RGB2HSV)
light_color = (1, 190, 200)
dark_color = (18, 255, 255)
mask_color = cv2.inRange(hsv_1, light_color, dark_color)
result_col = cv2.bitwise_and(imgeRGB , imgeRGB , mask=mask_color)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic22.jpg', mask_color)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic23.jpg', result_col)
resc = myColorfunBiaserUp(hsv_1, 513, 127, 127, 127, 1.3, 1.0, 1.0)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic24.jpg', resc)
resc = myColorfunBiaserUp(hsv_1, 1, 127, 127, 127, 0.2, 1.0, 1.0)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic25.jpg', resc)
resc = myColorfunBiaserUp(hsv_1, 1+8+64, 127, 127, 127, 0.2, 1.5, 2.0)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic26.jpg', resc)
imgeRGB = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
hsv_1 = cv2.cvtColor(imgeRGB , cv2.COLOR_RGB2HSV)
resc = myColorfunBiaserUp(hsv_1, 1+8+64, 127, 127, 127, 0.8, 1.3, 1.1)
gbresult = gaussian_filter(resc, sigma=-50)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic28.jpg', gbresult)
resc = myColorfunBiaserUp(hsv_1, 1+8+64+8+128, 127, 127, 127, 1.1, 1.3, 1.0)
gbresult = gaussian_filter(resc, sigma=-200)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic29.jpg', gbresult)
# adjust the gamma
gamma_new = adjust_gamma(gbresult, gamma=1.0)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic28.jpg', gamma_new)
#
# add noize good for animating
#
noiz1 = AddNoize(gbresult)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic29.jpg', noiz1)
noiz2 = AddNoize(noiz1)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic30.jpg', noiz2)
noiz1 = AddNoize(noiz2)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic31.jpg', noiz1)
noiz2 = AddNoize(noiz1)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic32.jpg', noiz2)
#
# make a painting using the gaussian filter
#
im = cv2.imread('/mnt/c/linuxmirror/ice.jpg')
imgeRGB = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
hsv_1 = cv2.cvtColor(imgeRGB , cv2.COLOR_RGB2HSV)
resc = myColorfunBiaserUp(hsv_1, 1+8+64+4, 50, 127, 127, 0.8, 1.3, 1.1)
gbresult = gaussian_filter(resc, sigma=1)
kr3 = cv2.imwrite('/mnt/c/linuxmirror/pic27.jpg', gbresult)


# now we are looking for a motion in two video frames
#
# inspired from https://github.com/ZlodeiBaal/BirdProject/blob/master/capture.py
#
im = cv2.imread('/mnt/c/linuxmirror/frame2.jpg')
im_prev = cv2.imread('/mnt/c/linuxmirror/frame1.jpg')
frame = cv2.resize(im,(312,164))
frame_old = cv2.resize(im_prev,(312,164))
diffimg = cv2.absdiff(frame, frame_old)
d_s = cv2.sumElems(diffimg)
shap = frame.shape
d1 = (d_s[0]+d_s[1]+d_s[2])/(shap[0]*shap[1])
print("distance frame 1 to 2 is :",d1)
im = cv2.imread('/mnt/c/linuxmirror/frame3.jpg')
im_prev = cv2.imread('/mnt/c/linuxmirror/frame2.jpg')
frame = cv2.resize(im,(312,164))
frame_old = cv2.resize(im_prev,(312,164))
diffimg = cv2.absdiff(frame, frame_old)
d_s = cv2.sumElems(diffimg)
shap = frame.shape
d2 = (d_s[0]+d_s[1]+d_s[2])/(shap[0]*shap[1])
print("distance frame 2 to 3 is :",d2)
im = cv2.imread('/mnt/c/linuxmirror/frame3.jpg')
im_prev = cv2.imread('/mnt/c/linuxmirror/frame1.jpg')
frame = cv2.resize(im,(312,164))
frame_old = cv2.resize(im_prev,(312,164))
diffimg = cv2.absdiff(frame, frame_old)
d_s = cv2.sumElems(diffimg)
shap = frame.shape
d = (d_s[0]+d_s[1]+d_s[2])/(shap[0]*shap[1])
print("total distance fram 1 to 3 is :",d,d1+d2,d1-(d1+d2))

#
# use the modified kirsch to look at edging
#
im2 = cv2.imread('/mnt/c/linuxmirror/tester1.jpg')
imge = cv2.resize(im2,(100,100))
kirfun = kirschMyfun(imge)
k2 = cv2.imwrite('/mnt/c/linuxmirror/kirschfun2.jpg', kirfun)
im3 = cv2.imread('/mnt/c/linuxmirror/leaf1.jpg')
imge = cv2.resize(im3,(100,100))
kirleaf1 = kirschMyfun(imge)
kr = cv2.imwrite('/mnt/c/linuxmirror/kirschleaf1.jpg', kirleaf1)
im3 = cv2.imread('/mnt/c/linuxmirror/leaf2.jpg')
imge = cv2.resize(im3,(100,100))
kirleaf1 = kirschMyfun(imge)
kr = cv2.imwrite('/mnt/c/linuxmirror/kirschleaf2.jpg', kirleaf1)
im3 = cv2.imread('/mnt/c/linuxmirror/weeds1.jpg')
imge = cv2.resize(im3,(100,100))
kirleaf1 = kirschMyfun(imge)
kr = cv2.imwrite('/mnt/c/linuxmirror/kirschweed.jpg', kirleaf1)
kirleaf2 = myColorfun(imge,511)
kr2 = cv2.imwrite('/mnt/c/linuxmirror/kirschweedcol.jpg', kirleaf2)
