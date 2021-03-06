#--------------------------------------------------------------------------------
# Overlay transparent PNG files with OpenCV
#
# the class was inspired from this here
# https://gist.github.com/electricbaka/05fae17e598d2500c2b240919217cd65
#
# usage :-
# import cv2
# from pngoverlay import PNGOverlay
#
# (1) read the background
# dst = cv2.imread('background.jpg') 
#
# (2) read the image
# fish = PNGOverlay('img_fish.png')
#
# (3)show the image
# fish.show(dst, x, y) #dst is the background image you want to display. 
# x and y are the center coordinates you want to display the overlayed object
#
# ---------- methods available to this class  ----------
# Rotate object
# fish.rotate(45) # 45 degree
#
# Resize object
# fish.resize(0.5) # half size
#-----------------------------------------------------------------------
import sys
import os
import cv2
import numpy as np

# ------ make the png transparent --------------------------------------
def _makeTransparent(file_name):
    imin = cv2.imread(file_name, -1)
    src_bgra = cv2.cvtColor(imin, cv2.COLOR_BGRA2RGBA)
    val = src_bgra.shape
    m = val[0]
    n = val[1]
    ps = np.array(src_bgra)
    changedBytes = np.zeros([m, n, 4], dtype=np.uint8)
    for x in range(1, m-2):
        for y in range(1, n-2):
	        # read each picsel from the image
            a = ps[x , y]
            # if we see white make it transparent
            if a[..., 0] >= 255 and a[..., 1]  >= 250 and a[..., 2]  >= 250:
                a[..., 3] = 0                                           # set A channel to 0 is transparent 
            changedBytes[x, y] = a
    return changedBytes

# ------ clear the background of a bgr stream  -------------------------
def _clrBackground(imin):
    src_bgra = cv2.cvtColor(imin, cv2.COLOR_BGRA2RGBA)
    val = src_bgra.shape
    m = val[0]
    n = val[1]
    ps = np.array(src_bgra)
    changedBytes = np.zeros([m, n, 4], dtype=np.uint8)
    for x in range(1, m-2):
        for y in range(1, n-2):
	        # read each picsel from the image
            a = ps[x , y]
            # if we see white make it transparent
            if a[..., 0] >= 255 and a[..., 1]  >= 250 and a[..., 2]  >= 250:
                a[..., 3] = 0                                           # set A channel to 0 is transparent 
            changedBytes[x, y] = a
    return changedBytes

# ------ mirror the object horizontally  -------------------------------        
def _horizontalMirror(file_name):  
    imin = cv2.imread(file_name, -1)
    src_bgra = cv2.cvtColor(imin, cv2.COLOR_BGRA2RGBA)
    val = src_bgra.shape
    m = val[0]
    n = val[1]
    ps = np.array(src_bgra)
    changedBytes = np.zeros([m, n, 4], dtype=np.uint8)
    for x in range(1, m-2):
        for y in range(1, n-2):
	        # read each picsel from the image
            a = ps[(m-2) -x, y]
            changedBytes[x, y] = a
    return changedBytes

# ------ mirror the object vertically ----------------------------------    
def _verticalMirror(file_name):
    imin = cv2.imread(file_name, -1)
    src_bgra = cv2.cvtColor(imin, cv2.COLOR_BGRA2RGBA)
    val = src_bgra.shape
    m = val[0]
    n = val[1]
    ps = np.array(src_bgra)
    changedBytes = np.zeros([m, n, 4], dtype=np.uint8)
    for x in range(1, m-2):
        for y in range(1, n-2):
	        # read each picsel from the image
            a = ps[x, (n -2) - y]
            changedBytes[x, y] = a
    return changedBytes
    
# ------ mirror the object horizontally and clear background -----------
def _horizontalMirrorClearBgnd(file_name):  
    imin = cv2.imread(file_name, -1)
    src_bgra = cv2.cvtColor(imin, cv2.COLOR_BGRA2RGBA)
    val = src_bgra.shape
    m = val[0]
    n = val[1]
    ps = np.array(src_bgra)
    changedBytes = np.zeros([m, n, 4], dtype=np.uint8)
    for x in range(1, m-2):
        for y in range(1, n-2):
	        # read each picsel from the image
            a = ps[(m-2) -x, y]
            # if we see white make it transparent
            if a[..., 0] >= 255 and a[..., 1]  >= 250 and a[..., 2]  >= 250:
                a[..., 3] = 0                                           # set A channel to 0 is transparent 
            changedBytes[x, y] = a
    return changedBytes

# ------ mirror the object vertically and clear background -------------    
def _verticalMirrorClearBgnd(file_name):
    imin = cv2.imread(file_name, -1)
    src_bgra = cv2.cvtColor(imin, cv2.COLOR_BGRA2RGBA)
    val = src_bgra.shape
    m = val[0]
    n = val[1]
    ps = np.array(src_bgra)
    changedBytes = np.zeros([m, n, 4], dtype=np.uint8)
    for x in range(1, m-2):
        for y in range(1, n-2):
	        # read each picsel from the image
            a = ps[x, (n -2) - y]
            # if we see white make it transparent
            if a[..., 0] >= 255 and a[..., 1]  >= 250 and a[..., 2]  >= 250:
                a[..., 3] = 0                                           # set A channel to 0 is transparent 
            changedBytes[x, y] = a
    return changedBytes
            
class PNGOverlay():
    def __init__(self, filename):
        # Import as an image with alpha channel (BGRA)
        self.src_init = cv2.imread(filename, -1)
        self.src_init = cv2.cvtColor(self.src_init, cv2.COLOR_BGRA2RGBA)
        
        #Add the minimum required transparent color image to the surroundings
        self.src_init = self._addTransparentImage(self.src_init)

        #Image transformation does not require default
        self.flag_transformImage = False

        #Preprocess the image
        self._preProcessingImage(self.src_init)

        #initial value
        self.degree = 0
        self.size_value = 1

    def _addTransparentImage(self, src):                                # Add a transparent color area of ​​the image to the surroundings in advance so as not to crop when rotating
        height, width, _ = src.shape                                    # Obtaining HWC

        #Makes a transparent square with a diagonal length as one side for rotation
        diagonal = int(np.sqrt(width **2 + height ** 2))
        src_diagonal = np.zeros((diagonal, diagonal, 4), dtype=np.uint8)

        #Overwrite src in the center of the transparent square
        p1 = int(diagonal/2 - width/2)
        p2 = p1 + width
        q1 = int(diagonal/2 - height/2)
        q2 = q1 + height
        src_diagonal[q1:q2,p1:p2,:] = src[:,:,:]

        return src_diagonal

    def _preProcessingImage(self, src_bgra):                            # Divide the BGRA image into a BGR image (src) and an A image (mask), and retain the information required for overlaying
        self.mask = src_bgra[:,:,3]                                     # Extract only A from src and use it as a mask
        self.src = src_bgra[:,:,:3]                                     # Extract only GBR from src and use it as src
        self.mask = cv2.cvtColor(self.mask, cv2.COLOR_GRAY2BGR)         # A into 3 channels
        self.mask = self.mask / 255.0                                   # Normalized to 0.0-1.0
        self.height, self.width, _ = src_bgra.shape                     # Obtaining HWC
        self.flag_preProcessingImage = False                            # Lower the preprocessing flag once
        
    def rotate(self, degree):                                           # Image rotation parameter reception
        self.degree = degree
        self.flag_transformImage = True

    def resize(self, size_value):                                       # Image size parameter reception
        self.size_value = size_value
        self.flag_transformImage = True

    def _transformImage(self):                                          # It is necessary to resize and rotate in a series at once instead of doing it separately in each method
        #---------------------------------
        #resize
        #---------------------------------
        self.src_bgra = cv2.resize(self.src_init, dsize=None, fx=self.size_value, fy=self.size_value) # Specified by magnification

        #re-read into height and width from the new size
        self.height, self.width, _ = self.src_bgra.shape                # Obtaining HWC

        #---------------------------------
        # rotate
        #---------------------------------
        # getRotationMatrix2D
        center = (int(self.width/2), int(self.height/2))
        trans = cv2.getRotationMatrix2D(center, self.degree, 1)

        # Affine transformation
        self.src_bgra = cv2.warpAffine(self.src_bgra, trans, (self.width, self.height))

        # Since the transformation is finished, set the flag to False
        self.flag_transformImage == False

        # Preprocess the image before overlaying
        self.flag_preProcessingImage = True

    def show(self, dst, x, y):                                          # src is superimposed on the dst image and displayed. Center coordinate specification
        # Rotation and resizing need to be done in bulk just before overlay
        if self.flag_transformImage == True:
            self._transformImage()

        # Execute if preprocessing is required
        if self.flag_preProcessingImage == True:
            self._preProcessingImage(self.src_bgra)

        x1, y1 = x - int(self.width/2), y - int(self.height/2)
        x2, y2 = x1 + self.width, y1 + self.height                      # Note that if you do not use a calculation formula that adds width and height, an error may occur with a deviation of 1.
        a1, b1 = 0, 0
        a2, b2 = self.width, self.height
        dst_height, dst_width, _ = dst.shape

        # Not displayed if the x and y specified coordinates are completely out of dst
        if x2 <= 0 or x1 >= dst_width or y2 <= 0 or y1 >= dst_height:
            return

        #Corrects the protrusion from the dst frame
        x1, y1, x2, y2, a1, b1, a2, b2 = self._correctionOutofImage(dst, x1, y1, x2, y2, a1, b1, a2, b2)

        # Blend src images to dst by a percentage of A
        dst[y1:y2, x1:x2] = self.src[b1:b2, a1:a2] * self.mask[b1:b2, a1:a2] + dst[y1:y2, x1:x2] * ( 1 - self.mask[b1:b2, a1:a2] )

    def _correctionOutofImage(self, dst, x1, y1, x2, y2, a1, b1, a2, b2): #Correct x, y and a, b if the x, y coordinates are out of frame
        dst_height, dst_width, _ = dst.shape
        if x1 < 0:
            a1 = -x1
            x1 = 0
        if x2 > dst_width:
            a2 = self.width - x2 + dst_width
            x2 = dst_width
        if y1 < 0:
            b1 = -y1
            y1 = 0
        if y2 > dst_height:
            b2 = self.height - y2 + dst_height
            y2 = dst_height

        return x1, y1, x2, y2, a1, b1, a2, b2

# ===================== Test code ======================================
if __name__ == '__main__':

    # transform the png iamges to clear background outlays only
    readbytes = _makeTransparent('/mnt/c/linuxmirror/14149.png')
    cv2.imwrite('/mnt/c/linuxmirror/14149_2.png', readbytes)  
    readbytes = _makeTransparent('/mnt/c/linuxmirror/14133.png')
    cv2.imwrite('/mnt/c/linuxmirror/14133_2.png', readbytes)  
    readbytes = _makeTransparent('/mnt/c/linuxmirror/14134.png')
    cv2.imwrite('/mnt/c/linuxmirror/14134_2.png', readbytes)  
    readbytes = _makeTransparent('/mnt/c/linuxmirror/14131.png')
    cv2.imwrite('/mnt/c/linuxmirror/14131_2.png', readbytes)  
    readbytes = _makeTransparent('/mnt/c/linuxmirror/14150.png')
    cv2.imwrite('/mnt/c/linuxmirror/14150_2.png', readbytes) 
    readbytes = _makeTransparent('/mnt/c/linuxmirror/14146.png')
    cv2.imwrite('/mnt/c/linuxmirror/14146_2.png', readbytes)  
    readbytes = _verticalMirrorClearBgnd('/mnt/c/linuxmirror/14146.png')
    cv2.imwrite('/mnt/c/linuxmirror/14146_3.png', readbytes)   
    readbytes = _horizontalMirrorClearBgnd('/mnt/c/linuxmirror/14146.png')
    cv2.imwrite('/mnt/c/linuxmirror/14146_4.png', readbytes)      
    readbytes = _makeTransparent('/mnt/c/linuxmirror/14144.png')
    cv2.imwrite('/mnt/c/linuxmirror/14144_2.png', readbytes) 
    readbytes = _makeTransparent('/mnt/c/linuxmirror/14151.png')
    cv2.imwrite('/mnt/c/linuxmirror/14151_2.png', readbytes) 
    readbytes = _makeTransparent('/mnt/c/linuxmirror/14142.png')
    cv2.imwrite('/mnt/c/linuxmirror/14142_2.png', readbytes) 
    readbytes = _makeTransparent('/mnt/c/linuxmirror/14145.png')
    cv2.imwrite('/mnt/c/linuxmirror/14145_2.png', readbytes) 
                            
    # Instance generation for every potential screen object pose
    startPose = PNGOverlay('/mnt/c/linuxmirror/14142_2.png')
    stop_pose = PNGOverlay('/mnt/c/linuxmirror/14145_2.png')
    runPose = PNGOverlay('/mnt/c/linuxmirror/14149_2.png')
    stopped = PNGOverlay('/mnt/c/linuxmirror/14150_2.png')
    pose1 = PNGOverlay('/mnt/c/linuxmirror/14146_2.png')
    pose1_rotRight = PNGOverlay('/mnt/c/linuxmirror/14146_3.png')
    pose1_rotUp = PNGOverlay('/mnt/c/linuxmirror/14146_4.png')
    pose2 = PNGOverlay('/mnt/c/linuxmirror/14144_2.png')
    run_left = PNGOverlay('/mnt/c/linuxmirror/14151_2.png')
    rabbit1 = PNGOverlay('/mnt/c/linuxmirror/14133_2.png')
    rabbit2 = PNGOverlay('/mnt/c/linuxmirror/14134_2.png')
    rabbit3 = PNGOverlay('/mnt/c/linuxmirror/14131_2.png')

    #Overlay method execution frame 0
    dst = cv2.imread('/mnt/c/linuxmirror/art2.jpg') #background
    dst = cv2.resize(dst, dsize=None, fx=0.8, fy=0.8)
    startPose.show(dst, 200, 100)
    rabbit1.show(dst, 730, 380)
    rabbit2.rotate(-35)
    rabbit2.show(dst, 600, 500)
    rabbit3.resize(0.8)
    #rabbit3.rotate(40)
    rabbit3.show(dst, 400, 500)
    cv2.imwrite('/mnt/c/linuxmirror/animate0.jpg', dst)  
    #Overlay method execution frame 1
    dst = cv2.imread('/mnt/c/linuxmirror/art2.jpg') #background
    dst = cv2.resize(dst, dsize=None, fx=0.8, fy=0.8)
    runPose.show(dst, 200, 100)
    rabbit1.show(dst, 730, 380)
    rabbit2.rotate(-35)
    rabbit2.show(dst, 600, 500)
    rabbit3.resize(0.8)
    #rabbit3.rotate(40)
    rabbit3.show(dst, 400, 500)
    cv2.imwrite('/mnt/c/linuxmirror/animate1.jpg', dst)  
    #Overlay method execution frame 2
    dst = cv2.imread('/mnt/c/linuxmirror/art2.jpg') #background
    dst = cv2.resize(dst, dsize=None, fx=0.8, fy=0.8)
    runPose.show(dst, 250, 100)
    rabbit1.show(dst, 700, 380)
    rabbit2.rotate(-45)
    rabbit2.show(dst, 600, 500)
    rabbit3.resize(0.8)
    #rabbit3.rotate(40)
    rabbit3.show(dst, 400, 450)
    cv2.imwrite('/mnt/c/linuxmirror/animate2.jpg', dst) 
    #Overlay method execution frame 3
    dst = cv2.imread('/mnt/c/linuxmirror/art2.jpg') #background
    dst = cv2.resize(dst, dsize=None, fx=0.8, fy=0.8)
    runPose.show(dst, 300, 100)
    rabbit1.show(dst, 710, 370)
    rabbit2.rotate(-15)
    rabbit2.show(dst, 600, 500)
    rabbit3.resize(0.8)
    #rabbit3.rotate(40)
    rabbit3.show(dst, 400, 400)
    cv2.imwrite('/mnt/c/linuxmirror/animate3.jpg', dst) 
    #Overlay method execution frame 4
    dst = cv2.imread('/mnt/c/linuxmirror/art2.jpg') #background
    dst = cv2.resize(dst, dsize=None, fx=0.8, fy=0.8)
    runPose.show(dst, 350, 100)
    rabbit1.show(dst, 730, 380)
    #rabbit2.rotate(-35)
    rabbit2.show(dst, 600, 500)
    rabbit3.resize(0.8)
    #rabbit3.rotate(40)
    rabbit3.show(dst, 400, 500)
    cv2.imwrite('/mnt/c/linuxmirror/animate4.jpg', dst)  
    #Overlay method execution frame 5
    dst = cv2.imread('/mnt/c/linuxmirror/art2.jpg') #background
    dst = cv2.resize(dst, dsize=None, fx=0.8, fy=0.8)
    runPose.show(dst, 400, 100)
    rabbit1.show(dst, 730, 380)
    #rabbit2.rotate(-35)
    rabbit2.show(dst, 600, 500)
    rabbit3.resize(0.8)
    rabbit3.rotate(-40)
    rabbit3.show(dst, 400, 500)
    cv2.imwrite('/mnt/c/linuxmirror/animate5.jpg', dst)  
    #Overlay method execution frame 6
    dst = cv2.imread('/mnt/c/linuxmirror/art2.jpg') #background
    dst = cv2.resize(dst, dsize=None, fx=0.8, fy=0.8)
    runPose.show(dst, 500, 100)
    rabbit1.show(dst, 720, 390)
    #rabbit2.rotate(-35)
    rabbit2.show(dst, 600, 500)
    rabbit3.resize(0.8)
    rabbit3.rotate(-40)
    rabbit3.show(dst, 400, 500)
    cv2.imwrite('/mnt/c/linuxmirror/animate6.jpg', dst)
    #Overlay method execution frame 7
    dst = cv2.imread('/mnt/c/linuxmirror/art2.jpg') #background
    dst = cv2.resize(dst, dsize=None, fx=0.8, fy=0.8)
    stopped.show(dst, 500, 100)
    rabbit1.show(dst, 720, 390)
    #rabbit2.rotate(-35)
    rabbit2.show(dst, 610, 510)
    rabbit3.resize(0.8)
    rabbit3.rotate(10)
    rabbit3.show(dst, 400, 500)
    cv2.imwrite('/mnt/c/linuxmirror/animate7.jpg', dst)
    #Overlay method execution frame 8
    dst = cv2.imread('/mnt/c/linuxmirror/art2.jpg') #background
    dst = cv2.resize(dst, dsize=None, fx=0.8, fy=0.8)
    pose1.show(dst, 500, 100)
    rabbit1.show(dst, 720, 390)
    #rabbit2.rotate(-35)
    rabbit2.show(dst, 610, 510)
    rabbit3.resize(0.8)
    #rabbit3.rotate(10)
    rabbit3.show(dst, 400, 500)
    cv2.imwrite('/mnt/c/linuxmirror/animate8.jpg', dst)
    #Overlay method execution frame 9
    dst = cv2.imread('/mnt/c/linuxmirror/art2.jpg') #background
    dst = cv2.resize(dst, dsize=None, fx=0.8, fy=0.8)
    pose2.show(dst, 500, 100)
    rabbit1.show(dst, 720, 390)
    #rabbit2.rotate(-35)
    rabbit2.show(dst, 610, 510)
    rabbit3.resize(0.8)
    rabbit3.rotate(-10)
    rabbit3.show(dst, 400, 500)
    cv2.imwrite('/mnt/c/linuxmirror/animate9.jpg', dst)
    #Overlay method execution frame 10
    dst = cv2.imread('/mnt/c/linuxmirror/art2.jpg') #background
    dst = cv2.resize(dst, dsize=None, fx=0.8, fy=0.8)
    run_left.show(dst, 500, 100)
    rabbit1.show(dst, 520, 390)
    #rabbit2.rotate(-35)
    rabbit2.show(dst, 610, 510)
    rabbit3.resize(0.8)
    rabbit3.rotate(-10)
    rabbit3.show(dst, 400, 500)
    cv2.imwrite('/mnt/c/linuxmirror/animate10.jpg', dst)
    #Overlay method execution frame 11
    dst = cv2.imread('/mnt/c/linuxmirror/art2.jpg') #background
    dst = cv2.resize(dst, dsize=None, fx=0.8, fy=0.8)
    run_left.show(dst, 400, 100)
    rabbit1.show(dst, 320, 390)
    #rabbit2.rotate(-35)
    rabbit2.show(dst, 610, 510)
    rabbit3.resize(0.8)
    #rabbit3.rotate(-10)
    rabbit3.show(dst, 400, 500)
    cv2.imwrite('/mnt/c/linuxmirror/animate11.jpg', dst)
    #Overlay method execution frame 12
    dst = cv2.imread('/mnt/c/linuxmirror/art2.jpg') #background
    dst = cv2.resize(dst, dsize=None, fx=0.8, fy=0.8)
    run_left.show(dst, 300, 100)
    rabbit1.show(dst, 220, 390)
    rabbit2.rotate(5)
    rabbit2.show(dst, 600, 510)
    rabbit3.resize(0.8)
    rabbit3.rotate(10)
    rabbit3.show(dst, 400, 500)
    cv2.imwrite('/mnt/c/linuxmirror/animate12.jpg', dst)
    #Overlay method execution frame 13
    dst = cv2.imread('/mnt/c/linuxmirror/art2.jpg') #background
    dst = cv2.resize(dst, dsize=None, fx=0.8, fy=0.8)
    pose1.show(dst, 200, 100)
    rabbit1.show(dst, 180, 390)
    rabbit2.rotate(-5)
    rabbit2.show(dst, 600, 400)
    rabbit3.resize(0.8)
    rabbit3.rotate(10)
    rabbit3.show(dst, 400, 500)
    cv2.imwrite('/mnt/c/linuxmirror/animate13.jpg', dst)
    #Overlay method execution frame 14
    dst = cv2.imread('/mnt/c/linuxmirror/art2.jpg') #background
    dst = cv2.resize(dst, dsize=None, fx=0.8, fy=0.8)
    stop_pose.show(dst, 200, 100)
    rabbit1.show(dst, 120, 390)
    rabbit2.rotate(0)
    rabbit2.show(dst, 600, 510)
    rabbit3.resize(0.8)
    rabbit3.rotate(10)
    rabbit3.show(dst, 400, 500)
    cv2.imwrite('/mnt/c/linuxmirror/animate14.jpg', dst)
    #Overlay method execution frame 15 change background and overlay
    dst = cv2.imread('/mnt/c/linuxmirror/BL005.jpg') #background
    dst = cv2.resize(dst, dsize=None, fx=0.8, fy=0.8)
    stop_pose.show(dst, 200, 100)
    cv2.imwrite('/mnt/c/linuxmirror/animate15.jpg', dst)
    # frame 16 just puts another object on this background
    pose2.show(dst, 400, 100)   
    cv2.imwrite('/mnt/c/linuxmirror/animate16.jpg', dst)
    # frame 17 just puts another smaller object on this background
    pose1.resize(0.4)
    pose1.show(dst, 70, 100)   
    cv2.imwrite('/mnt/c/linuxmirror/animate17.jpg', dst)
    #Overlay method execution frame 18 change background and overlay
    dst = cv2.imread('/mnt/c/linuxmirror/BL005.jpg') #background
    dst = cv2.resize(dst, dsize=None, fx=0.8, fy=0.8)
    stop_pose.show(dst, 200, 100)    
    pose2.show(dst, 400, 100)  
    pose1_rotRight.resize(0.4)
    pose1_rotRight.show(dst, 70, 100)  
    cv2.imwrite('/mnt/c/linuxmirror/animate18.jpg', dst)
    #Overlay method execution frame 19 change background and overlay
    dst = cv2.imread('/mnt/c/linuxmirror/BL005.jpg') #background
    dst = cv2.resize(dst, dsize=None, fx=0.8, fy=0.8)
    stop_pose.show(dst, 200, 100)    
    pose2.show(dst, 400, 100)  
    pose1_rotUp.resize(0.4)
    pose1_rotUp.show(dst, 70, 100)  
    cv2.imwrite('/mnt/c/linuxmirror/animate19.jpg', dst)
    #Overlay method execution frame 20 change background and overlay
    dst = cv2.imread('/mnt/c/linuxmirror/BL005.jpg') #background
    dst = cv2.resize(dst, dsize=None, fx=0.8, fy=0.8)
    stop_pose.show(dst, 200, 100)    
    pose2.show(dst, 400, 100)  
    pose1_rotRight.resize(0.4)
    pose1_rotRight.show(dst, 65, 100)  
    cv2.imwrite('/mnt/c/linuxmirror/animate20.jpg', dst)

    dst = cv2.imread('/mnt/c/linuxmirror/art2.jpg') #background
    dst = cv2.resize(dst, dsize=None, fx=0.8, fy=0.8)
    rabbit2.rotate(60)
    rabbit2.show(dst, 200, 100)
    runPose.rotate(-90)
    runPose.resize(1.3)
    runPose.show(dst, 700, 200)
    rabbit3.resize(0.3)
    rabbit3.rotate(-5)
    rabbit3.show(dst, 500, 500)
    cv2.imwrite('/mnt/c/linuxmirror/animate21.jpg', dst)  
#
#    you can use imshow rather than imwrite to you're screen if you want
#
#    cv2.imshow('dst',dst)
#    cv2.waitKey(0)
#
#    end it with
#    cv2.destroyAllWindows()
