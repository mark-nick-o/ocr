import cv2
import numpy as np
import math

#
# ported from https://topic.alibabacloud.com/a/opencv-edge-font-colorreddetectionfont-reberts-sobel-prewitt-kirsch_8_8_32059025.html
# This is function uses the maximum result RGB : gives funky output
#
def kirsch(image):
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
            # green channel
            a[..., 1] = max(a[..., 1].max(), b[..., 1].max())
            a[..., 1] = max(a[..., 1].max(), c[..., 1].max())
            a[..., 1] = max(a[..., 1].max(), d[..., 1].max())
            # red channel
            a[..., 2] = max(a[..., 2].max(), b[..., 2].max())
            a[..., 2] = max(a[..., 2].max(), c[..., 2].max())
            a[..., 2] = max(a[..., 2].max(), d[..., 2].max())
            kirsch[(y + 1) * step, (x + 1)] = a
    return kirsch
#
# This is function uses the minimum instead of maximum
#
def kirschmin(image):
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
            a[..., 0] = min(a[..., 0].min(), b[..., 0].min())
            a[..., 0] = min(a[..., 0].min(), c[..., 0].min())
            a[..., 0] = min(a[..., 0].min(), d[..., 0].min())
            # green channel
            a[..., 1] = min(a[..., 1].min(), b[..., 1].min())
            a[..., 1] = min(a[..., 1].min(), c[..., 1].min())
            a[..., 1] = min(a[..., 1].min(), d[..., 1].min())
            # red channel
            a[..., 2] = min(a[..., 2].min(), b[..., 2].min())
            a[..., 2] = min(a[..., 2].min(), c[..., 2].min())
            a[..., 2] = min(a[..., 2].min(), d[..., 2].min())
            kirsch[(y + 1) * step, (x + 1)] = a
    return kirsch
#
# This is a port of a function on the net (fixedcode hang up) : gives black box ?
#
def kirsch2(image):
    val = image.shape
    m = val[0]
    n = val[1]
    kirsch = np.zeros([m, n, 3], dtype=np.uint8)
    for i in range(2, m-1):
        for j in range(2, n-1):
            d1 = np.square(5 * image[i - 1, j - 1] + 5 * image[i - 1, j] + 5 * image[i - 1, j + 1] - 3 * image[i, j - 1] - 3 * image[i, j + 1] - 3 * image[i + 1, j - 1] - 3 * image[i + 1, j] - 3 * image[i + 1, j + 1])
            d2 = np.square((-3) * image[i - 1, j - 1] + 5 * image[i - 1, j] + 5 * image[i - 1, j + 1] - 3 * image[i, j - 1] + 5 * image[i, j + 1] - 3 * image[i + 1, j - 1] - 3 * image[i + 1, j] - 3 * image[i + 1, j + 1])
            d3 = np.square((-3) * image[i - 1, j - 1] - 3 * image[i - 1, j] + 5 * image[i - 1, j + 1] - 3 * image[i, j - 1] + 5 * image[i, j + 1] - 3 * image[i + 1, j - 1] - 3 * image[i + 1, j] + 5 * image[i + 1, j + 1])
            d4 = np.square((-3) * image[i - 1, j - 1] - 3 * image[i - 1, j] - 3 * image[i - 1, j + 1] - 3 * image[i, j - 1] + 5 * image[i, j + 1] - 3 * image[i + 1, j - 1] + 5 * image[i + 1, j] + 5 * image[i + 1, j + 1])
            d5 = np.square((-3) * image[i - 1, j - 1] - 3 * image[i - 1, j] - 3 * image[i - 1, j + 1] - 3 * image[i, j - 1] - 3 * image[i, j + 1] + 5 * image[i + 1, j - 1] + 5 * image[i + 1, j] + 5 * image[i + 1, j + 1])
            d6 = np.square((-3) * image[i - 1, j - 1] - 3 * image[i - 1, j] - 3 * image[i - 1, j + 1] + 5 * image[i, j - 1] - 3 * image[i, j + 1] + 5 * image[i + 1, j - 1] + 5 * image[i + 1, j] - 3 * image[i + 1, j + 1])
            d7 = np.square(5 * image[i - 1, j - 1] - 3 * image[i - 1, j] - 3 * image[i - 1, j + 1] + 5 * image[i, j - 1] - 3 * image[i, j + 1] + 5 * image[i + 1, j - 1] - 3 * image[i + 1, j] - 3 * image[i + 1, j + 1])
            d8 = np.square(5 * image[i - 1, j - 1] + 5 * image[i - 1, j] - 3 * image[i - 1, j + 1] + 5 * image[i, j - 1] - 3 * image[i, j + 1] - 3 * image[i + 1, j - 1] - 3 * image[i + 1, j] - 3 * image[i + 1, j + 1])
            # : Take the maximum value in each direction, the effect is not good, use another method
            a = d1
            #
	        # blue channel (took out np.sqrt as always gave black output)
	        # a[..., 0] = int(np.sqrt(max(a[..., 1].max(), d2[..., 0].max()))) 
	        #
            a[..., 0] = int((max(a[..., 0].max(), d2[..., 0].max())))
            a[..., 0] = int((max(a[..., 0].max(), d3[..., 0].max())))
            a[..., 0] = int((max(a[..., 0].max(), d4[..., 0].max())))
            a[..., 0] = int((max(a[..., 0].max(), d5[..., 0].max())))
            a[..., 0] = int((max(a[..., 0].max(), d6[..., 0].max())))
            a[..., 0] = int((max(a[..., 0].max(), d7[..., 0].max())))
            a[..., 0] = int((max(a[..., 0].max(), d8[..., 0].max())))
            a[..., 0] = int((max(a[..., 0].max(), d8[..., 0].max())))
            #
            # this is for on/off color
            #
            #if a[..., 0] > 127:
            #    a[..., 0] = 255
            #else:
            #    a[...,0] = 0
            #
            # green channel
            # a[..., 1] = int(np.sqrt(max(a[..., 1].max(), d2[..., 1].max()))) 
            #
            a[..., 1] = int((max(a[..., 1].max(), d2[..., 1].max()))) 
            a[..., 1] = int((max(a[..., 1].max(), d3[..., 1].max()))) 
            a[..., 1] = int((max(a[..., 1].max(), d4[..., 1].max()))) 
            a[..., 1] = int((max(a[..., 1].max(), d5[..., 1].max()))) 
            a[..., 1] = int((max(a[..., 1].max(), d6[..., 1].max()))) 
            a[..., 1] = int((max(a[..., 1].max(), d7[..., 1].max()))) 
            a[..., 1] = int((max(a[..., 1].max(), d8[..., 1].max())))           
            #print(a[..., 1])
            #if a[..., 1] > 127:
            #    a[..., 1] = 255
            #else:
            #    a[...,1] = 0
            #    
            # red channel
            # a[..., 2] = int(np.sqrt(max(a[..., 2].max(), d2[..., 2].max()))) 
            #
            a[..., 2] = int((max(a[..., 2].max(), d2[..., 2].max()))) 
            a[..., 2] = int((max(a[..., 2].max(), d3[..., 2].max()))) 
            a[..., 2] = int((max(a[..., 2].max(), d4[..., 2].max()))) 
            a[..., 2] = int((max(a[..., 2].max(), d5[..., 2].max()))) 
            a[..., 2] = int((max(a[..., 2].max(), d6[..., 2].max()))) 
            a[..., 2] = int((max(a[..., 2].max(), d7[..., 2].max()))) 
            a[..., 2] = int((max(a[..., 2].max(), d8[..., 2].max())))  
            #print(a[..., 2])
            #if a[..., 2] > 127:
            #    a[..., 2] = 255
            #else:
            #    a[...,2] = 0
            #print(a)
            # kirsch[i,j]= int(np.sqrt(max(list)))
            kirsch[i,j] = a
                         # : Rounding the die length in all directions
            # kirsch[i, j] =int(np.sqrt(d1+d2+d3+d4+d5+d6+d7+d8))
    # for i in range(m):
    #    for j in range(n):
    #        if kirsch[i,j]>127:
    #            kirsch[i,j]=255
    #        else:
    #            kirsch[i,j]=0
    return kirsch    
# ======== kirsch edge detector ========================================
im = cv2.imread('/mnt/c/linuxmirror/testFile1.jpg')
imge = cv2.resize(im,(100,100))
kir = kirsch(imge)
kr = cv2.imwrite('/mnt/c/linuxmirror/kirsch.jpg', kir)
kirmin = kirschmin(imge)
km = cv2.imwrite('/mnt/c/linuxmirror/kirschmin.jpg', kirmin)
im = cv2.imread('/mnt/c/linuxmirror/amadas.jpg')
imge = cv2.resize(im,(100,100))
kir2 = kirsch2(imge)
k2 = cv2.imwrite('/mnt/c/linuxmirror/kirsch2.jpg', kir2)
