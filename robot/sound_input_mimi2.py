#!/usr/bin/python3
#
# This shows how to convert speach to text using mimi API and vice versa
# it can also translate two texts using the available languages
#
# version using curl 
#
# 
import urllib.request, ssl
import urllib.parse
import requests
import json
import codecs
import sys
import os
# python2 from urllib import urlencode
from urllib.parse import urlencode
# from codecs_to_hex import to_hex
# conda install arrow (for utc time)
import arrow
# pydub for audio conversion
# pip install pydub
from pydub import AudioSegment as am
# if you need to chunk the audio
from pydub.utils import make_chunks

import re

#import pycurl

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
    STOP_TIME=0                                                         # initialise the stop time variable incase it never reads
         
    # you can get this data from you're account 
    # go to https://console.mimi.fd.ai/ to set it up
    #
    # change this key to these details to that of you're account
    # mimi and mimi-nist services are free account
    #
    APPLIC_ID='7fce6419408c4c9186e95c3a19e77368'                        # application id test-app 
    CLIENT_ID='5f68968174704e549ec926e1c2f8dbf1'                        # client id
    # secret key
    SECRET_KEY='de9c93a3f468dadb58722e70c5ab071f33d55a6d25466c19e1cf28d106afaa1250d33343355f369cfcb54f9c61087af17beef5cdf256c989a88f17f2fc52d858862b331a0ffeb8bd0074e952e5c4df1df8bb359ac8ec9c7bb7272a6e256d00ed19fce35e8c35a9576515e485287de34499cd36565cfe5d1c18139f69c7b0b4125c8eaac2834283ac2752580d892f237aaa464ac1c4b55dbd31b4134d488a53ac19d0dda3ed2a4fca9b82fe05a19a6bda0c3324f4063fccd4268f063020dca2147a29059b56f056c526759af410177913c904fe4232dd88ad7c6b3b6dc640dc268edeb10bfa722e62e465ca16b61152184c322d0d3e562d6e1c86e612ef00a681'                                            
	
    if (len(sys.argv) - 1) <= 0:
        print("<program> --sound2txt <wavfile> <engine> or --txt2sound <text> or --txt2txt <txt> langfrom langto")
        sys.exit()

    LANG_STR='ja'
    if (len(sys.argv) - 1) >= 2:
        if not sys.argv[1].find("--sound2txt") == -1:   
            fileNam = "/mnt/c/linuxmirror/" + sys.argv[2]               # ------- read in the requested iamge ---------
            fileNameGiven = sys.argv[2]
            if os.path.isfile(fileNam) == False:
                fileNam = fileNam + ".wav"
                fileNameGiven = sys.argv[2] + ".wav"
            if os.path.isfile(fileNam) == False:
                print("invalid file name or path %s" % fileNam)	
                sys.exit(1)
            #
            # decide on the process we are using to translate sound to text
            #
            if (len(sys.argv) - 1) == 3:
                if not sys.argv[3].find("nictasr") == -1:
                    MIMI_PROCESS='nict-asr'                             # using mimi,ASR powered by NICT 
                elif not sys.argv[3].find("googleasr") == -1:
                    MIMI_PROCESS='google-asr'                           # using mimi,ASR powered by google 
                else:
                    MIMI_PROCESS='asr'                                  # using mimi,to asr
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
    else:
        if (len(sys.argv) - 1) == 1:
            fileNam = "/mnt/c/linuxmirror/" + sys.argv[1]               # ------- read in the requested iamge ---------
            fileNameGiven = sys.argv[1]
            if os.path.isfile(fileNam) == False:
                fileNam = fileNam + ".wav"
            if os.path.isfile(fileNam) == False:
                print("invalid file name or path %s" % fileNam)	
                sys.exit(1)
            MIMI_PROCESS='asr'                                  # using mimi,to asr

            audio = am.from_file(fileNam)                               # check how long the sound sample is
            if audio.duration_seconds >= MAX_AUDIO_TIME:                # its too long to send in one go
                reqOperation = CONVERT_CHUNK                            # request to convert sound as chunks as too long
            else:				
                reqOperation = CONVERT_SOUND                            # request to convert sound  
        else:
            print("======== no filebane given =========")
            sys.exit(2)
          
# ------ see if we have already a valid access key (within 1hr) --------
#
# was stored in a json file we made
#
    if os.path.isfile('mimi.api') == False:
        operation = GET_ACCESS_KEY
    else:
        with open("mimi.api", "r", encoding='utf-8') as f:
            jsonValues = f.read()
            data = json.loads(jsonValues)                               # returns JSON object as dictionary
            print(data)
            ACCESS_KEY = data['accessToken']
            #STOP_TIME = float(data['endTimestamp'])                    seems to be an error with this  
            #STOP_TIME = int(data['stop'])
            STOP_TIME = float(data['endTimestamp']) + float(data['expires_in'])
            f.close()
            utc_ts = arrow.utcnow().format('X')                         # use arrow to get the current timestamp 
            print("stop ---- %f current %f" % (STOP_TIME,float(utc_ts)))      
            if (STOP_TIME > float(utc_ts)):                             # if we havent reached the stop time the key hasnt expired
                code=int(data['code'])
                status=data['status']
                progress=int(data['progress'])
                if code == 200 and not status.find("success") == -1 and progress == 100 :
                    ACCESS_KEY=data['accessToken']
                    operation = reqOperation    
                    access_key_str = 'Bearer ' + str(ACCESS_KEY);       # tag bearer to the access key we are using
                else:
                    operation = GET_ACCESS_KEY
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
        print("===== getting an access key ====")
        reader = codecs.getreader("utf-8")
        try:
            #restOfurl = ' -F grant_type="https://auth.mimi.fd.ai/grant_type/client_credentials" -F client_id="{}:{}" -F client_secret= "{}" --form-string scope="https://apis.mimi.fd.ai/auth/asr/http-api-service;https://apis.mimi.fd.ai/auth/asr/websocket-api-service;https://apis.mimi.fd.ai/auth/nict-asr/http-api-service;https://apis.mimi.fd.ai/auth/nict-asr/websocket-api-service;https://apis.mimi.fd.ai/auth/nict-tts/http-api-service;https://apis.mimi.fd.ai/auth/nict-tra/http-api-service' .format(APPLIC_ID,   CLIENT_ID, SECRET_KEY)
            restOfurl = ' -F grant_type="https://auth.mimi.fd.ai/grant_type/client_credentials" -F client_id="%s:%s" -F client_secret= "%s" --form-string scope="https://apis.mimi.fd.ai/auth/asr/http-api-service;https://apis.mimi.fd.ai/auth/asr/websocket-api-service;https://apis.mimi.fd.ai/auth/nict-asr/http-api-service;https://apis.mimi.fd.ai/auth/nict-asr/websocket-api-service;https://apis.mimi.fd.ai/auth/nict-tts/http-api-service;https://apis.mimi.fd.ai/auth/nict-tra/http-api-service'   %   (APPLIC_ID,   CLIENT_ID, SECRET_KEY)
            #print(restOfurl)
            restOfurl = restOfurl.replace(' ', '%20')
            textTest="{'client_secret' : SECRET_KEY, 'client_id': APPLIC_ID}"
            testEnc = urlencode({'client_secret' : SECRET_KEY, 'client_id': APPLIC_ID})
            print("encoded %s" % testEnc+":"+str(CLIENT_ID))
            #exit()
            #response = urllib.request.urlopen('https://auth.mimi.fd.ai/v2/token -F grant_type="https://auth.mimi.fd.ai/grant_type/client_credentials" -F client_id="%s:%s" -F client_secret= "%s" --form-string scope="https://apis.mimi.fd.ai/auth/asr/http-api-service;https://apis.mimi.fd.ai/auth/asr/websocket-api-service;https://apis.mimi.fd.ai/auth/nict-asr/http-api-service;https://apis.mimi.fd.ai/auth/nict-asr/websocket-api-service;https://apis.mimi.fd.ai/auth/nict-tts/http-api-service;https://apis.mimi.fd.ai/auth/nict-tra/http-api-service"'   %   (APPLIC_ID,   CLIENT_ID, SECRET_KEY))
            #response = urllib.request.urlopen(f"https://auth.mimi.fd.ai/v2/token{restOfurl}")
            urlreq = "https://auth.mimi.fd.ai/v2/token" + restOfurl
            #response = requests.get('https://auth.mimi.fd.ai/v2/token -F grant_type="https://auth.mimi.fd.ai/grant_type/client_credentials" -F client_id="%s:%s" -F client_secret= "%s" --form-string scope="https://apis.mimi.fd.ai/auth/asr/http-api-service;https://apis.mimi.fd.ai/auth/asr/websocket-api-service;https://apis.mimi.fd.ai/auth/nict-asr/http-api-service;https://apis.mimi.fd.ai/auth/nict-asr/websocket-api-service;https://apis.mimi.fd.ai/auth/nict-tts/http-api-service;https://apis.mimi.fd.ai/auth/nict-tra/http-api-service"'   %   (APPLIC_ID,   CLIENT_ID, SECRET_KEY))
            response = requests.get(urlreq)
            print("requests")
            print(response)
            print("requests")
            #response = urllib.request.urlopen(urlreq)
        except requests.exceptions.HTTPError:
            print("request to get mimi access key via http failed")
            print("code : %d" % e.code)
            print("message %s" % e.read())
            sys.exit(0)
        cmd = '/home/mark/pics/mimi_acc_key.sh'
        f = os.popen(cmd)
        response = f.read()
        obj = json.loads(response)                              # read the json respose to the http request if you need encode
        #obj = json.load(response)                                       # read the json respose to the http request  
        
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
            ACCESS_KEY = accesstoken    
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
                    'Content-Type' : 'audio/x-pcm;bit=16;rate=16000;channels=2',
                    'x-mimi-process' : MIMI_PROCESS,
                    'Authorization' : access_key_str,
                    'x-mimi-input-language': LANG_STR  } 
        # req = urllib.request.Request(url, headers, data=audData )
        cmd = '/home/mark/pics/mimi_speak2txt.sh ' + fileNameGiven + ' ' + MIMI_PROCESS
        print(cmd)
        f = os.popen(cmd)
        response = f.read()
        print("========= response ===========")
        print(response)
        #response='{"type": "asr#nictlvcsr", "session_id": "0a2c6fa4-866f-11eb-b66b-42010a920fc6", "status": "recog-finished", "response" : [ {"result" : "number 1"}, {"result" : "number2"} ] }'
        #
        # open the url and read the response
        #    
        #try:
        #    response = urllib.request.urlopen(req,context=ctx).read()       
        #except urllib.error.HTTPError as e:
        #    print("request to translate using mimi via http failed")
        #    print("code : %d" % e.code)
        #    print("message %s" % e.read())
        #    sys.exit(0)
 
        #obj = json.load(response) 
        
        # seems to crash with japanese chars
        #obj = json.loads(response)
        

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
            req = urllib.request.Request(url, headers, data=raw_audio_chunk )   
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
                 
     
    elif operation == TEXT_TO_SOUND:                                    # ================ input text to a sound file =============================
# ------- using the access key check valid time and get speach ---------
#
# POST https://tts.mimi.fd.ai/speech_synthesis
#
#    
        #ctx = ssl.create_default_context()                                  # to ignore SSL certificate errors should not be needed
        #ctx.check_hostname = False
        #ctx.verify_mode = ssl.CERT_NONE
    
        #url = 'https://tts.mimi.fd.ai/speech_synthesis'                 # url and port on mimi to get decryption of sound to text
        #user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'             # to suggest we are a browser
        #access_key_str = 'Bearer' + str(ACCESS_KEY);                        # tag bearer to the access key we are using
        #utfwriter = codecs.getwriter("utf-8")                              # set the reader to utf-8 
        #utf8_txt = utfwriter(INPUT_TXT)
        #print(utf8_txt)
        text_mod = re.sub('x',"%",INPUT_TXT)   
        print("=========== text MOD =============")
        print(text_mod)   
        cmd = '/home/mark/pics/mimi_text2speak.sh ' + text_mod
        f = os.popen(cmd)
        response = f.read() 
        print(response)
        
        #obj = json.load(utfreader(response))
        #print(obj)        
        #
        # the https headers for the post
        #
        #headers = { 'User_Agent' : user_agent,                               
        #            'Authorization' : access_key_str }
        #query = { 'text' : utf8_txt,
        #          'lang' : LANG_STR,
        #          'engine' : 'nict'   } 
        #req = urllib.request.Request(url, query, headers)
        #cmd = '/home/mark/pics/mimi_txt2speak.sh ' + fileNameGiven
        #f = os.popen(cmd)
        #response = f.read()
        #
        # open the url and read the response in blocks of 100000
        # save them as response.raw audio file (speech)
        #    
        #try:
        #    response = urllib.request.urlopen(req,context=ctx)  
        #    with open('/mnt/c/linuxmirror/response.raw', 'wb') as fhand:
        #        size = 0
        #        while True:
        #            info = response.read(100000)
        #            if len(info) < 1: break
        #            size = size + len(info)
        #            fhand.write(info)
        #        print(size, 'characters copied.')
        #        fhand.close()   
        #except urllib.error.HTTPError as e:
        #    print("request to translate using mimi via http failed")
        #    print("code : %d" % e.code)
        #    print("message %s" % e.read())
        #    sys.exit(0)
            
    elif operation == MACHINE_TRANSLATION:                              # ================ translate the text =============================
		
# ------- using the access key check valid time and Translate ---------
#
# POST 'https://tra.mimi.fd.ai/machine_translation'
#
#    
        ctx = ssl.create_default_context()                              # to ignore SSL certificate errors should not be needed
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        utfwriter = codecs.getwriter("utf-8")                           # set the writer to utf-8        
        utf8_txt = utfwriter(INPUT_TXT)
        print("=========== UTF-8 =============")
        print(utf8_txt)
        print ("UTF-8 :%s" % INPUT_TXT.encode('utf-8').hex())
        
        #url = 'https://tra.mimi.fd.ai/machine_translation'              # url and port on mimi to get decryption of sound to text
        #user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'         # to suggest we are a browser
        text_mod = re.sub('x',"%",INPUT_TXT)   
        print("=========== text MOD =============")
        print(text_mod)
                
        #
        # the https headers for the post
        #
        #headers = { 'User_Agent' : user_agent,                               
        #            'Authorization' : access_key_str }
        #query = { 'text' : utf8_txt,
        #          'source_lang' : LANG_STR,
        #          'target_lang' : LANG_STR2   } 
        #req = urllib.request.Request(url, query, headers)
        #utfreader = codecs.getreader("utf-8")                           # set the reader to utf-8 
        #
        # open the url and read the response
        #    
        #try:
        #    response = urllib.request.urlopen(req,context=ctx).read()       
        #except urllib.error.HTTPError as e:
        #    print("request to translate using mimi via http failed")
        #    print("code : %d" % e.code)
        #    print("message %s" % e.read())
        #    sys.exit(0)
        
        cmd = '/home/mark/pics/mimi_txt2txt.sh ' + text_mod
        f = os.popen(cmd)
        response = f.read() 
        
        print(response)
        #obj = json.load(utfreader(response))
        #print(obj)
