#!/usr/bin/python3
#
# This shows how to convert speach to text using mimi API and vice versa
# it can also translate two texts using the available languages
#
# 
import urllib.request, ssl
import urllib.parse
import json
import codecs
import sys
import os
# conda install arrow (for utc time)
import arrow
# pydub for audio conversion
from pydub import AudioSegment as am
# if you need to chunk the audio
from pydub.utils import make_chunks

if __name__ == '__main__':

    #
    # enumerate the mimi state engine
    #
    GET_ACCESS_KEY=1                                                    # get access key
    CONVERT_SOUND=2                                                     # convert sound to text
    CONVERT_CHUNK=3                                                     # convert sound chunks to text (long sound)
    TEXT_TO_SOUND=4                                                     # convert text to sound
    SPEAKER_DISCOVER=5                                                  # discover the speaker
    MACHINE_TRANSLATION=6                                               # machine translation

    MAX_AUDIO_TIME=10                                                   # maximum length in seconds for audio before chunking
     
    # you can get this data from you're account 
    # go to https://console.mimi.fd.ai/ to set it up
    #
    # change this key to that of you're account
    #
    APPLIC_ID='423c7f871b1263a5eaf3d3660226649fd53db'                   # application id
    CLIENT_ID='1247532a53db981'                                         # client id
    SECRET_KEY='21064734592'                                            # secret key
	
    if (len(sys.argv) - 1) <= 0:
        print("<program> --sound2txt <wavfile> <engine> or --txt2sound <text> or --txt2txt <txt> langfrom langto")
        sys.exit()

    if (len(sys.argv) - 1) >= 2:
        if not sys.argv[1].find("--sound2txt") == -1:   
            # ------- read in the requested iamge ---------
            fileNam = "/mnt/c/linuxmirror/" + sys.argv[2]
            if os.path.isfile(fileNam) == False:
	            fileNam = fileNam + ".wav"
            if os.path.isfile(fileNam) == False:
                print("invalid file name or path %s" % fileNam)	
                sys.exit()
            #
            # decide on the process we are using to translate sound to text
            #
            if not sys.argv[3].find("nictasr") == -1:
                MIMI_PROCESS='nict-asr'                                 # using mimi,ASR powered by NICT 
            elif not sys.argv[3].find("googleasr") == -1:
                MIMI_PROCESS='google-asr'                               # using mimi,ASR powered by google 
            else:
                MIMI_PROCESS='asr'                                      # using mimi,to asr 
            audio = am.from_file(fileNam)                               # check how long the sound sample is
            if audio.duration_seconds >= MAX_AUDIO_TIME:                # its too long to send in one go
                reqOperation = CONVERT_CHUNK                            # request to convert sound as chunks as too long
            else:				
                reqOperation = CONVERT_SOUND                            # request to convert sound
        elif not sys.argv[1].find("--txt2txt") == -1:          
            INPUT_TXT=sys.argv[2]                                       # ------- set the text input string ---------
            #
            # choose the spoken language
            # ja, en, es, fr, id, ko, my, th, vi, zh, zh-TW
            #
            if (len(sys.argv) - 1) == 4:
                LANG_STR=sys.argv[3]
                LANG_STR2=sys.argv[4]
            else:    
                LANG_STR='en'
                LANG_STR2='ja'  
            reqOperation = MACHINE_TRANSLATION                          # request to convert text from one lang to another                      
        else:     
            INPUT_TXT=sys.argv[2]                                       # ------- set the text input string ---------
            if (len(sys.argv) - 1) == 3:
                LANG_STR=sys.argv[3]
            else:    
                LANG_STR='en'        
            reqOperation = TEXT_TO_SOUND                                # request to convert text from one lang to another 
            
# ------ see if we have already a valid access key (within 1hr) --------
#
# was stored in a json file we made
#
    if os.path.isfile('mimi.json') == False:
        operation = GET_ACCESS_KEY
    else:
        f = open('mimi.json',)                                          # Opening JSON file 
        data = json.load(f)                                             # returns JSON object as dictionary
        ACCESS_KEY = data['accessToken']
        STOP_TIME = int(data['stop'])
        f.close()
    utc_ts = arrow.utcnow().format('X')                                 # use arrow to get the current timestamp
        
    if (STOP_TIME > int(utc_ts)):                                       # if we havent reached the stop time the key hasnt expired
        operation = reqOperation
    else:
        operation = GET_ACCESS_KEY

# ------ do the operation requested by the state machine ---------------
#
#
    if operation == GET_ACCESS_KEY: 
# ------------------- get access key ----------------------------------
#
# you can also use google 
# HTTP request
# POST https://auth.mimi.fd.ai/v2/token \ -F grant_type="https://auth.mimi.fd.ai/grant_type/client_credentials" \ -F client_id="<applicationId>:<clientId>" \ -F client_secret= "<clientSecret>" \ --form-string scope="https://apis.mimi.fd.ai/auth/asr/http-api-service;https://apis.mimi.fd.ai/auth/asr/websocket-api-service;https://apis.mimi.fd.ai/auth/nict-asr/http-api-service;https://apis.mimi.fd.ai/auth/nict-asr/websocket-api-service;https://apis.mimi.fd.ai/auth/nict-tts/http-api-service;https://apis.mimi.fd.ai/auth/nict-tra/http-api-service"
#
        reader = codecs.getreader("utf-8")
        try:
            response = urllib.request.urlopen('https://auth.mimi.fd.ai/v2/token -F grant_type="https://auth.mimi.fd.ai/grant_type/client_credentials" -F client_id="%s:%s" -F client_secret= "%s" --form-string scope="https://apis.mimi.fd.ai/auth/asr/http-api-service;https://apis.mimi.fd.ai/auth/asr/websocket-api-service;https://apis.mimi.fd.ai/auth/nict-asr/http-api-service;https://apis.mimi.fd.ai/auth/nict-asr/websocket-api-service;https://apis.mimi.fd.ai/auth/nict-tts/http-api-service;https://apis.mimi.fd.ai/auth/nict-tra/http-api-service"'   %   (APPLIC_ID,   CLIENT_ID, SECRET_KEY))
        except urllib.error.HTTPError as e:
            print("request to get mimi access key via http failed")
            print("code : %d" % e.code)
            print("message %s" % e.read())
            sys.exit(0)

        obj = json.load(reader(response))                                   # read the json respose to the http request 

        code=int(obj['code'])
        status=obj['status']
        progress=int(obj['progress'])

#
# write the token and time to a json file 
#
        if code == 200 and not status.find("success") == -1 and progress == 100 :
            accesstoken=obj['accessToken']
            startTimeValidity=obj['startTimestamp']
            stopTimeValidity=obj['endTimestamp']  
            acc_dict = { "acc_token" : accesstoken, "start" : startTimeValidity, "stop" : stopTimeValidity }
            with open("mimi_auth.json", "w") as outfile:
                json.dump(acc_dict, outfile)
                outfile.close()
            operation = reqOperation     
        else:
            print("request to get a mimi access key via http failed : error : %s" % obj['error'])
            sys.exit(0)
                     
        access_key_str = 'Bearer ' + str(ACCESS_KEY);                   # tag bearer to the access key we are using
        
    if operation == CONVERT_SOUND:                                      # ================ input sound file to a text output =============================
#
# ------ downsample and convert to raw ---------------------------------
#
        sound = am.from_file(fileNam, format='wav', frame_rate=44000)
        sound = sound.set_frame_rate(16000)
        sound.export('/mnt/c/linuxmirror/downsampled.raw', format='raw') 
        
# ------- using the access key check valid time and Translate ---------
#
# POST 'https://service.mimi.fd.ai:443'
#
#    
        ctx = ssl.create_default_context()                                  # to ignore SSL certificate errors should not be needed
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    
        url = 'https://service.mimi.fd.ai:443'                              # url and port on mimi to get decryption of sound to text
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'             # to suggest we are a browser

        with open('/mnt/c/linuxmirror/downsampled.raw', 'rb') as f:         # open the raw audio file 
            audData = f.read()
            f.close()    
        #
        # the https headers for the post
        #
        headers = { 'User_Agent' : user_agent,                               
                    'Content-Type' : audio/x-pcm;bit=16;rate=16000;channels=1,
                    'x-mimi-process' : MIMI_PROCESS,
                    'Authorization' : access_key_str,
                    'x-mimi-input-language': LANG_STR  } 
        req = urllib.request.Request(url, data=audData, headers)

        #
        # open the url and read the response
        #    
        try:
            response = urllib.request.urlopen(req,context=ctx).read()       
        except urllib.error.HTTPError as e:
            print("request to translate using mimi via http failed")
            print("code : %d" % e.code)
            print("message %s" % e.read())
            sys.exit(0)
 
        #obj = json.load(reader(response)) dont think we use utf-8
        obj = json.load(response)
        
        #
        # Iterating through the json list for what we heard
        # and reply back with the expected speech as text
        #  
        if not obj['type'].find("asr#nictlvcsr") == -1:                     # using nict
            for i in obj['result']: 
                print(i)
        elif not obj['type'].find("asr#mimilvcsr") == -1:                   # mimi asr
            for i in obj['result']: 
                print(i)
            print("====== pronunciation ======")
            for i in obj['pronunciation']: 
                print(i)        
        else:
            for i in obj['result']: 
                print(i)

    elif operation == CONVERT_CHUNK:                                    # ================ input sound file chunks to a text output chunks ============================= 
#
# ------ downsample and convert to raw then chunk it -------------------
#
        sound = am.from_file(fileNam, format='wav', frame_rate=44000)
        sound = sound.set_frame_rate(16000)
        sound.export('/mnt/c/linuxmirror/downsampled.raw', format='raw') 
        sound = am.from_file('/mnt/c/linuxmirror/downsampled.raw', format='raw', frame_rate=16000)        
        chunk_length_ms = 1000                                          # pydub calculates in millisec
        chunks = make_chunks(sound, chunk_length_ms)                    # Make chunks of one sec
        				               
        # if you need chunk
        for i, chunk in enumerate(chunks):
            raw_audio_chunk = chunk.raw_data
            req = urllib.request.Request(url, data=raw_audio_chunk, headers)   
            #
            # open the url and read the response
            #    
            try:
                response = urllib.request.urlopen(req,context=ctx).read()       
            except urllib.error.HTTPError as e:
                print("request to translate using mimi via http failed")
                print("code : %d" % e.code)
                print("message %s" % e.read())
                sys.exit(0)
 
            obj = json.load(response)
        
            #
            # Iterating through the json list for what we heard
            # and reply back with the expected speech as text
            #  
            if not obj['type'].find("asr#nictlvcsr") == -1:                     # using nict
                for i in obj['result']: 
                    print(i)
            elif not obj['type'].find("asr#mimilvcsr") == -1:                   # mimi asr
                for i in obj['result']: 
                    print(i)
                print("====== pronunciation ======")
                    for i in obj['pronunciation']: 
                        print(i)        
            else:
                for i in obj['result']: 
                    print(i)           
     
    elif operation == TEXT_TO_SOUND:                                    # ================ input text to a sound file =============================
# ------- using the access key check valid time and get speach ---------
#
# POST https://tts.mimi.fd.ai/speech_synthesis
#
#    
        ctx = ssl.create_default_context()                                  # to ignore SSL certificate errors should not be needed
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    
        url = 'https://tts.mimi.fd.ai/speech_synthesis'                 # url and port on mimi to get decryption of sound to text
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'             # to suggest we are a browser
        access_key_str = 'Bearer' + str(ACCESS_KEY);                        # tag bearer to the access key we are using
   
        #
        # the https headers for the post
        #
        headers = { 'User_Agent' : user_agent,                               
                    'Authorization' : access_key_str }
        query = { 'text' : INPUT_TXT,
                  'lang' : LANG_STR,
                  'engine' : 'nict'   } 
        req = urllib.request.Request(url, query, headers)

        #
        # open the url and read the response in blocks of 100000
        # save them as response.raw audio file (speech)
        #    
        try:
            response = urllib.request.urlopen(req,context=ctx)  
            with open('/mnt/c/linuxmirror/response.raw', 'wb') as fhand:
                size = 0
                while True:
                    info = response.read(100000)
                    if len(info) < 1: break
                    size = size + len(info)
                    fhand.write(info)
                print(size, 'characters copied.')
                fhand.close()   
        except urllib.error.HTTPError as e:
            print("request to translate using mimi via http failed")
            print("code : %d" % e.code)
            print("message %s" % e.read())
            sys.exit(0)
            
    elif operation == MACHINE_TRANSLATION:                              # ================ translate the text =============================
		
# ------- using the access key check valid time and Translate ---------
#
# POST 'https://tra.mimi.fd.ai/machine_translation'
#
#    
        ctx = ssl.create_default_context()                              # to ignore SSL certificate errors should not be needed
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        reader = codecs.getreader("utf-8")                              # set the reader to utf-8 
        url = 'https://tra.mimi.fd.ai/machine_translation'              # url and port on mimi to get decryption of sound to text
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'         # to suggest we are a browser
   
        #
        # the https headers for the post
        #
        headers = { 'User_Agent' : user_agent,                               
                    'Authorization' : access_key_str }
        query = { 'text' : reader(INPUT_TXT),
                  'source_lang' : LANG_STR,
                  'target_lang' : LANG_STR2   } 
        req = urllib.request.Request(url, query, headers)

        #
        # open the url and read the response
        #    
        try:
            response = urllib.request.urlopen(req,context=ctx).read()       
        except urllib.error.HTTPError as e:
            print("request to translate using mimi via http failed")
            print("code : %d" % e.code)
            print("message %s" % e.read())
            sys.exit(0)
 
        obj = json.load(reader(response))
        print(obj)
