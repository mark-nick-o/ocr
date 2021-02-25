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
here a robot using the machine vision may read various labels of sizes and shapes containg various milk bottles in various languages
the initial iterator.py script will rotate those labels and try to read and translate the text
to determine in ranking what it has discovered and if it matches definitions of the requested type

this has some decent success (apart from in japanese)

a 2nd take will be made to automatically re-size images and feed them back into the rotate reader when the iamge can not be read as it comes

a script will be made in an attempt to read the circle text if possible
