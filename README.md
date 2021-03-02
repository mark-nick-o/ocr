# OCR / OpenCV
==============
Tests for ocr of various graphics and demostration of manipulating photo for better use by ocr by resizing, inverting, rotating or edge detection.
used ocrad and also tesseract for picture to text ocr extraction.

Added some filters just to show how to effect pictures in various ways

You can either use ocr then use a sequence of rotate, re-size, invert effects to read it if you're result is not satisfactory thats what the examples show you

Or you can control a camera by using a gimbal and camera focus/zoom and read the resulting video input then passing it to the ocr.

Some of the effects can also be used just to change a video for artistic effect or to calculate if something has moved for example, this is found in the various features of openCV in the script funWithfixels.py

Can be used to read scanners text of shopping items on web page or machine vision can also speak that for the visually impaired 

ROBOT READER
============
a demo project was made in the subdirectory robot

this is a challenge for the robot to read correctly all the labels and categorise each choice against the wishes in its mind the request of the master

here a robot using the machine vision may read various labels of sizes and shapes containg various milk bottles in various languages
the initial iterator.py script will rotate those labels and try to read and translate the text
to determine in ranking what it has discovered and if it matches definitions of the requested type

command line usage :: python iterator.py path_to_files/pic_file_name <optional language code | ocrad>
you can choose language of picture you want to translate
Japan / Spain / France / Germany / Russia / Italy
or if you pass ocrad it will use ocrad ocr instead of default english language and tesseract ocr

this has some decent success (apart from in japanese - one now works)

by using the unwrapper for bottles some labels now read better these have been added

a 2nd take will be made to automatically re-size images and feed them back into the rotate reader when the iamge can not be read as it comes

its also possible to use Extended MNIST (EMNIST) using Neural Network (CNN) for Recognition

a script will be made in an attempt to read the circle text if possible

if you got espeak you can read them out or write them to a brialle keyboard if you're for example use this nice one 
https://github.com/AaditT/braille
