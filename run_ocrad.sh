#!/bin/bash
# ======================================================================
# Linux script to run OCR functions for test
# it was originally inspired from this information :-
# https://github.com/baumanta/OCR_octave/blob/master/run_ocrad.sh
#
# tested with ocrad and then used tesseract
#
# ======================================================================
# use ocrad ocr engine
# install this with : sudo apt install ocrad
# results are okay with some error
# ======================================================================
# this line is outputting to the text file file.txt (only the numbers)
ocrad -a --filter=numbers_only --format=utf8 --output=file.txt $1
echo " ===== ocrad : with pnm file ============ "
# this line is outputting to the stdout in this case its piped back to 
# the python calling script which catches the std output into variable f
# format utf8 seemed to be needed to get better with different fonts
ocrad --format=utf8 $1
#ocrad $1
# ======================================================================
# using tesseract ocr engine instead (performance was better on tests)
# please refer to here 
# https://launchpad.net/~alex-p/+archive/ubuntu/tesseract-ocr-devel
#
# sudo add-apt-repository ppa:alex-p/tesseract-ocr-devel 
# sudo apt-get update
# sudo apt install tesseract-ocr 
# results are a lot better than ocrad during my tests
# if you know the dots per inch for the input file you can use --dpi
#
# if you need another language e.g. welsh command is as below (cym is cymru)
# sudo apt-get install tesseract-ocr-cym
# ======================================================================
tesseract testFile1.pnm eurotext-eng -l eng
echo " ====== tesseract : pnm file ============= "
cat eurotext-eng.txt 
tesseract /mnt/c/linuxmirror/testFile1.jpg euroraw-eng -l eng
echo " ====== tesseract : raw picture file ===== "
cat euroraw-eng.txt 
tesseract /mnt/c/linuxmirror/plate1.jpg plate1-eng -l eng
echo " ====== tesseract : number plate 1 ===== "
cat plate1-eng.txt 
tesseract /mnt/c/linuxmirror/plate2.jpg plate2-eng -l eng
echo " ====== tesseract : number plate 2 ===== "
cat plate2-eng.txt 
tesseract /mnt/c/linuxmirror/CW102.jpg milkbott-eng -l eng
echo " ====== tesseract : milk bottle 1 ===== "
cat milkbott-eng.txt 
tesseract /mnt/c/linuxmirror/CW103.jpg milkbot2-eng -l eng
echo " ====== tesseract : milk bottle 2 ===== "
cat milkbot2-eng.txt 
tesseract /mnt/c/linuxmirror/CW104.jpeg butter-eng -l eng
echo " ====== tesseract : butter label ===== "
cat butter-eng.txt 
tesseract /mnt/c/linuxmirror/CW104.tif butter1-eng -l eng
echo " ====== tesseract : butter label 1 inverted tiff ===== "
cat butter1-eng.txt 
tesseract /mnt/c/linuxmirror/CW105.jpeg butter2-eng -l eng
echo " ====== tesseract : butter label 2 ===== "
cat butter2-eng.txt 
tesseract /mnt/c/linuxmirror/CW106.jpg butter3-eng -l eng
echo " ====== tesseract : butter label 2 inverted ===== "
cat butter3-eng.txt 
tesseract /mnt/c/linuxmirror/CW107.tif butter4-eng -l eng
echo " ====== tesseract : butter label 2 inverted tiff ===== "
cat butter4-eng.txt 
tesseract /mnt/c/linuxmirror/CW108.jpg butter5-eng -l eng
echo " ====== tesseract : butter label 2 ===== "
cat butter5-eng.txt 
tesseract /mnt/c/linuxmirror/CW109.jpg butter6-eng -l eng
echo " ====== tesseract : butter label 3 ===== "
cat butter6-eng.txt 
tesseract /mnt/c/linuxmirror/CW110jpg butter7-eng -l eng
echo " ====== tesseract : butter label 3 invert rotate ===== "
cat butter7-eng.txt 
tesseract /mnt/c/linuxmirror/CW111.jpg butter8-eng -l eng
echo " ====== tesseract : butter label 3 rotate ===== "
cat butter8-eng.txt 
tesseract /mnt/c/linuxmirror/CW112.jpg clot-eng -l eng
echo " ====== tesseract : clotted cream ===== "
cat clot-eng.txt 
tesseract /mnt/c/linuxmirror/CW113.jpg curd-eng -l eng
echo " ====== tesseract : goat curd ===== "
cat curd-eng.txt 
tesseract /mnt/c/linuxmirror/CW114.jpg curd2-eng -l eng
echo " ====== tesseract : goat curd invert rotate ===== "
cat curd2-eng.txt
tesseract /mnt/c/linuxmirror/CW115.jpg curd3-eng -l eng
echo " ====== tesseract : goat curd rotate ===== "
cat curd3-eng.txt 
tesseract /mnt/c/linuxmirror/plate5.jpg plat3-eng -l eng
echo " ====== tesseract : number plate 3 after re-sizing fonts ===== "
cat plat3-eng.txt 
tesseract /mnt/c/linuxmirror/CW117.jpg wine-eng -l eng
echo " ====== tesseract : wine bottle ===== "
cat wine-eng.txt 
tesseract /mnt/c/linuxmirror/barcode.gif barcode-eng -l eng
echo " ====== tesseract : dpd barcode ===== "
cat barcode-eng.txt
tesseract /mnt/c/linuxmirror/nlpost2.gif nlpost-eng -l eng
echo " ====== tesseract : tnt post NL barcode (needed to be enlarged) hard to get due to font ===== "
cat nlpost-eng.txt  
tesseract /mnt/c/linuxmirror/royalmail2.gif royalm-eng -l eng
echo " ====== tesseract : royal mail (needs enlarging same problems) ===== "
cat royalm-eng.txt  
tesseract /mnt/c/linuxmirror/auspost3.gif ausm-eng -l eng
tesseract /mnt/c/linuxmirror/auspost2.jpg ausm1-eng -l eng
echo " ====== tesseract : aus post (rescaled 1st 6 is too hard to get ?) ===== "
cat ausm-eng.txt 
cat ausm1-eng.txt 
# you can translate pdf by conversion
# use sudo apt install poppler-utils to install pdftoppm
pdftoppm -png /mnt/c/linuxmirror/testpdf.pdf /mnt/c/linuxmirror/testpdf 
tesseract /mnt/c/linuxmirror/testpdf-1.png pdf-eng -l eng
echo " ====== tesseract : pdf doc white on black ===== "
cat pdf-eng.txt 
#
# if you need to say the text for the visually impaired
# then install this....
# sudo apt install espeak
# and use it like to say the last file outloud
# espeak -f pdf-eng.txt
#
