# ======================================================================
#
# The mind for this robot vision reader is to look for a product
# and determine if what we pass as the photo matches for suitablility
# of the correct product chosen
#
# the module uses rotation and inversion to look at the image
#
# re-sizer module operates on image from outside this reader
# unwrapper module also operates from outside this reader
#
# so far not bad success on reading and categorising all the images
# correctly
#
# ======================================================================

import os
import platform
import numpy as np
import cv2
import sys
from scipy.ndimage import gaussian_filter
import re

syst=platform.system()
#
# ----------------------------------------------------------------------
# add for windows support of tesseract ocr (install it first)
# and also the python extension
# pip install pytesseract
# conda install -c conda-forge pytesseract 
# ----------------------------------------------------------------------
#
if not syst.find("Win") == -1:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
#
# choose the config language if you want
# config = r'--oem 3 --psm 6'

if (len(sys.argv) - 1) <= 0:
    print("please pass the filename for the screenshot you want to analyse")
    sys.exit()

# ------------- Get Flavor if there is one -----------------------------
# enumerate possible variation types which are flavors to omit
# it can be the product but is a variant with these key words
BanaValue = 1
MintValue = 2
ChocValue = 3
WoodValue = 4
BlueValue = 5                                                           #blueberries / mirtili
MochaValue = 6
StrawBryVal = 7
OrangeValue = 8
PeachValue = 9
LemonValue = 10
ApricotValue = 11
PearValue = 12
AppleValue = 13
RaspberryValue = 14
CherryValue = 15
NumOfFlavors = 20                                                       # leave for 6 spare flavors for now

# ------------- Get alternate source if there is one -------------------
# enumerate possible variation types which are sources to omit
# it can be the product but is a variant with these key words
CowValue = 0
SheepValue = 2
GoatValue = 1
DonkeyValue = 3
BuffaloValue = 4
SoyValue = 5
AlmondValue = 6
RiceValue = 7
CamelValue = 8
NumOfVariants = 10
 
variaMilkStart = 30
variationStart = (NumOfVariants*NumOfFlavors) + NumOfFlavors

# ------------ Identify Product ----------------------------------------
# enumerate possible wrong products to omit
# the description was matched but if we have these strings its not what 
# we are looking for
#
# we are just identifying the single product for eliminaiton from the rank
# ignores type and flavor attribute (dont have flavors)
#
noProduct = -1                                                          # used to reset the product in cases where the string can mean supplier for example
CreamValue = 0                                                          # cream / flower (used for fior di latte) 
ButterValue = 1
CheeseValue = 2
SoapValue = 3
ShampooValue = 4
Ravaggiolo = 5                                                          #- not in engine (an italian cheese)
Balsam = 6
Liqor = 7
Grappa = 8                                                              # grappa / grappe
Shower = 9
Kefir = 10
Biscuit = 11
# yogurt is last one in this sequence as it can also have a flavor attribute 
# (in all these cases above we are ignoring the flavor attribute)
# we are still ignoring the type attribute for yoghurt in this example
#
Yogurt = 12
# chocolate is a product derived from phrasing and this time we are listing 
# the types of the item not the flavors
# 
ChocoBar=20
NumOfProducts = ChocoBar

wrongStart = ((NumOfVariants*NumOfFlavors) + (NumOfFlavors*2)) 

# set a flag stating remove yoghurt this is in the situation
# were we saw milk with a contact address as 
# office@fructjoghurt.com
# we say if we got a @ or a . attached to that word remove and ignore the word
# for the whole ocr iteration
#
productRemove = 0                                                       # this product contains a negative removal string as described above if we see that this is set to the productId
                                                            
# ------- read in the requested iamge ---------
fileNam = "/mnt/c/linuxmirror/" + sys.argv[1]
if os.path.isfile(fileNam) == False:
	fileNam = fileNam + ".jpg"
if os.path.isfile(fileNam) == False:
    print("Invalid file name passed")	
    sys.exit()
im2 = cv2.imread(fileNam) 

# ----- adaptive gaussian thresholding -----------------------------
#img = cv2.medianBlur(im2,5)
#ret,th1 = cv2.threshold(img,127,255,cv2.THRESH_BINARY)
# ----- adaptive mean thresholding ---------------------------------
#th2 = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,11,2)
# ----- adaptive gaussian thresholding -----------------------------
#th3 = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    
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
# for image 253.jpg we need to make at least 30 to read milk from the 
# bottle and get class 12 returned, due to the picture angle on the original
# being so tilted
#
# image 24.jpg needed value of 15 this was enough to read tilted vollmilch
#
numOfIerations = 30
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
productType = -1                                                        # source of milk e.g. goat, sheep, donkey

# search string e.g. supplier
sFound1 = -1
sFound2 = -1
sFoundPart = -1
stringFound = -1

# general product search
generalFound = -1

# phrase selection in english language "milk chocolate"
# note if required needs to be done separate in each lanuage
# e.g. cioccolata il latte di pecora
# chocolate milk sheep when tarnslated does not work
#
chocoPhrase = 0
noFlavor = 0

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
    # erosion to thin font if needed 
    # for example on image 33
    #kernel = np.ones((5,5),np.uint8)
    #erosion = cv2.erode(im2,kernel,iterations = 3)
    #dilated = cv2.dilate(rotated,kernel,iterations = 1)
    # filter
    gbresult = gaussian_filter(rotated, sigma=-2)
    #gbresult = gaussian_filter(erosion, sigma=-2)

    # ------------------ for linux -------------------------------------
    if not syst.find("Lin") == -1:
        if (len(sys.argv)-1) == 2 and not sys.argv[2].find("ocrad") == -1:  # argument is ocrad ocr instead
           im_rgb = cv2.cvtColor(~gbresult, cv2.COLOR_BGR2RGB)
           mb = cv2.imwrite('/mnt/c/linuxmirror/pic_rot_lefti.pnm', im_rgb)
        else:                                                           # argument is country code 
           mb = cv2.imwrite('/mnt/c/linuxmirror/pic_rot_lefti.jpg', ~gbresult) 

        if (len(sys.argv)-1) == 1:
            f = os.popen('/home/mark/pics/read_label_ocr.sh pic_rot_lefti.jpg')
        elif (len(sys.argv)-1) == 2:                                    # argument is country code or ocrad
            cmd = '/home/mark/pics/read_label_ocr.sh pic_rot_lefti ' + sys.argv[2]     
            f = os.popen(cmd)
        strFound = f.read()
    #
    # --------------------- for windows --------------------------------
    elif not syst.find("Win") == -1:
        im_rgb = cv2.cvtColor(~gbresult, cv2.COLOR_BGR2RGB)
    #  if you use a custom config strFound = pytesseract.image_to_string(im_rgb, config=config)
        if (len(sys.argv)-1) == 2:
            if not sys.argv[2].find("fr") == -1: 
                strFound = pytesseract.image_to_string(im_rgb, lang='eng+fra')
            elif not sys.argv[2].find("de") == -1: 
                strFound = pytesseract.image_to_string(im_rgb, lang='eng+deu')   
            elif not sys.argv[2].find("it") == -1: 
                strFound = pytesseract.image_to_string(im_rgb, lang='eng+ita') 
            elif not sys.argv[2].find("jp") == -1: 
                strFound = pytesseract.image_to_string(im_rgb, lang='eng+jpn') 
            elif not sys.argv[2].find("ru") == -1: 
                strFound = pytesseract.image_to_string(im_rgb, lang='eng+rus') 
            elif not sys.argv[2].find("sp") == -1: 
                strFound = pytesseract.image_to_string(im_rgb, lang='eng+spa')
            else:
                strFound = pytesseract.image_to_string(im_rgb)				
        else:
            strFound = pytesseract.image_to_string(im_rgb)		 
                                                 
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
    
    # cream must be exact matched to remove creamery being a match
    pattern = re.compile(r"\bcream\b")
            
    if not strFound.find("BUTTER") == -1 or not strFound.find("Butter") == -1  or not strFound.find("butter") == -1:
	    productWrong = ButterValue
    elif not strFound.find("SOAP") == -1 or not strFound.find("Soap") == -1 or not strFound.find("soap") == -1:
	    productWrong = SoapValue
    elif not strFound.find("SHAMPOO") == -1 or not strFound.find("Shampoo") == -1 or not strFound.find("shampoo") == -1:
	    productWrong = ShampooValue
    elif not strFound.find("CHEESE") == -1 or not strFound.find("Cheese") == -1 or not strFound.find("cheese") == -1:
	    productWrong = CheeseValue
    elif not strFound.find("RAVAGGIOLO") == -1 or not strFound.find("Ravaggiolo") == -1 or not strFound.find("ravaggiolo") == -1:
        productWrong = Ravaggiolo
    elif not strFound.find("BALSAM") == -1 or not strFound.find("Balsam") == -1 or not strFound.find("balsam") == -1:
        productWrong = Balsam
    elif not strFound.find("GRAPPA") == -1 or not strFound.find("Grappa") == -1 or not strFound.find("grappa") == -1 or not strFound.find("GRAPPE") == -1 or not strFound.find("Grappe") == -1 or not strFound.find("grappe") == -1:
        productWrong = Grappa
    elif re.search(pattern, strFound.lower()) or not strFound.find("flower") == -1 or not strFound.find("Flower") == -1 or not strFound.find("FLOWER") == -1:
        productWrong = CreamValue  
    elif not strFound.find("YOGURT") == -1 or not strFound.find("Yogurt") == -1 or not strFound.find("yogurt") == -1 or not strFound.find("yoghurt") == -1 or not strFound.find("Yoghurt") == -1 or not strFound.find("YOGHURT") == -1:
        productWrong = Yogurt
        # ----- look to see if this is true a product description ------
        #
        # if we found Yogurt we possibly eliminate it being the product
        # as some email is farmer@yogurtcremery.com
        # or web address might be www.yogurtfarms.com
        # it may still be milk so set the remove status to yogurt and
        # decide on the combination of keywords read from the label at 
        # the end of the sequence
        #  
        i = 0                                          
        inWordArray = strFound.split()
        sizeOfList = len(inWordArray)
        while i < sizeOfList:
            #if (not inWordArray[i].find("Yogurt") == -1 or not inWordArray[i].find("YOGURT") == -1 or not inWordArray[i].find("yogurt") == -1) and (not inWordArray[i].find("@") == -1 and not inWordArray[i].find(".") == -1):	# found product yogurt between @ and .		         
            if (not inWordArray[i].find("Yogurt") == -1 or not inWordArray[i].find("YOGURT") == -1 or not inWordArray[i].find("yogurt") == -1) and (not inWordArray[i].find("@") == -1 or not inWordArray[i].find(".") == -1):	# found product containing @ or . with yogurt (ocr stream)	
                productRemove == Yogurt                                 # suggest removing product if no flavor found and we found keyword milk (logic is at end after all picture iterations)
            i += 1
    elif not strFound.find("SOAP") == -1 or not strFound.find("Soap") == -1 or not strFound.find("soap") == -1:
        productWrong = SoapValue
    elif not strFound.find("SHOWER") == -1 or not strFound.find("Shower") == -1 or not strFound.find("shower") == -1:
        productWrong = Shower
    elif not strFound.find("KEFIR") == -1 or not strFound.find("Kefir") == -1 or not strFound.find("kefir") == -1:
        productWrong = Kefir
    elif not strFound.find("BISCUIT") == -1 or not strFound.find("Biscuit") == -1 or not strFound.find("biscuit") == -1:
        productWrong = Biscuit   

    if not strFound.find("RemovYog") == -1:                             # if this is seen in the stream we want to remove that product as it was for example and email not the product
        productRemove = Yogurt                                          # example pic office@naturjoghurt.at (you must add other products if you have emails like mrX@cheeseprods.com and also sell milk
        
    if not strFound.find("КОЗЬЕ") == -1:
        productType = GoatValue
        		                              	    
	# not correct if flavoured, amish wood milk, goat milk, sheep milk
    if not strFound.find("Goat") == -1 or not strFound.find("goat") == -1 or not strFound.find("GOAT") == -1 or not strFound.find("KO3bE") == -1 or not strFound.find("козье") == -1:
        productType = GoatValue
    elif not strFound.find("Sheep") == -1 or not strFound.find("SHEEP") == -1 or not strFound.find("sheep") == -1 or not strFound.find("EWE") == -1 or not strFound.find("овече") == -1:
        productType = SheepValue
    elif not strFound.find("Camel") == -1 or not strFound.find("CAMEL") == -1 or not strFound.find("camel") == -1:
        productType = CamelValue
    elif not strFound.find("Donkey") == -1 or not strFound.find("DONKEY") == -1 or not strFound.find("donkey") == -1:
        productType = DonkeyValue
    elif not strFound.find("Buffalo") == -1 or not strFound.find("BUFFALO") == -1 or not strFound.find("buffalo") == -1:
        productType = BuffaloValue

    # in german the word "packen" came up as possibly "grapple" this meant in we got apple flavor when it wasnt
    # so match apple exactly maybe should be others too.. not needed in the challenge
    #
    pattern = re.compile(r"\bapple\b")
    pattern2 = re.compile(r"\bmint\b")
                        
    if re.search(pattern2, strFound.lower()):  
        productFlavor = MintValue
    elif not strFound.find("CHOCOLATE") == -1 or not strFound.find("Chocolate") == -1 or not strFound.find("chocolate") == -1:
        productFlavor = ChocValue
    elif not strFound.find("BANANA") == -1 or not strFound.find("Banana") == -1 or not strFound.find("banana") == -1:
        productFlavor = BanaValue	
    elif (not strFound.find("Wood") == -1 and not strFound.find("Amish")) or (not strFound.find("AMISH") and not strFound.find("WOOD") == -1):
        productFlavor = WoodValue	
    elif not strFound.find("Blue") == -1 or not strFound.find("BLUE") == -1 or not strFound.find("blue") == -1 or not strFound.find("Mirtili") == -1 or not strFound.find("MIRTILI") == -1 or not strFound.find("mirtili") == -1:
        productFlavor = BlueValue
    elif not strFound.find("Mocha") == -1 or not strFound.find("MOCHA") == -1 or not strFound.find("mocha") == -1 or not strFound.find("Coffee") == -1 or not strFound.find("COFFEE") == -1 or not strFound.find("coffee") == -1:
        productFlavor = MochaValue
    elif not strFound.find("Straw") == -1 or not strFound.find("STRAW") == -1 or not strFound.find("straw") == -1:
        productFlavor = StrawBryVal
    elif not strFound.find("Orange") == -1 or not strFound.find("ORANGE") == -1 or not strFound.find("orange") == -1:
        productFlavor = OrangeValue
    elif not strFound.find("Peach") == -1 or not strFound.find("PEACH") == -1 or not strFound.find("peach") == -1:
        productFlavor = PeachValue
    elif not strFound.find("Lemon") == -1 or not strFound.find("LEMON") == -1 or not strFound.find("lemon") == -1:
        productFlavor = LemonValue
    elif not strFound.find("Apricot") == -1 or not strFound.find("APRICOT") == -1 or not strFound.find("apricot") == -1:
        productFlavor = ApricotValue
    elif not strFound.find("Pear") == -1 or not strFound.find("PEAR") == -1 or not strFound.find("pear") == -1:
        productFlavor = PearValue
    elif re.search(pattern, strFound.lower()):                          # apple must be exact
        productFlavor = AppleValue
    elif not strFound.find("Raspberry") == -1 or not strFound.find("RASPBERRY") == -1 or not strFound.find("raspberry") == -1:
        productFlavor = RaspberryValue
    elif not strFound.find("Cherr") == -1 or not strFound.find("CHERR") == -1 or not strFound.find("cherr") == -1:  # cherry or cherries
        productFlavor = CherryValue
        
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

    # ------------- look for general product match ---------------------           
    # look for general product (russian text translation was not working so hardcoded it)
    if not strFound.find("Milk") == -1 or not strFound.find("MILK") == -1 or not strFound.find("Mik") == -1 or not strFound.find("milk") == -1 or not strFound.find("МОЛОКО") == -1 or not strFound.find("молоко") == -1:
        generalFound = 0
    #
    # ------------- example of phrase selection ------------------------
    #
    # we look for milk chocolate in one phrase (resets every picture) 
    # but not with flavor to mean chocolate not milk
    # Phrase = "milk chocolate"
    # this works for english language and phrasing is differnet in other languages 
    #
    # this version splits the entire result and compares words
    # then i thought the 2nd method would be much faster
    #
    #if not chocoPhrase == 2:
    #    i = 0
    #    inWordArray = strFound.split()
    #    sizeOfList = len(inWordArray)
    #    while i < sizeOfList:
    #        if not inWordArray[i].find("Milk") == -1 or not inWordArray[i].find("MILK") == -1 or not inWordArray[i].find("milk") == -1:			         
    #            milkOrder = i
    #        if not inWordArray[i].find("Chocolate") == -1 or not inWordArray[i].find("CHOCOLATE") == -1 or not inWordArray[i].find("chocolate") == -1:			         
    #            chocOrder = i
    #        i += 1 
    #    if milkOrder < chocOrder:
    #        chocoPhrase = 2                                             # latch that we say the phrase "milk" then "chocolate"
    #
    # alternate : should be faster
    # we dont bother splitting them (use logical AND to see least value)
    #
    if not chocoPhrase == 2:    
        milkPosn = strFound.find("Milk") & strFound.find("MILK") & strFound.find("milk")
        chocPosn = strFound.find("Chocolate") & strFound.find("CHOCOLATE") & strFound.find("chocolate")
        # print("===== milk %s =====choc %s ========" % (milkPosn , chocPosn))
        if (not milkPosn == -1 and not chocPosn == -1) and (milkPosn < chocPosn):
            chocoPhrase = 2
    
    # if we see flavor the phrase (for milk chocolate) is invalid "milk chocolate flavor" "whole milk flavour : chocolate" is then back to milk rather than bar of chocolate
    if not strFound.find("Flavor") == -1 or not strFound.find("FLAVOR") == -1 or not strFound.find("flavour") == -1 or not strFound.find("flavor") == -1 or not strFound.find("Flavour") == -1 or not strFound.find("FLAVOUR") == -1:
        noFlavor = 1
                    
    # found the string and the product on the label
    #
    if not stringFound == -1 and not productFound == -1:
        x = 12 
		
    #        
    # now repeat for the iamge NOT inverted
    #
    # --------------- for linux ----------------------------------------
    #
    if not syst.find("Lin") == -1:
        if (len(sys.argv)-1) == 2 and not sys.argv[2].find("ocrad") == -1:  # argument is country code or ocrad
            im_rgb = cv2.cvtColor(gbresult, cv2.COLOR_BGR2RGB)
            mb = cv2.imwrite('/mnt/c/linuxmirror/pic_rot_left.pnm', im_rgb)
        else:
            mb = cv2.imwrite('/mnt/c/linuxmirror/pic_rot_left.jpg', gbresult) 
        		
        if (len(sys.argv)-1) == 1:
            f = os.popen('/home/mark/pics/read_label_ocr.sh pic_rot_left.jpg')
        elif (len(sys.argv)-1) == 2:
            cmd = '/home/mark/pics/read_label_ocr.sh pic_rot_left ' + sys.argv[2] 
            f = os.popen(cmd)
        strFound = f.read()
    #
    # --------------------- for windows --------------------------------
    #
    elif not syst.find("Win") == -1:
        im_rgb = cv2.cvtColor(~gbresult, cv2.COLOR_BGR2RGB)
    #  if you use a custom config strFound = pytesseract.image_to_string(im_rgb, config=config)
        if (len(sys.argv)-1) == 2:
            if not sys.argv[2].find("fr") == -1: 
                strFound = pytesseract.image_to_string(im_rgb, lang='eng+fra')
            elif not sys.argv[2].find("de") == -1: 
                strFound = pytesseract.image_to_string(im_rgb, lang='eng+deu')   
            elif not sys.argv[2].find("it") == -1: 
                strFound = pytesseract.image_to_string(im_rgb, lang='eng+ita') 
            elif not sys.argv[2].find("jp") == -1: 
                strFound = pytesseract.image_to_string(im_rgb, lang='eng+jpn') 
            elif not sys.argv[2].find("ru") == -1: 
                strFound = pytesseract.image_to_string(im_rgb, lang='eng+rus') 
            elif not sys.argv[2].find("sp") == -1: 
                strFound = pytesseract.image_to_string(im_rgb, lang='eng+spa')
            else:
                strFound = pytesseract.image_to_string(im_rgb)

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
    # cream must be exact matched to remove creamery being a match
    pattern = re.compile(r"\bcream\b")
     
    if not strFound.find("BUTTER") == -1 or not strFound.find("Butter") == -1  or not strFound.find("butter") == -1:
	    productWrong = ButterValue
    elif not strFound.find("SOAP") == -1 or not strFound.find("Soap") == -1 or not strFound.find("soap") == -1:
	    productWrong = SoapValue
    elif not strFound.find("SHAMPOO") == -1 or not strFound.find("Shampoo") == -1 or not strFound.find("shampoo") == -1:
	    productWrong = ShampooValue
    elif not strFound.find("CHEESE") == -1 or not strFound.find("Cheese") == -1 or not strFound.find("cheese") == -1:
	    productWrong = CheeseValue
    elif not strFound.find("RAVAGGIOLO") == -1 or not strFound.find("Ravaggiolo") == -1 or not strFound.find("ravaggiolo") == -1:
        productWrong = Ravaggiolo
    elif not strFound.find("BALSAM") == -1 or not strFound.find("Balsam") == -1 or not strFound.find("balsam") == -1:
        productWrong = Balsam
    elif not strFound.find("GRAPPA") == -1 or not strFound.find("Grappa") == -1 or not strFound.find("grappa") == -1 or not strFound.find("GRAPPE") == -1 or not strFound.find("Grappe") == -1 or not strFound.find("grappe") == -1:
        productWrong = Grappa
    elif re.search(pattern, strFound.lower()) or not strFound.find("flower") == -1 or not strFound.find("Flower") == -1 or not strFound.find("FLOWER") == -1:
        productWrong = CreamValue  
    elif not strFound.find("YOGURT") == -1 or not strFound.find("Yogurt") == -1 or not strFound.find("yogurt") == -1 or not strFound.find("yoghurt") == -1 or not strFound.find("Yoghurt") == -1 or not strFound.find("YOGHURT") == -1:
        productWrong = Yogurt
        # ----- look to see if this is true a product description ------
        #
        # if we found Yogurt we possibly eliminate it being the product
        # as some email is farmer@yogurtcremery.com
        # or web address might be www.yogurtfarms.com
        # it may still be milk so set the remove status to yogurt and
        # decide on the combination of keywords read from the label at 
        # the end of the sequence
        #  
        i = 0                                          
        inWordArray = strFound.split()
        sizeOfList = len(inWordArray)
        while i < sizeOfList:
            #if (not inWordArray[i].find("Yogurt") == -1 or not inWordArray[i].find("YOGURT") == -1 or not inWordArray[i].find("yogurt") == -1) and (not inWordArray[i].find("@") == -1 and not inWordArray[i].find(".") == -1):	# found product yogurt between @ and .		         
            if (not inWordArray[i].find("Yogurt") == -1 or not inWordArray[i].find("YOGURT") == -1 or not inWordArray[i].find("yogurt") == -1) and (not inWordArray[i].find("@") == -1 or not inWordArray[i].find(".") == -1):	# found product containing @ or . with yogurt (ocr stream)	
                productRemove == Yogurt                                 # suggest removing product if no flavor found and we found keyword milk (logic is at end after all picture iterations)
            i += 1
    elif not strFound.find("SOAP") == -1 or not strFound.find("Soap") == -1 or not strFound.find("soap") == -1:
        productWrong = SoapValue
    elif not strFound.find("SHOWER") == -1 or not strFound.find("Shower") == -1 or not strFound.find("shower") == -1:
        productWrong = Shower
    elif not strFound.find("KEFIR") == -1 or not strFound.find("Kefir") == -1 or not strFound.find("kefir") == -1:
        productWrong = Kefir
    elif not strFound.find("BISCUIT") == -1 or not strFound.find("Biscuit") == -1 or not strFound.find("biscuit") == -1:
        productWrong = Biscuit 

    if not strFound.find("RemovYog") == -1:                             # if this is seen in the stream we want to remove that product as it was for example and email not the product
        productRemove = Yogurt                                          # example pic office@naturjoghurt.at (you must add other products if you have emails like mrX@cheeseprods.com and also sell milk
        
    if not strFound.find("КОЗЬЕ") == -1:
        productType = GoatValue
        		
	# not correct if flavoured, amish wood milk, goat milk, sheep milk
    if not strFound.find("Goat") == -1 or not strFound.find("goat") == -1 or not strFound.find("GOAT") == -1 or not strFound.find("KO3bE") == -1 or not strFound.find("козье") == -1:
        productType = GoatValue
    elif not strFound.find("Sheep") == -1 or not strFound.find("SHEEP") == -1 or not strFound.find("sheep") == -1 or not strFound.find("EWE") == -1 or not strFound.find("овече") == -1:
        productType = SheepValue
    elif not strFound.find("Camel") == -1 or not strFound.find("CAMEL") == -1 or not strFound.find("camel") == -1:
        productType = CamelValue
    elif not strFound.find("Donkey") == -1 or not strFound.find("DONKEY") == -1 or not strFound.find("donkey") == -1:
        productType = DonkeyValue
    elif not strFound.find("Buffalo") == -1 or not strFound.find("BUFFALO") == -1 or not strFound.find("buffalo") == -1:
        productType = BuffaloValue

    # in german the word "packen" came up as possibly "grapple" this meant in we got apple flavor when it wasnt
    # so match apple exactly maybe should be others too.. not needed in the challenge
    #
    pattern = re.compile(r"\bapple\b")
    pattern2 = re.compile(r"\bmint\b")
                        
    if re.search(pattern2, strFound.lower()):  
        productFlavor = MintValue
    elif not strFound.find("CHOCOLATE") == -1 or not strFound.find("Chocolate") == -1 or not strFound.find("chocolate") == -1:
        productFlavor = ChocValue
    elif not strFound.find("BANANA") == -1 or not strFound.find("Banana") == -1 or not strFound.find("banana") == -1:
        productFlavor = BanaValue	
    elif (not strFound.find("Wood") == -1 and not strFound.find("Amish")) or (not strFound.find("AMISH") and not strFound.find("WOOD") == -1):
        productFlavor = WoodValue	
    elif not strFound.find("Blue") == -1 or not strFound.find("BLUE") == -1 or not strFound.find("blue") == -1 or not strFound.find("Mirtili") == -1 or not strFound.find("MIRTILI") == -1 or not strFound.find("mirtili") == -1:
        productFlavor = BlueValue
    elif not strFound.find("Mocha") == -1 or not strFound.find("MOCHA") == -1 or not strFound.find("mocha") == -1 or not strFound.find("Coffee") == -1 or not strFound.find("COFFEE") == -1 or not strFound.find("coffee") == -1:
        productFlavor = MochaValue
    elif not strFound.find("Straw") == -1 or not strFound.find("STRAW") == -1 or not strFound.find("straw") == -1:
        productFlavor = StrawBryVal
    elif not strFound.find("Orange") == -1 or not strFound.find("ORANGE") == -1 or not strFound.find("orange") == -1:
        productFlavor = OrangeValue
    elif not strFound.find("Peach") == -1 or not strFound.find("PEACH") == -1 or not strFound.find("peach") == -1:
        productFlavor = PeachValue
    elif not strFound.find("Lemon") == -1 or not strFound.find("LEMON") == -1 or not strFound.find("lemon") == -1:
        productFlavor = LemonValue
    elif not strFound.find("Apricot") == -1 or not strFound.find("APRICOT") == -1 or not strFound.find("apricot") == -1:
        productFlavor = ApricotValue
    elif not strFound.find("Pear") == -1 or not strFound.find("PEAR") == -1 or not strFound.find("pear") == -1:
        productFlavor = PearValue
    elif re.search(pattern, strFound.lower()):                          # apple must be exact
        productFlavor = AppleValue
    elif not strFound.find("Raspberry") == -1 or not strFound.find("RASPBERRY") == -1 or not strFound.find("raspberry") == -1:
        productFlavor = RaspberryValue
    elif not strFound.find("Cherr") == -1 or not strFound.find("CHERR") == -1 or not strFound.find("cherr") == -1:  # cherry or cherries
        productFlavor = CherryValue
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
    if not strFound.find("Milk") == -1 or not strFound.find("MILK") == -1 or not strFound.find("Mik") == -1 or not strFound.find("milk") == -1 or not strFound.find("МОЛОКО") == -1 or not strFound.find("молоко") == -1:
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
    # ----- erosion to thin font if needed -----------------------------
    # for example on image 33
    #kernel = np.ones((5,5),np.uint8)
    #erosion = cv2.erode(rotated,kernel,iterations = 3)
    #dilated = cv2.dilate(rotated,kernel,iterations = 1)
    # ----- filter -----------------------------------------------------
    gbresult = gaussian_filter(rotated, sigma=-2)
    #gbresult = gaussian_filter(erosion, sigma=-2)
    
    # ------------------ for linux -------------------------------------
    #
    if not syst.find("Lin") == -1:
        if (len(sys.argv)-1) == 2 and not sys.argv[2].find("ocrad") == -1:  # argument is country code or ocrad
            im_rgb = cv2.cvtColor(~gbresult, cv2.COLOR_BGR2RGB)
            mb = cv2.imwrite('/mnt/c/linuxmirror/pic_rot_righti.pnm', im_rgb)
        else:
            mb = cv2.imwrite('/mnt/c/linuxmirror/pic_rot_righti.jpg', ~gbresult)  
        if (len(sys.argv)-1) == 1:
            f = os.popen('/home/mark/pics/read_label_ocr.sh pic_rot_righti.jpg')
        elif (len(sys.argv)-1) == 2:
            cmd = '/home/mark/pics/read_label_ocr.sh pic_rot_righti ' + sys.argv[2] 
            f = os.popen(cmd)
        strFound = f.read()
    #
    # --------------------- for windows --------------------------------
    #
    elif not syst.find("Win") == -1:
        im_rgb = cv2.cvtColor(~gbresult, cv2.COLOR_BGR2RGB)
    #  if you use a custom config strFound = pytesseract.image_to_string(im_rgb, config=config)
        if (len(sys.argv)-1) == 2:
            if not sys.argv[2].find("fr") == -1: 
                strFound = pytesseract.image_to_string(im_rgb, lang='eng+fra')
            elif not sys.argv[2].find("de") == -1: 
                strFound = pytesseract.image_to_string(im_rgb, lang='eng+deu')   
            elif not sys.argv[2].find("it") == -1: 
                strFound = pytesseract.image_to_string(im_rgb, lang='eng+ita') 
            elif not sys.argv[2].find("jp") == -1: 
                strFound = pytesseract.image_to_string(im_rgb, lang='eng+jpn') 
            elif not sys.argv[2].find("ru") == -1: 
                strFound = pytesseract.image_to_string(im_rgb, lang='eng+rus') 
            elif not sys.argv[2].find("sp") == -1: 
                strFound = pytesseract.image_to_string(im_rgb, lang='eng+spa')
            else:
                strFound = pytesseract.image_to_string(im_rgb)
        else:
            strFound = pytesseract.image_to_string(im_rgb)
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
    # cream must be exact matched to remove creamery being a match
    pattern = re.compile(r"\bcream\b")
     
    if not strFound.find("BUTTER") == -1 or not strFound.find("Butter") == -1  or not strFound.find("butter") == -1:
	    productWrong = ButterValue
    elif not strFound.find("SOAP") == -1 or not strFound.find("Soap") == -1 or not strFound.find("soap") == -1:
	    productWrong = SoapValue
    elif not strFound.find("SHAMPOO") == -1 or not strFound.find("Shampoo") == -1 or not strFound.find("shampoo") == -1:
	    productWrong = ShampooValue
    elif not strFound.find("CHEESE") == -1 or not strFound.find("Cheese") == -1 or not strFound.find("cheese") == -1:
	    productWrong = CheeseValue
    elif not strFound.find("RAVAGGIOLO") == -1 or not strFound.find("Ravaggiolo") == -1 or not strFound.find("ravaggiolo") == -1:
        productWrong = Ravaggiolo
    elif not strFound.find("BALSAM") == -1 or not strFound.find("Balsam") == -1 or not strFound.find("balsam") == -1:
        productWrong = Balsam
    elif not strFound.find("GRAPPA") == -1 or not strFound.find("Grappa") == -1 or not strFound.find("grappa") == -1 or not strFound.find("GRAPPE") == -1 or not strFound.find("Grappe") == -1 or not strFound.find("grappe") == -1:
        productWrong = Grappa
    elif re.search(pattern, strFound.lower()) or not strFound.find("flower") == -1 or not strFound.find("Flower") == -1 or not strFound.find("FLOWER") == -1:
        productWrong = CreamValue  
    elif not strFound.find("YOGURT") == -1 or not strFound.find("Yogurt") == -1 or not strFound.find("yogurt") == -1 or not strFound.find("yoghurt") == -1 or not strFound.find("Yoghurt") == -1 or not strFound.find("YOGHURT") == -1:
        productWrong = Yogurt
        # ----- look to see if this is true a product description ------
        #
        # if we found Yogurt we possibly eliminate it being the product
        # as some email is farmer@yogurtcremery.com
        # or web address might be www.yogurtfarms.com
        # it may still be milk so set the remove status to yogurt and
        # decide on the combination of keywords read from the label at 
        # the end of the sequence
        #  
        i = 0                                          
        inWordArray = strFound.split()
        sizeOfList = len(inWordArray)
        while i < sizeOfList:
            #if (not inWordArray[i].find("Yogurt") == -1 or not inWordArray[i].find("YOGURT") == -1 or not inWordArray[i].find("yogurt") == -1) and (not inWordArray[i].find("@") == -1 and not inWordArray[i].find(".") == -1):	# found product yogurt between @ and .		         
            if (not inWordArray[i].find("Yogurt") == -1 or not inWordArray[i].find("YOGURT") == -1 or not inWordArray[i].find("yogurt") == -1) and (not inWordArray[i].find("@") == -1 or not inWordArray[i].find(".") == -1):	# found product containing @ or . with yogurt (ocr stream)	
                productRemove == Yogurt                                 # suggest removing product if no flavor found and we found keyword milk (logic is at end after all picture iterations)
            i += 1
    elif not strFound.find("SOAP") == -1 or not strFound.find("Soap") == -1 or not strFound.find("soap") == -1:
        productWrong = SoapValue
    elif not strFound.find("SHOWER") == -1 or not strFound.find("Shower") == -1 or not strFound.find("shower") == -1:
        productWrong = Shower
    elif not strFound.find("KEFIR") == -1 or not strFound.find("Kefir") == -1 or not strFound.find("kefir") == -1:
        productWrong = Kefir
    elif not strFound.find("BISCUIT") == -1 or not strFound.find("Biscuit") == -1 or not strFound.find("biscuit") == -1:
        productWrong = Biscuit  

    if not strFound.find("RemovYog") == -1:                             # if this is seen in the stream we want to remove that product as it was for example and email not the product
        productRemove = Yogurt                                          # example pic office@naturjoghurt.at (you must add other products if you have emails like mrX@cheeseprods.com and also sell milk
        
    if not strFound.find("КОЗЬЕ") == -1:
        productType = GoatValue
        		
	# not correct if flavoured, amish wood milk, goat milk, sheep milk
    if not strFound.find("Goat") == -1 or not strFound.find("goat") == -1 or not strFound.find("GOAT") == -1 or not strFound.find("KO3bE") == -1 or not strFound.find("козье") == -1:
        productType = GoatValue
    elif not strFound.find("Sheep") == -1 or not strFound.find("SHEEP") == -1 or not strFound.find("sheep") == -1 or not strFound.find("EWE") == -1 or not strFound.find("овече") == -1:
        productType = SheepValue
    elif not strFound.find("Camel") == -1 or not strFound.find("CAMEL") == -1 or not strFound.find("camel") == -1:
        productType = CamelValue
    elif not strFound.find("Donkey") == -1 or not strFound.find("DONKEY") == -1 or not strFound.find("donkey") == -1:
        productType = DonkeyValue
    elif not strFound.find("Buffalo") == -1 or not strFound.find("BUFFALO") == -1 or not strFound.find("buffalo") == -1:
        productType = BuffaloValue

    # in german the word "packen" came up as possibly "grapple" this meant in we got apple flavor when it wasnt
    # so match apple exactly maybe should be others too.. not needed in the challenge
    #
    pattern = re.compile(r"\bapple\b")
    pattern2 = re.compile(r"\bmint\b")
                        
    if re.search(pattern2, strFound.lower()):  
        productFlavor = MintValue
    elif not strFound.find("CHOCOLATE") == -1 or not strFound.find("Chocolate") == -1 or not strFound.find("chocolate") == -1:
        productFlavor = ChocValue
    elif not strFound.find("BANANA") == -1 or not strFound.find("Banana") == -1 or not strFound.find("banana") == -1:
        productFlavor = BanaValue	
    elif (not strFound.find("Wood") == -1 and not strFound.find("Amish")) or (not strFound.find("AMISH") and not strFound.find("WOOD") == -1):
        productFlavor = WoodValue	
    elif not strFound.find("Blue") == -1 or not strFound.find("BLUE") == -1 or not strFound.find("blue") == -1 or not strFound.find("Mirtili") == -1 or not strFound.find("MIRTILI") == -1 or not strFound.find("mirtili") == -1:
        productFlavor = BlueValue
    elif not strFound.find("Mocha") == -1 or not strFound.find("MOCHA") == -1 or not strFound.find("mocha") == -1 or not strFound.find("Coffee") == -1 or not strFound.find("COFFEE") == -1 or not strFound.find("coffee") == -1:
        productFlavor = MochaValue
    elif not strFound.find("Straw") == -1 or not strFound.find("STRAW") == -1 or not strFound.find("straw") == -1:
        productFlavor = StrawBryVal
    elif not strFound.find("Orange") == -1 or not strFound.find("ORANGE") == -1 or not strFound.find("orange") == -1:
        productFlavor = OrangeValue
    elif not strFound.find("Peach") == -1 or not strFound.find("PEACH") == -1 or not strFound.find("peach") == -1:
        productFlavor = PeachValue
    elif not strFound.find("Lemon") == -1 or not strFound.find("LEMON") == -1 or not strFound.find("lemon") == -1:
        productFlavor = LemonValue
    elif not strFound.find("Apricot") == -1 or not strFound.find("APRICOT") == -1 or not strFound.find("apricot") == -1:
        productFlavor = ApricotValue
    elif not strFound.find("Pear") == -1 or not strFound.find("PEAR") == -1 or not strFound.find("pear") == -1:
        productFlavor = PearValue
    elif re.search(pattern, strFound.lower()):                          # apple must be exact
        productFlavor = AppleValue
    elif not strFound.find("Raspberry") == -1 or not strFound.find("RASPBERRY") == -1 or not strFound.find("raspberry") == -1:
        productFlavor = RaspberryValue
    elif not strFound.find("Cherr") == -1 or not strFound.find("CHERR") == -1 or not strFound.find("cherr") == -1:  # cherry or cherries
        productFlavor = CherryValue
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
    if not strFound.find("Milk") == -1 or not strFound.find("MILK") == -1 or not strFound.find("Mik") == -1 or not strFound.find("milk") == -1 or not strFound.find("МОЛОКО") == -1 or not strFound.find("молоко") == -1:
       generalFound = 0
    #
    # found the string and the product on the label
    #
    if not stringFound == -1 and not productFound == -1:
        x = 12 

    # ------------------- for linux ------------------------------------
    #
    if not syst.find("Lin") == -1:
        if (len(sys.argv)-1) == 2 and not sys.argv[2].find("ocrad") == -1:  # argument is country code or ocrad
            im_rgb = cv2.cvtColor(gbresult, cv2.COLOR_BGR2RGB)
            mb = cv2.imwrite('/mnt/c/linuxmirror/pic_rot_right.pnm', im_rgb)
        else:
            mb = cv2.imwrite('/mnt/c/linuxmirror/pic_rot_right.jpg', gbresult)  
        
        if (len(sys.argv)-1) == 1:
            f = os.popen('/home/mark/pics/read_label_ocr.sh pic_rot_right.jpg')
        elif (len(sys.argv)-1) == 2:
            cmd = '/home/mark/pics/read_label_ocr.sh pic_rot_right ' + sys.argv[2] 
            f = os.popen(cmd)
        strFound = f.read()
    #
    # --------------------- for windows --------------------------------
    #
    elif not syst.find("Win") == -1:
        im_rgb = cv2.cvtColor(~gbresult, cv2.COLOR_BGR2RGB)
    #  if you use a custom config strFound = pytesseract.image_to_string(im_rgb, config=config)
        if (len(sys.argv)-1) == 2:
            if not sys.argv[2].find("fr") == -1: 
                strFound = pytesseract.image_to_string(im_rgb, lang='eng+fra')
            elif not sys.argv[2].find("de") == -1: 
                strFound = pytesseract.image_to_string(im_rgb, lang='eng+deu')   
            elif not sys.argv[2].find("it") == -1: 
                strFound = pytesseract.image_to_string(im_rgb, lang='eng+ita') 
            elif not sys.argv[2].find("jp") == -1: 
                strFound = pytesseract.image_to_string(im_rgb, lang='eng+jpn') 
            elif not sys.argv[2].find("ru") == -1: 
                strFound = pytesseract.image_to_string(im_rgb, lang='eng+rus') 
            elif not sys.argv[2].find("sp") == -1: 
                strFound = pytesseract.image_to_string(im_rgb, lang='eng+spa')
            else:
                strFound = pytesseract.image_to_string(im_rgb)
        else:
            strFound = pytesseract.image_to_string(im_rgb)
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
       
    # cream must be exact matched to prevent creamery being a match
    pattern = re.compile(r"\bcream\b")
     
    if not strFound.find("BUTTER") == -1 or not strFound.find("Butter") == -1  or not strFound.find("butter") == -1:
	    productWrong = ButterValue
    elif not strFound.find("SOAP") == -1 or not strFound.find("Soap") == -1 or not strFound.find("soap") == -1:
	    productWrong = SoapValue
    elif not strFound.find("SHAMPOO") == -1 or not strFound.find("Shampoo") == -1 or not strFound.find("shampoo") == -1:
	    productWrong = ShampooValue
    elif not strFound.find("CHEESE") == -1 or not strFound.find("Cheese") == -1 or not strFound.find("cheese") == -1:
	    productWrong = CheeseValue
    elif not strFound.find("RAVAGGIOLO") == -1 or not strFound.find("Ravaggiolo") == -1 or not strFound.find("ravaggiolo") == -1:
        productWrong = Ravaggiolo
    elif not strFound.find("BALSAM") == -1 or not strFound.find("Balsam") == -1 or not strFound.find("balsam") == -1:
        productWrong = Balsam
    elif not strFound.find("GRAPPA") == -1 or not strFound.find("Grappa") == -1 or not strFound.find("grappa") == -1 or not strFound.find("GRAPPE") == -1 or not strFound.find("Grappe") == -1 or not strFound.find("grappe") == -1:
        productWrong = Grappa
    elif re.search(pattern, strFound.lower()) or not strFound.find("flower") == -1 or not strFound.find("Flower") == -1 or not strFound.find("FLOWER") == -1:
        productWrong = CreamValue  
    elif not strFound.find("YOGURT") == -1 or not strFound.find("Yogurt") == -1 or not strFound.find("yogurt") == -1 or not strFound.find("yoghurt") == -1 or not strFound.find("Yoghurt") == -1 or not strFound.find("YOGHURT") == -1:
        productWrong = Yogurt
        # ----- look to see if this is true a product description ------
        #
        # if we found Yogurt we possibly eliminate it being the product
        # as some email is farmer@yogurtcremery.com
        # or web address might be www.yogurtfarms.com
        # it may still be milk so set the remove status to yogurt and
        # decide on the combination of keywords read from the label at 
        # the end of the sequence
        #  
        i = 0                                          
        inWordArray = strFound.split()
        sizeOfList = len(inWordArray)
        while i < sizeOfList:
            #if (not inWordArray[i].find("Yogurt") == -1 or not inWordArray[i].find("YOGURT") == -1 or not inWordArray[i].find("yogurt") == -1) and (not inWordArray[i].find("@") == -1 and not inWordArray[i].find(".") == -1):	# found product yogurt between @ and .		         
            if (not inWordArray[i].find("Yogurt") == -1 or not inWordArray[i].find("YOGURT") == -1 or not inWordArray[i].find("yogurt") == -1) and (not inWordArray[i].find("@") == -1 or not inWordArray[i].find(".") == -1):	# found product containing @ or . with yogurt (ocr stream)	
                productRemove == Yogurt                                 # suggest removing product if no flavor found and we found keyword milk (logic is at end after all picture iterations)
            i += 1
    elif not strFound.find("SOAP") == -1 or not strFound.find("Soap") == -1 or not strFound.find("soap") == -1:
        productWrong = SoapValue
    elif not strFound.find("SHOWER") == -1 or not strFound.find("Shower") == -1 or not strFound.find("shower") == -1:
        productWrong = Shower
    elif not strFound.find("KEFIR") == -1 or not strFound.find("Kefir") == -1 or not strFound.find("kefir") == -1:
        productWrong = Kefir
    elif not strFound.find("BISCUIT") == -1 or not strFound.find("Biscuit") == -1 or not strFound.find("biscuit") == -1:
        productWrong = Biscuit  

    if not strFound.find("RemovYog") == -1:                             # if this is seen in the stream we want to remove that product as it was for example and email not the product
        productRemove = Yogurt                                          # example pic office@naturjoghurt.at (you must add other products if you have emails like mrX@cheeseprods.com and also sell milk
        
    if not strFound.find("КОЗЬЕ") == -1:                                # hack dont know why ?
        productType = GoatValue
        		        
	# not correct if flavoured, amish wood milk, goat milk, sheep milk
    if not strFound.find("Goat") == -1 or not strFound.find("goat") == -1 or not strFound.find("GOAT") == -1 or not strFound.find("KO3bE") == -1 or not strFound.find("козье") == -1:
        productType = GoatValue
    elif not strFound.find("Sheep") == -1 or not strFound.find("SHEEP") == -1 or not strFound.find("sheep") == -1 or not strFound.find("EWE") == -1 or not strFound.find("овече") == -1:
        productType = SheepValue
    elif not strFound.find("Camel") == -1 or not strFound.find("CAMEL") == -1 or not strFound.find("camel") == -1:
        productType = CamelValue
    elif not strFound.find("Donkey") == -1 or not strFound.find("DONKEY") == -1 or not strFound.find("donkey") == -1:
        productType = DonkeyValue
    elif not strFound.find("Buffalo") == -1 or not strFound.find("BUFFALO") == -1 or not strFound.find("buffalo") == -1:
        productType = BuffaloValue

    # in german the word "packen" came up as possibly "grapple" this meant in we got apple flavor when it wasnt
    # so match apple exactly maybe should be others too.. not needed in the challenge
    #
    pattern = re.compile(r"\bapple\b")
    pattern2 = re.compile(r"\bmint\b")
                        
    if re.search(pattern2, strFound.lower()):  
        productFlavor = MintValue
    elif not strFound.find("CHOCOLATE") == -1 or not strFound.find("Chocolate") == -1 or not strFound.find("chocolate") == -1:
        productFlavor = ChocValue
    elif not strFound.find("BANANA") == -1 or not strFound.find("Banana") == -1 or not strFound.find("banana") == -1:
       productFlavor = BanaValue	
    elif (not strFound.find("Wood") == -1 and not strFound.find("Amish")) or (not strFound.find("AMISH") and not strFound.find("WOOD") == -1):
        productFlavor = WoodValue	
    elif not strFound.find("Blue") == -1 or not strFound.find("BLUE") == -1 or not strFound.find("blue") == -1 or not strFound.find("Mirtili") == -1 or not strFound.find("MIRTILI") == -1 or not strFound.find("mirtili") == -1:
        productFlavor = BlueValue
    elif not strFound.find("Mocha") == -1 or not strFound.find("MOCHA") == -1 or not strFound.find("mocha") == -1 or not strFound.find("Coffee") == -1 or not strFound.find("COFFEE") == -1 or not strFound.find("coffee") == -1:
        productFlavor = MochaValue
    elif not strFound.find("Straw") == -1 or not strFound.find("STRAW") == -1 or not strFound.find("straw") == -1:
        productFlavor = StrawBryVal
    elif not strFound.find("Orange") == -1 or not strFound.find("ORANGE") == -1 or not strFound.find("orange") == -1:
        productFlavor = OrangeValue
    elif not strFound.find("Peach") == -1 or not strFound.find("PEACH") == -1 or not strFound.find("peach") == -1:
        productFlavor = PeachValue
    elif not strFound.find("Lemon") == -1 or not strFound.find("LEMON") == -1 or not strFound.find("lemon") == -1:
        productFlavor = LemonValue
    elif not strFound.find("Apricot") == -1 or not strFound.find("APRICOT") == -1 or not strFound.find("apricot") == -1:
        productFlavor = ApricotValue
    elif not strFound.find("Pear") == -1 or not strFound.find("PEAR") == -1 or not strFound.find("pear") == -1:
        productFlavor = PearValue
    elif re.search(pattern, strFound.lower()):                          # apple must be exact
        productFlavor = AppleValue
    elif not strFound.find("Raspberry") == -1 or not strFound.find("RASPBERRY") == -1 or not strFound.find("raspberry") == -1:
        productFlavor = RaspberryValue
    elif not strFound.find("Cherr") == -1 or not strFound.find("CHERR") == -1 or not strFound.find("cherr") == -1:  # cherry or cherries
        productFlavor = CherryValue
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
    if not strFound.find("Milk") == -1 or not strFound.find("MILK") == -1 or not strFound.find("Mik") == -1 or not strFound.find("milk") == -1 or not strFound.find("МОЛОКО") == -1 or not strFound.find("молоко") == -1:
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
# useful debug

if productRemove == Yogurt and generalFound == 0:                       # we say @ or . in the string containing yoghurt eliminate the product if we also had milk
    if productFlavor == -1:                                             # if it had a flavor it is defined as remaining as yoghurt otherwise nullify the product
        productWrong = noProduct
    	
print("==== product type %s =====" % productType)
print("==== product flavor %s =====" % productFlavor)
print("==== product wrong %s =====" % productWrong)

if chocoPhrase == 2 and noFlavor == 0:                                  # we saw milk chocolate and not any mention of flavor
    print("==== bar of %s milk chocolate ===== " % productType)
    retVal = wrongStart + ChocoBar + NumOfFlavors + productType         # if it was a bar of chocolate set to wrong product and specify type e.g sheeps milk chocolate (posn after yogurt)
    print(retVal)	
elif not productWrong == -1:                                            # a wrong product word had been detected which eliminates the product
    if productWrong == Yogurt:
        if not productFlavor == -1:
	        retVal = wrongStart + productWrong + productFlavor          # because yoghurt also has a flavor so list them
        else:
            retVal = wrongStart + productWrong                          # yoghurt without a flavour
    else:
        retVal = wrongStart + productWrong                              # wrong product was found i.e butter (even if it says organic whole milk farm)
    print(retVal)
elif productFlavor == -1:                                               # no product variance occurred
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
        if not productType == -1:                                       # we had a source variance e.g. goat, sheep, donkey so bias by that to show this in the result
            milkType = productType + 11                                 
        else:
            milkType = 11                                               # product description just milk
        print(milkType)   
    else:
        milkType = 10 + NumOfVariants 
        print(milkType)                                                 # no match ( if we get no output from the ocr we need to enter a re-sizing method to get sensible ocr reader working)
else:
    if not generalFound == -1:                                          # it was a milk
        if not productType == -1:                                       # from another source than a cow offset the start by the source type
            retVal = ((productType * 10) + 10) + variaMilkStart + productFlavor				
        else:
            retVal = variaMilkStart + productFlavor                     # return another product code (the flavor or variant of the product i.e. mint goat camel)
        print(retVal)
    else:
	    retVal = variationStart + productFlavor                         # saw a keyword without milk (e.g. cheese chocolate goat)
	    print(retVal)
