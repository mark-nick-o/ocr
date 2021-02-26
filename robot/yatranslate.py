#!/usr/bin/python3
 
import urllib.request
import urllib.parse
import json
import codecs
#
# This shows how to actiavte translation via yandex
# to translate russian to english however you have to pay
#
#
import sys

# you can set up a free key here: https://tech.yandex.com/translate/
#
# you have to pay now 
# change this key to that of you're account
#
APIKEY='trnsl.1.1.20151211T093839Z.8d3588d6cfec6343.3c4423c7f871b1263a5eaf3d3660226649fd53db'
APIKEY2='trnsl.1.1.20190308T095934Z.95ae5cf4e28588ea.9d108fb6e768af347464925e4e98b91edb0013f5'

try:
    TEXT = urllib.parse.quote(sys.argv[1])
except IndexError:
    print("No text to translate")
    sys.exit(0)
 
# ------------------- Detect language ----------------------------------
#
# you can also use google 
# HTTP request
# POST https://translation.googleapis.com/language/translate/v2/detect
#
reader = codecs.getreader("utf-8")
try:
    response = urllib.request.urlopen('https://translate.yandex.net/api/v1.5/tr.json/detect?key=%s&text="%s"'   %   (APIKEY,   TEXT))
except urllib.error.HTTPError:
    print("Detection request via http failed")
    sys.exit(0)
 
obj = json.load(reader(response))
 
LANG=obj['lang']
 
if LANG == 'ru':
    # set the language to convert russian to english
    LANG = 'en'
elif LANG == '':
    print("language not defined or invalid API key")
    sys.exit(0)
else:
    # otherwise set the language to russian
    LANG='ru'
 
# --------------- Translate --------------------------------------------
#
# POST https://translation.googleapis.com/language/translate/v2
#
try:
    response = urllib.request.urlopen('https://translate.yandex.net/api/v1.5/tr.json/translate?&format=plain&option=1&key=%s&text=%s&lang=%s'   %   (APIKEY,   TEXT,   LANG))
except urllib.error.HTTPError:
    print("translation failed")
    sys.exit(0)
 
obj = json.load(reader(response))
print("%s~%s" % (obj['lang'],obj['text'][0]))
