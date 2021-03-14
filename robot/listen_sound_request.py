#
# This python takes either a microphone or sound file as an input
# and tries to decipher the vocal message into text
#
#
import os
import sys
# python -m pip install --upgrade pip
# sudo -H pip3 install SpeechRecognition pydub
import speech_recognition as sr
# sudo apt-get install python-pyaudio python3-pyaudio
# pip3 install pyaudio
#
if __name__ == "__main__":

    if (len(sys.argv) - 1) <= 0:
        print("please pass the filename for the sound you want to convert to text or --MIC <duration> for a recording from the mircophone")
        sys.exit()
       
    r = sr.Recognizer()                                                 # initialize the recognizer

    if (len(sys.argv) - 1) == 2:                                        # passed -MIC <duration>
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=1)
            # audio_data = recognizer.listen(source, timeout=int(sys.argv[2]))
            audio_data = r.record(source, duration=int(sys.argv[2]))    # read the audio data from the default microphone for the period of the duration
        try:
            text = r.recognize_google(audio_data,language="en-US")      # recognize (convert from speech to text) - english USA 
            print("Decoded Text : {}".format(text))			
        except Exception as ex:
            print(ex)            
    else:  
        # ------- read in the requested iamge ---------
        fileNam = "/mnt/c/linuxmirror/" + sys.argv[1]
        if os.path.isfile(fileNam) == False:
            fileNam = fileNam + ".wav"
        if os.path.isfile(fileNam) == False:
            print("invalid file name or path %s" % fileNam)	
            sys.exit()      
        with sr.AudioFile(fileNam) as source:                           # open the file
            # audio_data = recognizer.listen(source)
            audio_data = r.record(source)                               # listen for the data (load audio to memory)
        try:
            text = r.recognize_google(audio_data,language="en-US")      # recognize (convert from speech to text) - english USA 
            print("Decoded Text : {}".format(text))			
        except Exception as ex:
            print(ex)     
            
    text = r.recognize_google(audio_data,language="en-US")              # recognize (convert from speech to text) - english USA            
    #text = r.recognize_google(audio_data,language="es-ES")              # recognize (convert from speech to text) - spanish
    print(text)
