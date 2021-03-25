#
# Conversion utilities for sound files for use with mimi speach to text
#
# This is the robots ears and voice
#
# we go from 44KHZ stereo to 16KHZ mono 
#
#
import sys
import os
import wave
from sound import *
import numpy as np
from pylab import *
import struct
import scipy.signal
import numpy as np
from pydub import AudioSegment as am

# make mono for left channel
def stereo2monoral(sig):
    monoral = []
    for i in range(0,len(sig), 2):
        monoral.append(sig[i])
    return np.array(monoral)

# make mono from average l and r
def stereo2monoave(sig):
    monorave = []
    for i in range(0,len(sig), 2):
        try:
            monorave.append((sig[i]+sig[i+1])/2)
        except:
            monorave.append(sig[i])			
    return np.array(monorave)

# make mono from average l and r and deepen
def stereo2monorave2(sig):
    monorave = []
    for i in range(0,len(sig), 2):
        try:
            monorave.append(np.sqrt(((sig[i]*sig[i])+(sig[i+1]*sig[i+1])))/2)
        except:
            monorave.append(sig[i])				
    return np.array(monorave)

# make mono from average l and r and clean it up
def stereo2monorave3(sig):
    monorave = []
    for i in range(0,len(sig), 2):
        try:
            monorave.append((1/(1+np.exp((sig[i+1])*(sig[i])/2))*255)&255)
        except:
            monorave.append(sig[i])				
    return np.array(monorave)

# make mono from average l and r and clean it up
def stereo2monorave4(sig):
    monorave = []
    for i in range(0,len(sig), 2):
        try:
            monorave.append((1/(1+~np.exp((sig[i+1])*(sig[i])/2))*127)&255)
        except:
            monorave.append(sig[i])				
    return np.array(monorave)
            
# make mono from right channel only
def stereo2monorar(sig):
    monorar = []
    for i in range(0,len(sig), 2):
        monorar.append(sig[i+1])
    return np.array(monorar)
        
# open sound file     
def openFile(filename, printInfo=1):
    wf = wave.open(filename , "r" )
    fs = wf.getframerate()                                              # Sampling frequency
    x = wf.readframes(wf.getnframes())
    x = frombuffer(x, dtype= "int16") / 32768.0                         # -1 - +1Normalized to
    if printInfo == 1:
        printWaveInfo(wf)
    wf.close()
    return x, fs, wf.getnchannels(), wf.getnframes()

# close sound file
def saveFile(data, fs, bit, filename, channel=1):
    print("channel", channel)
    data = [int(v * 32767.0) for v in data]
    data = struct.pack("h" * len(data), *data)
    w = wave.Wave_write(filename + ".wav")
    w.setnchannels(channel)
    w.setsampwidth(int(bit/8))
    w.setframerate(fs)
    w.writeframes(data)
    w.close()

# print wave file information
def printWaveInfo(wf):
    """WAVE Get file information"""
    print ("Number of channels:", wf.getnchannels())
    print ("Sample width:", wf.getsampwidth())
    print ("Sampling frequency:", wf.getframerate())
    print ("Number of frames:", wf.getnframes())
    print ("Parameters:", wf.getparams())
    print ("Length (seconds):", float(wf.getnframes()) / wf.getframerate())

# normqalise sound file    
def nomalize(x, xmax, xmin, a):
    min = 1 / 32768.0
    try:
        z = a * (x - xmin) / (xmax - xmin)
    except ZeroDivisionError:
        z = a * (x - xmin) / min
    return z

# pre-emphasis FIR filter
def preEmphasis(signal, p):
    """Emphasis filter"""
    # Create FIR filter with coefficients (1.0, -p)
    return scipy.signal.lfilter([1.0, -p], 1, signal)

# parent path file utility
def parentpath(path=__file__, f=0):
    return str('/'.join(os.path.abspath(path).split('/')[0:-1-f]))
                
if __name__ == "__main__" :


    if (len(sys.argv) - 1) <= 0:                                        # throw exception if no file to process
        print("<program> filename")
        sys.exit()

    mySoundFiles = "/mnt/c/linuxmirror/"
    fileNam = mySoundFiles + sys.argv[1]                                # ------- read in the specified sound file ---------
    fileNameOnly = sys.argv[1]
    if os.path.isfile(fileNam) == False:
        fileNam = fileNam + ".wav"
        fileNameOnly = sys.argv[1] + ".wav"
    if os.path.isfile(fileNam) == False:
        print("invalid file name or path %s" % fileNam)	
        sys.exit(1)
 
    fileNameSplit = fileNameOnly.split(".")                             # split the file and extension

    filePydubDown = fileNameSplit[0] + "_down." + fileNameSplit[1]      # define the extensions for each of the output files for each transformation 
    outPydubDown = mySoundFiles + filePydubDown  
    fileMonoLeft = fileNameSplit[0] + "_mono_l"    
    outMonoLeft = mySoundFiles + fileMonoLeft
    fileMonoRight = fileNameSplit[0] + "_mono_r"    
    outMonoRight = mySoundFiles + fileMonoRight 
    fileMonoAve = fileNameSplit[0] + "_mono_av"     
    outMonoAve = mySoundFiles + fileMonoAve 
    fileMonoEffect = fileNameSplit[0] + "_mono_eff"     
    outMonoEffect = mySoundFiles + fileMonoEffect 
    fileMonoDeep = fileNameSplit[0] + "_mono_deep"     
    outMonoDeep = mySoundFiles + fileMonoDeep 
    fileMonoClean = fileNameSplit[0] + "_mono_clean"     
    outMonoClean = mySoundFiles + fileMonoClean 
    fileMonoInvert = fileNameSplit[0] + "_mono_invert"     
    outMonoInvert = mySoundFiles + fileMonoInvert 
                                                     
    # downsampling to 16000 using pydub library function
    sound = am.from_file(fileNam, format='wav', frame_rate=44000)
    sound = sound.set_frame_rate(16000)
    sound.export(outPydubDown, format='wav') 

    # opening the sound file specified with python wav library      
    filedata = openFile(outPydubDown)
    sig = filedata[0]
    fs = filedata[1]
    L = filedata[2]

    # left channel to mono
    sig1 = stereo2monoral(sig);
    saveFile(sig1, fs, 16, outMonoLeft, 1)

    # effect the sound (sounds deeper)    
    sig1 = stereo2monorave2(sig);
    saveFile(sig1, fs, 16, outMonoDeep, 1)

    # clean up the sound (top and bottom) with a sigmoid function    
    sig1 = stereo2monorave3(sig);
    saveFile(sig1, fs, 16, outMonoClean, 1)

    # clean up the sound (top and bottom) with a sigmoid function (changed the bias)   
    sig1 = stereo2monorave4(sig);
    saveFile(sig1, fs, 16, outMonoInvert, 1)
        
    # average left and right channel to mono
    sig1 = stereo2monoave(sig);
    saveFile(sig1, fs, 16, outMonoAve, 1)
        
    # create an effect (shown for purpose) by taking average of averaged mono signal
    sig1 = stereo2monoave(sig1);
    saveFile(sig1, fs, 16, outMonoEffect, 1)    

    # right channel to mono
    sig1 = stereo2monorar(sig);
    saveFile(sig1, fs, 16, outMonoRight, 1)
