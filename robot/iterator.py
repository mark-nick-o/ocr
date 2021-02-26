import os
import numpy as np
import cv2
import sys
from scipy.ndimage import gaussian_filter

# ======================================================================
#
# The mind for this robot vision reader is to look for a product
# and determine if what we pass as the photo matches for suitablility
# of the correct product chosen
#
# the module uses rotation and inversion to look at the image
#
# re-sizer module operates on image from outside this reader
#
# ======================================================================

if (len(sys.argv) - 1) <= 0:
    print("please pass the filename for the screenshot you want to analyse")
    sys.exit()

# enumerate possible variation types to omit
BanaValue = 1
MintValue = 2
ChocValue = 3
SheepValue = 4
GoatValue = 5
WoodValue = 6
CamelValue = 7

# enumerate possible wrong products to omit
ButterValue = 1
SoapValue = 2
CheeseValue = 3
ShampooValue = 4

# ------- read in the requested iamge ---------
fileNam = "/mnt/c/linuxmirror/" + sys.argv[1]
if os.path.isfile(fileNam) == False:
	fileNam = fileNam + ".jpg"
if os.path.isfile(fileNam) == False:
    print("Invalid file name passed")	
    sys.exit()
im2 = cv2.imread(fileNam) 

# read size & set up the variance we wish to make in order to read the label
(h, w) = im2.shape[:2]
#
# the angle to start the rotation at
# default : 1.5
#
angleInDegrees = 1.5
#
# how much we iterate the angle by in each step
# default : 0.1 (smallest is finest)
#
angleStep = 0.1
#
# how many step changes we will make
#
# the larger the iteration the more we will rotate but the slower it is 
# to get a result
# default : 10
#
# for image CW200 we need to make at least 30 to read milk from the 
# bottle and get class 12 returned, due to the picture angle on the original
# being so tilted
#
numOfIerations = 10
# (10 * 0.1) means +/- 1 degree in either direction 

# flags for searching for a match are initialised at no match

# product
pFound1 = -1
pFound2 = -1
pFound3 = -1
productFound = -1                                                       # valid
productVariation = -1                                                   # next best suggestion
productWrong = -1                                                       # another product 
productFlavor = -1                                                      # another flavour eliminates correct wording 

# search string e.g. supplier
sFound1 = -1
sFound2 = -1
sFoundPart = -1
stringFound = -1

# general product search
generalFound = -1

# iterate up for one degree at a time until the string searched for was seen 
# or we exceeded the number of rotations in that direction
#
for x in range(numOfIerations):
    angleInDegrees=angleInDegrees+(x*angleStep)
    #im3 = cv2.resize(im2,(int(w*10),int(h*6)))
    #im3 = cv2.resize(im2,(int(w*8),int(h*6)))
    #(h, w) = im3.shape[:2]
    scale = 1.0
    center=tuple(np.array([h,w])/2)
    M = cv2.getRotationMatrix2D(center, angleInDegrees, scale)
    rotated = cv2.warpAffine(im2, M, (w, h))
    # filter
    gbresult = gaussian_filter(rotated, sigma=-2)
    mb = cv2.imwrite('/mnt/c/linuxmirror/pic_rot_lefti.jpg', ~gbresult) 
    if (len(sys.argv)-1) == 1:
        f = os.popen('/home/mark/pics/read_label_ocr.sh pic_rot_lefti.jpg')
    elif (len(sys.argv)-1) == 2:
        cmd = '/home/mark/pics/read_label_ocr.sh pic_rot_lefti.jpg ' + sys.argv[2] 
        f = os.popen(cmd)
    strFound = f.read()
    print ("The following text rotating forward invert: ", strFound, angleInDegrees)
    #
    # ================ exit loop when condition is met =================
    #
    # use this if you want to exit when you have read a particular string
    #
    #if not strFound.find("Farm") == -1:
	#    x = 10
    #
    # this example shows how to match the entire specified strings in 
    # one frame to continue and pass the criteria of matching
    #
    # consider пастеризоели = pateurised
    if not strFound.find("Organic") == -1 or not strFound.find("ORGANIC") == -1 or not strFound.find("organic") == -1:
        pFound1 = 0 
    if (not strFound.find("Whole") == -1 and not strFound.find("Milk") == -1) or (not strFound.find("WHOLE") == -1 and not strFound.find("MILK") == -1) or (not strFound.find("whole") == -1 and not strFound.find("milk") == -1): 
        pFound2 = 0  
    if (not strFound.find("Full") == -1 and not strFound.find("Milk") == -1) or (not strFound.find("FULL") == -1 and not strFound.find("MILK") == -1) or (not strFound.find("full") == -1 and not strFound.find("milk") == -1): 
        pFound2 = 0  
    if not pFound2 == -1 and not pFound1 == -1:                         # once this has been seen latch this out
        productFound = 0
    if not strFound.find("Raw") == -1:
        pFound3 = 0
    if not pFound2 == -1 and not pFound3 == -1:                         # product variation is seen :once this has been seen latch this out
        productVariation = 0   
                
    # variants containg the words but not the product    
    # variants of products that may contain the correct words but not be the correct product    
    if not strFound.find("BUTTER") == -1 or not strFound.find("Butter") == -1  or not strFound.find("butter") == -1:
	    productWrong = ButterValue
    if not strFound.find("SOAP") == -1 or not strFound.find("Soap") == -1 or not strFound.find("soap") == -1:
	    productWrong = SoapValue
    if not strFound.find("SHAMPOO") == -1 or not strFound.find("Shampoo") == -1 or not strFound.find("shampoo") == -1:
	    productWrong = ShampooValue
    if not strFound.find("CHEESE") == -1 or not strFound.find("Cheese") == -1 or not strFound.find("cheese") == -1:
	    productWrong = CheeseValue
	# not correct if flavoured, amish wood milk, goat milk, sheep milk
    if not strFound.find("Mint") == -1 or not strFound.find("MINT") == -1: 
        productFlavor = MintValue
    elif not strFound.find("CHOCOLATE") == -1 or not strFound.find("Chocolate") == -1:
        productFlavor = ChocValue
    elif not strFound.find("BANANA") == -1 or not strFound.find("Banana") == -1:
        productFlavor = BanaValue	
    elif (not strFound.find("Wood") == -1 and not strFound.find("Amish")) or (not strFound.find("AMISH") and not strFound.find("WOOD") == -1):
        productFlavor = WoodValue	
    elif not strFound.find("Goat") == -1 or not strFound.find("goat") == -1 or not strFound.find("GOAT") == -1 or not strFound.find("козье") == -1:
        productFlavor = GoatValue
    elif not strFound.find("Sheep") == -1 or not strFound.find("SHEEP") == -1 or not strFound.find("EWE") == -1 or not strFound.find("овече") == -1:
        productFlavor = SheepValue
    elif not strFound.find("Camel") == -1 or not strFound.find("CAMEL") == -1 or not strFound.find("camel") == -1:
        productFlavor = CamelValue
    #
    # ==================================================================
    #
    # use this if you want to exit when you have read a particular string
    # from each overall rotated reading (cumalative) 
    #
    # this one exits once we saw both from any rotation
    #
    if strFound.find("FARM") != -1 or strFound.find("Farm") != -1:      # we are looking for farm product 
        sFound1 = 0
    if not strFound.find("Berkeley") == -1:                             # one example of farm milk product 
        sFound2 = 0	
    elif not strFound.find("IVY") == -1 and not strFound.find("HOUSE") == -1: # one example of farm milk product   
        sFound2 = 0	
    elif not strFound.find("HOUSE") == -1 and strFound.find("IVY") == -1:  # one partial example of farm milk product  
        sFoundPart = 0	
    elif strFound.find("HOUSE") == -1 and not strFound.find("IVY") == -1:  # one partial example of farm milk product  
        sFoundPart = 0	
    elif not sFoundPart == -1 and not strFound.find("IVY") == -1:       # one example of farm milk product now fully seen 
        sFound2 = 0	
    elif not sFoundPart == -1 and not strFound.find("HOUSE") == -1:     # one example of farm milk product now fully seen 
        sFound2 = 0		
    if not sFound1 == -1 and not sFound2 == -1:                         # full farm product manufacturer met
        stringFound = 0
   
    # look for general product (russian text translation was not working so hardcoded it)
    if not strFound.find("Milk") == -1 or not strFound.find("MILK") == -1 or not strFound.find("Mik") == -1 or not strFound.find("milk") == -1 or not strFound.find("молоко") == -1:
        generalFound = 0
    #
    # found the string and the product on the label
    #
    if not stringFound == -1 and not productFound == -1:
        x = 12 
		
    #        
    # now repeat for the iamge NOT inverted
    #
    mb = cv2.imwrite('/mnt/c/linuxmirror/pic_rot_left.jpg', gbresult) 
    if (len(sys.argv)-1) == 1:
        f = os.popen('/home/mark/pics/read_label_ocr.sh pic_rot_left.jpg')
    elif (len(sys.argv)-1) == 2:
        cmd = '/home/mark/pics/read_label_ocr.sh pic_rot_left.jpg ' + sys.argv[2] 
        f = os.popen(cmd)
    strFound = f.read()
    print ("The following text rotating forward invert: ", strFound, angleInDegrees)
    #
    # ================ exit loop when condition is met =================
    #
    # use this if you want to exit when you have read a particular string
    #
    #if not strFound.find("Farm") == -1:
	#    x = 10
    #
    # this example shows how to match the entire specified strings in 
    # one frame to continue and pass the criteria of matching
    #
    if not strFound.find("Organic") == -1 or not strFound.find("ORGANIC") == -1 or not strFound.find("organic") == -1:
        pFound1 = 0 
    if (not strFound.find("Whole") == -1 and not strFound.find("Milk") == -1) or (not strFound.find("WHOLE") == -1 and not strFound.find("MILK") == -1) or (not strFound.find("whole") == -1 and not strFound.find("milk") == -1): 
        pFound2 = 0  
    if (not strFound.find("Full") == -1 and not strFound.find("Milk") == -1) or (not strFound.find("FULL") == -1 and not strFound.find("MILK") == -1) or (not strFound.find("full") == -1 and not strFound.find("milk") == -1): 
        pFound2 = 0  
    if not pFound2 == -1 and not pFound1 == -1:                         # once this has been seen latch this out
        productFound = 0
    if not strFound.find("Raw") == -1:
        pFound3 = 0
    if not pFound2 == -1 and not pFound3 == -1:                         # product variation is seen :once this has been seen latch this out
        productVariation = 0   
                
    # variants of products that may contain the correct words but not the correct product    
    if not strFound.find("BUTTER") == -1 or not strFound.find("Butter") == -1  or not strFound.find("butter") == -1:
	    productWrong = ButterValue
    if not strFound.find("SOAP") == -1 or not strFound.find("Soap") == -1 or not strFound.find("soap") == -1:
	    productWrong = SoapValue
    if not strFound.find("SHAMPOO") == -1 or not strFound.find("Shampoo") == -1 or not strFound.find("shampoo") == -1:
	    productWrong = ShampooValue
    if not strFound.find("CHEESE") == -1 or not strFound.find("Cheese") == -1 or not strFound.find("cheese") == -1:
	    productWrong = CheeseValue
	# not correct if flavoured, amish wood milk, goat milk, sheep milk
    if not strFound.find("Mint") == -1 or not strFound.find("MINT") == -1: 
        productFlavor = MintValue
    elif not strFound.find("CHOCOLATE") == -1 or not strFound.find("Chocolate") == -1:
        productFlavor = ChocValue
    elif not strFound.find("BANANA") == -1 or not strFound.find("Banana") == -1:
        productFlavor = BanaValue	
    elif (not strFound.find("Wood") == -1 and not strFound.find("Amish")) or (not strFound.find("AMISH") and not strFound.find("WOOD") == -1):
        productFlavor = WoodValue	
    elif not strFound.find("Goat") == -1 or not strFound.find("goat") == -1 or not strFound.find("GOAT") == -1 or not strFound.find("козье") == -1:
        productFlavor = GoatValue
    elif not strFound.find("Sheep") == -1 or not strFound.find("SHEEP") == -1 or not strFound.find("EWE") == -1 or not strFound.find("овече") == -1:
        productFlavor = SheepValue
    elif not strFound.find("Camel") == -1 or not strFound.find("CAMEL") == -1 or not strFound.find("camel") == -1:
        productFlavor = CamelValue
    #
    # ==================================================================
    #
    # use this if you want to exit when you have read a particular string
    # from each overall rotated reading (cumalative) 
    #
    # this one exits once we saw both from any rotation
    #
    if strFound.find("FARM") != -1 or strFound.find("Farm") != -1:      # we are looking for farm product 
        sFound1 = 0
    if not strFound.find("Berkeley") == -1:                             # one example of farm milk product 
        sFound2 = 0	
    elif not strFound.find("IVY") == -1 and not strFound.find("HOUSE") == -1: # one example of farm milk product   
        sFound2 = 0	
    elif not strFound.find("HOUSE") == -1 and strFound.find("IVY") == -1:  # one partial example of farm milk product  
        sFoundPart = 0	
    elif strFound.find("HOUSE") == -1 and not strFound.find("IVY") == -1:  # one partial example of farm milk product  
        sFoundPart = 0	
    elif not sFoundPart == -1 and not strFound.find("IVY") == -1:       # one example of farm milk product now fully seen 
        sFound2 = 0	
    elif not sFoundPart == -1 and not strFound.find("HOUSE") == -1:     # one example of farm milk product now fully seen 
        sFound2 = 0		
    if not sFound1 == -1 and not sFound2 == -1:                         # full farm product manufacturer met
        stringFound = 0
    # look for general product 
    if not strFound.find("Milk") == -1 or not strFound.find("MILK") == -1 or not strFound.find("Mik") == -1 or not strFound.find("milk") == -1 or not strFound.find("молоко") == -1:
        generalFound = 0
    #
    # found the string and the product on the label
    #
    if not stringFound == -1 and not productFound == -1:
        x = 12    
        
if not stringFound == -1 and not productFound == -1:                    # the product and supplier was found
	print("1")
#    sys.exit()
    
# reset the angle to unity
angleInDegrees=1.5

# iterate down for one degree until the string searched for was seen 
for x in range(numOfIerations):
    angleInDegrees=angleInDegrees-(x*angleStep)
    #im3 = cv2.resize(im2,(int(w*10),int(h*6)))
    #im3 = cv2.resize(im2,(int(w*8),int(h*6)))
    #(h, w) = im3.shape[:2]
    scale = 1.0
    center=tuple(np.array([h,w])/2)
    M = cv2.getRotationMatrix2D(center, angleInDegrees, scale)
    rotated = cv2.warpAffine(im2, M, (w, h))
    # filter
    gbresult = gaussian_filter(rotated, sigma=-2)
    mb = cv2.imwrite('/mnt/c/linuxmirror/pic_rot_righti.jpg', ~gbresult)  
    if (len(sys.argv)-1) == 1:
        f = os.popen('/home/mark/pics/read_label_ocr.sh pic_rot_righti.jpg')
    elif (len(sys.argv)-1) == 2:
        cmd = '/home/mark/pics/read_label_ocr.sh pic_rot_righti.jpg ' + sys.argv[2] 
        f = os.popen(cmd)
    strFound = f.read()
    print ("The following text was read rotating backward invert : ", strFound, angleInDegrees)
    #
    # ================ exit loop when condition is met =================
    #
    # use this if you want to exit when you have read a particular string
    #
    #if not strFound.find("Farm") == -1:
	#    x = 10
    #
    # this example shows how to match the entire specified strings in 
    # one frame to continue and pass the criteria of matching
    #
    if not strFound.find("Organic") == -1 or not strFound.find("ORGANIC") == -1 or not strFound.find("organic") == -1:
        pFound1 = 0 
    if (not strFound.find("Whole") == -1 and not strFound.find("Milk") == -1) or (not strFound.find("WHOLE") == -1 and not strFound.find("MILK") == -1) or (not strFound.find("whole") == -1 and not strFound.find("milk") == -1): 
        pFound2 = 0  
    if (not strFound.find("Full") == -1 and not strFound.find("Milk") == -1) or (not strFound.find("FULL") == -1 and not strFound.find("MILK") == -1) or (not strFound.find("full") == -1 and not strFound.find("milk") == -1): 
        pFound2 = 0  
    if not pFound2 == -1 and not pFound1 == -1:                         # once this has been seen latch this out
        productFound = 0
    if not strFound.find("Raw") == -1:
        pFound3 = 0
    if not pFound2 == -1 and not pFound3 == -1:                         # product variation is seen :once this has been seen latch this out
        productVariation = 0   
                
    # variants containg the words but not the product    
    # variants of products that may contain the correct words but not the correct product    
    if not strFound.find("BUTTER") == -1 or not strFound.find("Butter") == -1  or not strFound.find("butter") == -1:
	    productWrong = ButterValue
    if not strFound.find("SOAP") == -1 or not strFound.find("Soap") == -1 or not strFound.find("soap") == -1:
	    productWrong = SoapValue
    if not strFound.find("SHAMPOO") == -1 or not strFound.find("Shampoo") == -1 or not strFound.find("shampoo") == -1:
	    productWrong = ShampooValue
    if not strFound.find("CHEESE") == -1 or not strFound.find("Cheese") == -1 or not strFound.find("cheese") == -1:
	    productWrong = CheeseValue
	# not correct if flavoured, amish wood milk, goat milk, sheep milk
    if not strFound.find("Mint") == -1 or not strFound.find("MINT") == -1: 
        productFlavor = MintValue
    elif not strFound.find("CHOCOLATE") == -1 or not strFound.find("Chocolate") == -1:
        productFlavor = ChocValue
    elif not strFound.find("BANANA") == -1 or not strFound.find("Banana") == -1:
        productFlavor = BanaValue	
    elif (not strFound.find("Wood") == -1 and not strFound.find("Amish")) or (not strFound.find("AMISH") and not strFound.find("WOOD") == -1):
        productFlavor = WoodValue	
    elif not strFound.find("Goat") == -1 or not strFound.find("goat") == -1 or not strFound.find("GOAT") == -1 or not strFound.find("козье") == -1:
        productFlavor = GoatValue
    elif not strFound.find("Sheep") == -1 or not strFound.find("SHEEP") == -1 or not strFound.find("EWE") == -1 or not strFound.find("овече") == -1:
        productFlavor = SheepValue
    elif not strFound.find("Camel") == -1 or not strFound.find("CAMEL") == -1 or not strFound.find("camel") == -1:
        productFlavor = CamelValue
    #
    # ==================================================================
    #
    # use this if you want to exit when you have read a particular string
    # from each overall rotated reading (cumalative) 
    #
    # this one exits once we saw both from any rotation
    #
    if strFound.find("FARM") != -1 or strFound.find("Farm") != -1:      # we are looking for farm product 
        sFound1 = 0
    if not strFound.find("Berkeley") == -1:                             # one example of farm milk product 
        sFound2 = 0	
    elif not strFound.find("IVY") == -1 and not strFound.find("HOUSE") == -1: # one example of farm milk product   
        sFound2 = 0	
    elif not strFound.find("HOUSE") == -1 and strFound.find("IVY") == -1:  # one partial example of farm milk product  
        sFoundPart = 0	
    elif strFound.find("HOUSE") == -1 and not strFound.find("IVY") == -1:  # one partial example of farm milk product  
        sFoundPart = 0	
    elif not sFoundPart == -1 and not strFound.find("IVY") == -1:       # one example of farm milk product now fully seen 
        sFound2 = 0	
    elif not sFoundPart == -1 and not strFound.find("HOUSE") == -1:     # one example of farm milk product now fully seen 
        sFound2 = 0		
    if not sFound1 == -1 and not sFound2 == -1:                         # full farm product manufacturer met
        stringFound = 0
    # look for general product 
    if not strFound.find("Milk") == -1 or not strFound.find("MILK") == -1 or not strFound.find("Mik") == -1 or not strFound.find("milk") == -1 or not strFound.find("молоко") == -1:
       generalFound = 0
    #
    # found the string and the product on the label
    #
    if not stringFound == -1 and not productFound == -1:
        x = 12 

    mb = cv2.imwrite('/mnt/c/linuxmirror/pic_rot_right.jpg', gbresult)  
    if (len(sys.argv)-1) == 1:
        f = os.popen('/home/mark/pics/read_label_ocr.sh pic_rot_right.jpg')
    elif (len(sys.argv)-1) == 2:
        cmd = '/home/mark/pics/read_label_ocr.sh pic_rot_right.jpg ' + sys.argv[2] 
        f = os.popen(cmd)
    strFound = f.read()
    print ("The following text was read rotating backward  : ", strFound, angleInDegrees)
    #
    # ================ exit loop when condition is met =================
    #
    # use this if you want to exit when you have read a particular string
    #
    #if not strFound.find("Farm") == -1:
	#    x = 10
    #
    # this example shows how to match the entire specified strings in 
    # one frame to continue and pass the criteria of matching
    #
    if not strFound.find("Organic") == -1 or not strFound.find("ORGANIC") == -1 or not strFound.find("organic") == -1:
        pFound1 = 0 
    if (not strFound.find("Whole") == -1 and not strFound.find("Milk") == -1) or (not strFound.find("WHOLE") == -1 and not strFound.find("MILK") == -1) or (not strFound.find("whole") == -1 and not strFound.find("milk") == -1): 
        pFound2 = 0  
    if (not strFound.find("Full") == -1 and not strFound.find("Milk") == -1) or (not strFound.find("FULL") == -1 and not strFound.find("MILK") == -1) or (not strFound.find("full") == -1 and not strFound.find("milk") == -1): 
        pFound2 = 0  
    if not pFound2 == -1 and not pFound1 == -1:                         # once this has been seen latch this out
        productFound = 0
    if not strFound.find("Raw") == -1:
        pFound3 = 0
    if not pFound2 == -1 and not pFound3 == -1:                         # product variation is seen :once this has been seen latch this out
        productVariation = 0   
                
    # variants containg the words but not the product    
    # variants of products that may contain the correct words but not the correct product    
    if not strFound.find("BUTTER") == -1 or not strFound.find("Butter") == -1  or not strFound.find("butter") == -1:
	    productWrong = ButterValue
    if not strFound.find("SOAP") == -1 or not strFound.find("Soap") == -1 or not strFound.find("soap") == -1:
	    productWrong = SoapValue
    if not strFound.find("SHAMPOO") == -1 or not strFound.find("Shampoo") == -1 or not strFound.find("shampoo") == -1:
	    productWrong = ShampooValue
    if not strFound.find("CHEESE") == -1 or not strFound.find("Cheese") == -1 or not strFound.find("cheese") == -1:
	    productWrong = CheeseValue
	# not correct if flavoured, amish wood milk, goat milk, sheep milk
    if not strFound.find("Mint") == -1 or not strFound.find("MINT") == -1: 
        productFlavor = MintValue
    elif not strFound.find("CHOCOLATE") == -1 or not strFound.find("Chocolate") == -1:
        productFlavor = ChocValue
    elif not strFound.find("BANANA") == -1 or not strFound.find("Banana") == -1:
        productFlavor = BanaValue	
    elif (not strFound.find("Wood") == -1 and not strFound.find("Amish")) or (not strFound.find("AMISH") and not strFound.find("WOOD") == -1):
        productFlavor = WoodValue	
    elif not strFound.find("Goat") == -1 or not strFound.find("goat") == -1 or not strFound.find("GOAT") == -1 or not strFound.find("козье") == -1:
        productFlavor = GoatValue
    elif not strFound.find("Sheep") == -1 or not strFound.find("SHEEP") == -1 or not strFound.find("EWE") == -1 or not strFound.find("овече") == -1:
        productFlavor = SheepValue
    elif not strFound.find("Camel") == -1 or not strFound.find("CAMEL") == -1 or not strFound.find("camel") == -1:
        productFlavor = CamelValue
    #
    # ==================================================================
    #
    # use this if you want to exit when you have read a particular string
    # from each overall rotated reading (cumalative) 
    #
    # this one exits once we saw both from any rotation
    #
    if strFound.find("FARM") != -1 or strFound.find("Farm") != -1:      # we are looking for farm product 
        sFound1 = 0
    if not strFound.find("Berkeley") == -1:                             # one example of farm milk product 
        sFound2 = 0	
    elif not strFound.find("IVY") == -1 and not strFound.find("HOUSE") == -1: # one example of farm milk product   
        sFound2 = 0	
    elif not strFound.find("HOUSE") == -1 and strFound.find("IVY") == -1:  # one partial example of farm milk product  
        sFoundPart = 0	
    elif strFound.find("HOUSE") == -1 and not strFound.find("IVY") == -1:  # one partial example of farm milk product  
        sFoundPart = 0	
    elif not sFoundPart == -1 and not strFound.find("IVY") == -1:       # one example of farm milk product now fully seen 
        sFound2 = 0	
    elif not sFoundPart == -1 and not strFound.find("HOUSE") == -1:     # one example of farm milk product now fully seen 
        sFound2 = 0		
    if not sFound1 == -1 and not sFound2 == -1:                         # full farm product manufacturer met
        stringFound = 0
    # look for general product 
    if not strFound.find("Milk") == -1 or not strFound.find("MILK") == -1 or not strFound.find("Mik") == -1 or not strFound.find("milk") == -1 or not strFound.find("молоко") == -1:
       generalFound = 0
    #
    # found the string and the product on the label
    #
    if not stringFound == -1 and not productFound == -1:
        x = 12 
        
#
# conclude the result to the calling process ranking on suitability
# in the rules we asked for :-
# organic whole milk = product
# ivy house or berkerley farm = supplier
# we are able to read the bottles in eng,fra,jpn,rus,ger,spa,ita
# 
if not productWrong == -1:                                              # a wrong product word had been detected which eliminates the product
    retVal = 30 + productWrong                                          # wrong product was found i.e butter (even if it says organic whole milk farm)
    print(retVal)
elif productFlavor == -1:                                                 # no product variance occurred
    if not stringFound == -1 and not productFound == -1:                # the product and supplier was found - dedicated farm, organic whole milk
	    print("1")
    elif stringFound == -1 and not sFound1 == -1 and not productFound == -1:# the product was found from another farm supplier (farm organic whole milk)
        print("2")
    elif stringFound == -1 and not productFound == -1:                  # the product was found from another supplier (organic whole milk)
        print("3")
    elif not stringFound == -1 and productFound == -1:                  # the supplier was found but a different product
        print("4")
    elif not productVariation == -1:                                    # product variation very similar was found (raw rather than organic "Whole Milk" stated Raw/Unpasteurised)
	    print("5") 
    elif stringFound == -1 and productFound == -1 and not sFound1 == - 1 and not generalFound == -1: # the supplier was similar (farm) and similar product (keyword - milk)
        print("6") 
    elif not pFound2 == -1 and stringFound == -1 and productFound == -1 and not generalFound == -1: # the supplier not farm but similar product (keyword - whole milk)
        print("7")  
    elif not pFound1 == -1 and not pFound3 == -1 and stringFound == -1 and productFound == -1 and not generalFound == -1: # the supplier not was farm but similar product (keyword - raw organic milk)
        print("8") 
    elif not pFound1 == -1 and stringFound == -1 and productFound == -1 and not generalFound == -1: # the supplier not farm but similar product (keyword - organic milk)
        print("9") 
    elif not pFound3 == -1 and stringFound == -1 and productFound == -1 and not generalFound == -1: # the supplier not was farm but similar product (keyword - raw milk)
        print("10")  
    elif stringFound == -1 and productFound == -1 and not generalFound == -1: # the supplier not was farm but similar product (keyword - milk)
        print("11")   
    else:
        print("12")                                                     # no match ( if we get no output from the ocr we need to enter a re-sizing method to get sensible ocr reader working)
else:
    if not generalFound == -1:                                          # it was a milk
        retVal = 20 + productFlavor                                     # return another product code (the flavor or variant of the product i.e. cow goat camel)
        print(retVal)
    else:
	    retVal = 40 + productFlavor                                     # saw a keyword without milk (e.g. cheese chocolate goat)
	    print(retVal)
