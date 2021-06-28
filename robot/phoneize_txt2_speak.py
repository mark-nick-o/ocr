#
# use phonemize wrapper to improve input to a speach engine
# to speak aloud the text you want to say for the visually impaired
#
# pip install phonemizer
#
# pip install phonemizer  ref :: https://pypi.org/project/phonemizer/
#
# you need to install the speach engines you want ESPEAK/MBROLA/FESTIVAL/SEGMENTS
# sudo apt-get install festival espeak-ng mbrola 
# 
# you need to install the needed languages for mbrola
#
# show those available
# sudo apt-cache search mbrola
# 
# e.g. 
# ------ French --------------------------------------------------------
# sudo apt-get install mbrola mbrola-fr1
# ------ German --------------------------------------------------------
# sudo apt-get install mbrola mbrola-de1 - female de2 (male)
# ------ English -------------------------------------------------------
# sudo apt-get install mbrola mbrola-en1 - male us1 (female) ,2,3 (festvox-en1, festvox-us1,2,3)
# ------ Spanish -------------------------------------------------------
# sudo apt-get install mbrola mbrola-es1 (2) - male
# ------- Italian ------------------------------------------------------
# sudo apt-get install mbrola mbrola-it3 - male
#
# ------- Japan --------------------------------------------------------
# japanese - segments 
#
# ------- russian / japanese / english using kaldi TO COMPLETE ---------
#
# git clone https://github.com/kaldi-asr/kaldi.git
# cd kaldi/tools/; make; cd ../src; ./configure; make
# conda install -c pykaldi pykaldi-cpu
# for russian git clone https://github.com/SergeyShk/Speech-to-Text-Russian.git
# https://github.com/SergeyShk/Speech-to-Text-Russian
# http://alphacephei.com/kaldi/kaldi-ru-0.6.tar.gz
# https://habr.com/ru/post/323570/
#
# ------ mimi text to speech -------------------------------------------
# japanese

import argparse

# ======= common =======================================================
from phonemizer import main, backend, logger
import phonemizer.separator as separator
from phonemizer.separator import Separator

class PhoneSpeaker(object):
    """Класс для распознавания речи с помощью алгоритма nnet3"""

    def __init__(self, eng, lan, pun, text):
    
        self.eng = eng
        self.lan = lan
        self.pun = pun
        self.text = text
        # ======= default the engine to festival if none specified
        try:
            if not self.eng.find("fest") == -1:
                dummy == 1
        except:
            self.eng = "fest"
        # ======= default the language to english if none specified
        try:
            if not self.lan.find("en") == -1:
                dummy == 1
        except:
            self.lan = "en"
                    
    def recognize(self, wav=None):

        if not self.eng.find("fest") == -1:
           # ======= festival english us only =====================================
            from phonemizer.backend import FestivalBackend
            out1 = FestivalBackend('en-us', preserve_punctuation=False).phonemize(self.text, strip=True)
        elif not self.eng.find("esp") == -1:
           # ======= espeak =======================================================
            from phonemizer.backend import EspeakBackend
            if not self.lan.find("en") == -1:
                backend = EspeakBackend('en-us')
            elif not self.lan.find("fr") == -1:
                backend = EspeakBackend('fr-fr')
            elif not self.lan.find("de") == -1 or not self.lan.find("ger") == -1:
                backend = EspeakBackend('de-de')
            elif not self.lan.find("ita") == -1:
                backend = EspeakBackend('it-it')
            elif not self.lan.find("esp") == -1 or not self.lan.find("spa") == -1:
                backend = EspeakBackend('es-es')
            else:
                print("Invalid Language specified")
                exit(1)
            sep = separator.Separator(word=';eword ', syllable=None, phone=' ')
            out1 = backend.phonemize(self.text, sep, False)
        elif not self.eng.find("mbr") == -1: 
            # ====== mbrola ========================================================
            from phonemizer.backend import EspeakBackend, EspeakMbrolaBackend
            if EspeakMbrolaBackend.is_available():			              
                if not self.lan.find("en") == -1:
                    EspeakMbrolaBackend('mb-en1')
                elif not self.lan.find("fr") == -1:
                    EspeakMbrolaBackend('mb-fr2')
                elif not self.lan.find("de") == -1 or not self.lan.find("ger") == -1:
                    EspeakMbrolaBackend('mb-de1')
                elif not self.lan.find("ita") == -1:
                    EspeakMbrolaBackend('mb-es1')
                elif not self.lan.find("esp") == -1 or not self.lan.find("spa") == -1:
                    EspeakMbrolaBackend('mb-it3')
                else:
                    print("Invalid Language specified")
                    exit(1)				
                sep = separator.Separator(word=';eword ', syllable=None, phone=' ')
                out1 = backend.phonemize(self.text, sep, False)
        elif not self.eng.find("seg") == -1: 
            # ===== segment ========================================================
            from phonemizer.backend import SegmentsBackend
            if not self.lan.find("ja") == -1:
                backend = SegmentsBackend('japanese')
            else:
                print("Invalid Language specified")
                exit(1)
            sep = separator.Separator(word=';eword ', syllable=None, phone=' ')					
            out1 = backend.phonemize(self.text, sep, False)	
        else:
            print("Invalid Language specified")
            exit(1)			   	
        print(out1)                                                      # return the result string to the speach engine 
       		
# ======= parse command line args ======================================

if __name__ == '__main__':
	
    parser = argparse.ArgumentParser(description='parse the command line ')
    parser.add_argument('-e', '--eng', metavar='ENG', help='Choose the text to speech engine')
    parser.add_argument('-l', '--lan', metavar='LAN', help='Choose the text to speech language')
    parser.add_argument('-p', '--pun', metavar='PUN', help='Punctuation preserve or remove')    
    parser.add_argument('-t', '--txt', metavar='TXT', help='Text to convert for the speech engine') 
    args = parser.parse_args()

    phoneSpk = PhoneSpeaker( args.eng, args.lan, args.pun, args.txt )
    phoneSpk.recognize()
               
