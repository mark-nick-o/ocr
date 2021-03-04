#
# Text thinner clarifier
# helps to read some pictures with fat fonts in tesseract / ocrad
#
import cv2
import numpy as np
import os
import sys

if __name__ == '__main__':

    preprocess = "off"                                                  # thresh if you want otsu for leaves
    
    if (len(sys.argv) - 1) <= 0:
        print("please pass the filename for the screenshot you want to analyse")
        sys.exit()

    # ------- read in the requested iamge ---------
    fileNam = "/mnt/c/linuxmirror/" + sys.argv[1]
    if os.path.isfile(fileNam) == False:
	    fileNam = fileNam + ".jpg"
    if os.path.isfile(fileNam) == False:
        print("invalid file name or path %s" % fileNam)	
        sys.exit()
    imcv = cv2.imread(fileNam, cv2.IMREAD_UNCHANGED)
    ## ---- try this on bad fonts
    #
    ret,thresh = cv2.threshold(imcv,55,255,cv2.THRESH_BINARY)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT,(2,2)))
    cv2.imwrite('/mnt/c/linuxmirror/result_1.jpg', opening)

    ## ---- this is an interesting outliner
    #
    Kernel = np.ones((9, 9), dtype=np.uint8)
    IterNum = 1
    OpenImg = cv2.morphologyEx(src=imcv, op=cv2.MORPH_OPEN, kernel=Kernel, iterations=IterNum)
    ErodeImg = cv2.erode(src=imcv, kernel=Kernel, iterations=IterNum)
    DilateImg = cv2.dilate(src=ErodeImg, kernel=Kernel, iterations=IterNum)
    TopHatImg = cv2.morphologyEx(src=imcv, op=cv2.MORPH_TOPHAT, kernel=Kernel, iterations=IterNum)
    BasicTop = imcv - OpenImg
    cv2.imwrite('/mnt/c/linuxmirror/result_2.jpg', OpenImg)
    cv2.imwrite('/mnt/c/linuxmirror/result_3.jpg', DilateImg)
    cv2.imwrite('/mnt/c/linuxmirror/result_4.jpg', TopHatImg)
    cv2.imwrite('/mnt/c/linuxmirror/result_5.jpg', ~BasicTop)

    ## ---- this looks good especially output no. 8
    #
    Kernel = np.ones((9, 9), dtype=np.uint8)
    IterNum = 1
    CloseImg = cv2.morphologyEx(src=imcv, op=cv2.MORPH_CLOSE, kernel=Kernel, iterations=IterNum)
    DilateImg = cv2.dilate(src=imcv, kernel=Kernel, iterations=IterNum)
    ErodeImg = cv2.erode(src=DilateImg, kernel=Kernel, iterations=IterNum)
    BlackHatImg = cv2.morphologyEx(src=imcv, op=cv2.MORPH_BLACKHAT, kernel=Kernel, iterations=IterNum)
    BasicBlack = CloseImg - imcv
    cv2.imwrite('/mnt/c/linuxmirror/result_6.jpg', CloseImg)
    cv2.imwrite('/mnt/c/linuxmirror/result_7.jpg', ErodeImg)
    cv2.imwrite('/mnt/c/linuxmirror/result_8.jpg', BlackHatImg)
    cv2.imwrite('/mnt/c/linuxmirror/result_9.jpg', ~BasicBlack)

    ## ----- use of otsu for leaves not bad results
    #
    gray = cv2.cvtColor(imcv, cv2.COLOR_BGR2GRAY) 
    if preprocess == "thresh": 
        gray = cv2.threshold(gray, 0, 255,
            cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    gray = cv2.medianBlur(gray, 3)
    cv2.imwrite('/mnt/c/linuxmirror/result_10.jpg', gray)    

    ## ----- thresholds (look at color contrasts)
    #
    ret, threshold = cv2.threshold(gray, 200, 240, 10)                  # Here everything that is darker than 150 is replaced by 10, and everything that is brighter - 200
    cv2.imwrite('/mnt/c/linuxmirror/result_11.jpg', threshold)    
                              
    #num_comps, labeled_pixels, comp_stats, comp_centroids = cv2.connectedComponentsWithStats(thresh, connectivity=4)
    #min_comp_area = 10 # pixels
    # get the indices/labels of the remaining components based on the area stat
    # (skip the background component at index 0)
    #remaining_comp_labels = [i for i in range(1, num_comps) if comp_stats[i][4] >= min_comp_area]
    # filter the labeled pixels based on the remaining labels, 
    # assign pixel intensity to 255 (uint8) for the remaining pixels
    #clean_img = np.where(np.isin(labeled_pixels,remaining_comp_labels)==True,255,0).astype('uint8')
    #cv2.imwrite('/mnt/c/linuxmirror/result_2.jpg', clean_img)
