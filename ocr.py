# pip install opencv-contrib-python
# ======================================================================
#
# python script to run OCR functionality
# This can be used to iterate pic change when ocr doesnt output correct
# this action maybe for instance :- 
# 1.Rotate 2.Invert 3.Resize (4. canny for edge detection)
#
# you can use the script as an iterative autoscaler with known example 
# graphic files until the ocr output result is equal to the expectation
# then you can work out the correct ratio for that application for all 
# new and unknown files.
#
# ======================================================================
# 
import os
import cv2
import numpy as np
# ============== only if you want to do saliency =======================
# requires https://github.com/akisatok/pySaliencyMap
# for producing salency maps if you dont want uncomment this bit out
import pySaliencyMap

# ============== gaussian ==============================================
from scipy.ndimage import gaussian_filter
# ============== prewitt ===============================================
from scipy import ndimage
   
# read the designated image for use with the conversions
im = cv2.imread('/mnt/c/linuxmirror/testFile1.jpg')
# ======= instead use a webcam uncomment below =========================
# capture = cv2.VideoCapture(0)
#    while(True):
        # capture
#        retval, im = capture.read()


#if not im:
#    print('the image was not read correctly')
#else:
# ========= convert BGR to RGB =========================================
im_rgb = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
# here we write the image as a pnm file (we choose without modification)
# for testing with the ocrad ocr engine
oi = cv2.imwrite('/home/mark/pics/ocradFile.pnm', im_rgb)
# ========= crop the image if you want =================================
crop = im[ 0:200, 200:500 ]
oi = cv2.imwrite('/mnt/c/linuxmirror/crop.jpg', crop)

# ========= use this to re-size images if needed =======================
print('Original Dimensions : ',im.shape)
scale_percent = 60 # percent of original size <100 (smaller) >100 (bigger)
width = int(im.shape[1] * scale_percent / 100)     # can set explicitly
height = int(im.shape[0] * scale_percent / 100)    # can set explicitly
dim = (width, height) 
# ======== resize image ================================================
resized = cv2.resize(im, dim, interpolation = cv2.INTER_AREA) 
print('Resized Dimensions : ',resized.shape)
# ======== to show it ==================================================
# cv2.imshow("Resized image", resized)
# ======= if you want to write the re-sized image for use with ocr =====
rs = cv2.imwrite('/mnt/c/linuxmirror/resized1.jpg', resized)

# ========= invert image ===============================================
# im = (255-im)
ni = ~im
# im = cv2.bitwise_not(im)
# to write out 
iv = cv2.imwrite('/mnt/c/linuxmirror/invert1.jpg', ni)

# ======== rotate image ================================================
# 5 degree rotate to left
# angleInDegrees = 5  
# 5 degree rotate to right
angleInDegrees = -5 
# scale if you want here we do no change at value 1.0 unity
scale = 1.0 
(h, w) = im.shape[:2]  
center=tuple(np.array([h,w])/2)
# Perform the rotation
M = cv2.getRotationMatrix2D(center, angleInDegrees, scale)
rotated = cv2.warpAffine(im, M, (w, h))
ro = cv2.imwrite('/mnt/c/linuxmirror/rotated.jpg', rotated)
#
# alternate rotate code
#
# rad = math.radians(angleInDegrees)
# sin = math.sin(rad)
# cos = math.cos(rad)
# b_w = int((h * abs(sin)) + (w * abs(cos)))
# b_h = int((h * abs(cos)) + (w * abs(sin)))
# rot[0, 2] += ((b_w / 2) - center[0])
# rot[1, 2] += ((b_h / 2) - center[1])
# outImg = cv2.warpAffine(im, rot, (b_w, b_h), flags=cv2.INTER_LINEAR)
# oi = cv2.imwrite('/mnt/c/linuxmirror/rotated2.jpg', outImg)

# ========= Edge detection (doesnt normally help ocr) ==================
#
# very good for looking at weeds in fields though
#
# ========= apply canny filter =========================================
edges = cv2.Canny(im,100,200)
# ======= if you want to write the canny image for use =================
ca = cv2.imwrite('/mnt/c/linuxmirror/canny1.jpg', edges)
# ======= dilate function use when edge not connected ==================
kern = np.ones((5,5),np.uint8)
imgDilation = cv2.dilate(edges, kern, iterations=1)
ci = cv2.imwrite('/mnt/c/linuxmirror/cannydilate.jpg', imgDilation)
# ======= erode when you want to thin image ============================
imgErode = cv2.erode(imgDilation, kern, iterations=1)
ce = cv2.imwrite('/mnt/c/linuxmirror/cannyerode.jpg', imgErode)
# ========= sobel edge detection =======================================
laplacian = cv2.Laplacian(im,cv2.CV_64F)
sobelx = cv2.Sobel(im,cv2.CV_64F,1,0,ksize=5)
sobely = cv2.Sobel(im,cv2.CV_64F,0,1,ksize=5)
# Grayscale processing image (used by sobel and prewitt)
grayImage = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
# Sobel operator
x = cv2.Sobel(grayImage, cv2.CV_16S, 1, 0)
y = cv2.Sobel(grayImage, cv2.CV_16S, 0, 1)
# Turn uint8, image fusion
absX = cv2.convertScaleAbs(x)
absY = cv2.convertScaleAbs(y)
Sobel = cv2.addWeighted(absX, 0.5, absY, 0.5, 0)
# ======= if you want to write the sobel image for use =================
lp = cv2.imwrite('/mnt/c/linuxmirror/laplace1.jpg', laplacian)
sx = cv2.imwrite('/mnt/c/linuxmirror/sobelX.jpg', sobelx)
sy = cv2.imwrite('/mnt/c/linuxmirror/sobelY.jpg', sobely)
so = cv2.imwrite('/mnt/c/linuxmirror/sobel.jpg', Sobel)
# ======== prewitt edge detection ======================================
prewit = ndimage.prewitt(im)
pw = cv2.imwrite('/mnt/c/linuxmirror/prewitt.jpg', prewit)
# Prewitt operator
kernelx = np.array([[1,1,1],[0,0,0],[-1,-1,-1]],dtype=int)
kernely = np.array([[-1,0,1],[-1,0,1],[-1,0,1]],dtype=int)
x = cv2.filter2D(grayImage, cv2.CV_16S, kernelx)
y = cv2.filter2D(grayImage, cv2.CV_16S, kernely)
# Turn uint8, image fusion
absX = cv2.convertScaleAbs(x)
absY = cv2.convertScaleAbs(y)
Prewitt = cv2.addWeighted(absX, 0.5, absY, 0.5, 0)
pw = cv2.imwrite('/mnt/c/linuxmirror/prewitt2.jpg', Prewitt)
# ======== roberts edge detector =======================================
grayImage = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
# Roberts operator
kernelx = np.array([[-1, 0], [0, 1]], dtype=int)
kernely = np.array([[0, -1], [1, 0]], dtype=int)
x = cv2.filter2D(grayImage, cv2.CV_16S, kernelx)
y = cv2.filter2D(grayImage, cv2.CV_16S, kernely)
# Turn uint8, image fusion
absX = cv2.convertScaleAbs(x)
absY = cv2.convertScaleAbs(y)
Roberts = cv2.addWeighted(absX, 0.5, absY, 0.5, 0)
ro = cv2.imwrite('/mnt/c/linuxmirror/roberts.jpg', Roberts)

# ========= apply guassian blur on src image ===========================
dst = cv2.GaussianBlur(im,(5,5),cv2.BORDER_DEFAULT)
# display input and output image
#cv2.imshow("Gaussian Smoothing",numpy.hstack((im, dst)))
#gblur = np.hstack((im, dst)
gb = cv2.imwrite('/mnt/c/linuxmirror/gauss2.jpg', dst)
# sharp
gbresult = gaussian_filter(im, sigma=-1)
# smooth
#gbresult = gaussian_filter(im, sigma=1)
gb = cv2.imwrite('/mnt/c/linuxmirror/gaussi.jpg', gbresult)

# ========= apply filter on src image ==================================
kernel = np.ones((5,5),np.float32)/25
filtr = cv2.filter2D(im,-1,kernel)
fi = cv2.imwrite('/mnt/c/linuxmirror/filtered.jpg', filtr)
# ========= compute gradient using scharr ==============================
gradx = cv2.Scharr(im, cv2.CV_32F, 1, 0, scale=1.0/32)
grady = cv2.Scharr(im, cv2.CV_32F, 0, 1, scale=1.0/32)
gx = cv2.imwrite('/mnt/c/linuxmirror/gradx.jpg', gradx)
gy = cv2.imwrite('/mnt/c/linuxmirror/grady.jpg', grady)
gradient = np.dstack([gradx, grady])

            
# ======== implementation for extracting a saliency map from image 
# you need to download the following python code libraries
# ref :- https://github.com/akisatok/pySaliencyMap
# ref :- L. Itti, C. Koch, E. Niebur, 
# A Model of Saliency-Based Visual Attention for Rapid Scene Analysis, 
# IEEE Transactions on Pattern Analysis and Machine Intelligence, 
# Vol. 20, No. 11, pp. 1254-1259, Nov 1998.
#
# some further interesting info in matlab can be found here
# http://people.vision.caltech.edu/~harel/share/gbvs.php
#
im2 = cv2.imread('/mnt/c/linuxmirror/pic1.jpg')
im = cv2.resize(im2,(300,300))
imgsize = im.shape
img_width  = imgsize[1]
img_height = imgsize[0]
sm = pySaliencyMap.pySaliencyMap(img_width, img_height)
saliency_map = sm.SMGetSM(im)
binarized_map = sm.SMGetBinarizedSM(im)
salient_region = sm.SMGetSalientRegion(im)
sm = cv2.imwrite('/mnt/c/linuxmirror/saliency.jpg', saliency_map)
bm = cv2.imwrite('/mnt/c/linuxmirror/binarized.jpg', binarized_map)
sr_rgb = cv2.cvtColor(salient_region, cv2.COLOR_BGR2RGB) 
sr = cv2.imwrite('/mnt/c/linuxmirror/salient_reg.jpg', sr_rgb)   

# if you are using a webcam then uncomment it here
        # exit if the key "q" is pressed
#        if cv2.waitKey(1) & 0xFF == ord('q'):
#            break

# if you use imshow to look at anything you need this one  
# cv2.destroyAllWindows()

#if not oi:
#    print('Image was not converted')
#else:
#
# here we are shelling to the operating system to run the ocr on the pnm
# it also runs the ocr tests on the labels we are testing
#
f = os.popen('/home/mark/pics/run_ocrad.sh /home/mark/pics/ocradFile.pnm')
strFound = f.read()
print ("The following text was read using ocrad : ", strFound)
#
# alternative OCR with GUI is lios installed using python as follows
# git clone https://gitlab.com/Nalin-x-Linux/lios-3.git
# cd lios-3
# sudo python3 setup.py install --install-data=/usr or in my case
# sudo python3 setup.py install --install-data=/home
#
