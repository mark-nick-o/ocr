#
# ======================================================================
# IIR Filter using scipy
# perform high pass or low pass filter on sound to try to clarify for
# the sound to text engine
# ======================================================================
#
# ref :- https://atatat.hatenablog.com/entry/data_proc_python4
#        https://github.com/jiaaro/pydub/blob/master/test/test.py
#
# Implement High or low pass filter to attempt to make sound more 
# recognisable to the speach to text engine e.g. mimi
#
import os
import sys
import wave
from sound import *
import numpy as np
from pylab import *
import struct
from scipy import signal
import numpy as np
from pydub import AudioSegment as am
import re

#
# split string by delimeter 
#
def split(delimiters, string, maxsplit=0):
    regexPattern = '|'.join(map(re.escape, delimiters))
    return re.split(regexPattern, string, maxsplit)
    
# lowpass filter
def lowpass(x, samplerate, fp, fs, gpass, gstop):
    fn = samplerate / 2                                                # the Nyquist species number fn is calculated using the sampling rate (number of samples / second) of the signal.
    wp = fp / fn                                                        # the pass frequency wp of the low-pass filter
    ws = fs / fn                                                        # blocking frequency
    N, Wn = signal.buttord(wp, ws, gpass, gstop)                        # attenuation amount gpass in wp is specified in dB Gstop is also set to 40 dB this time in attenuation in the blocking band
    b, a = signal.butter(N, Wn, "low")                                  # Calculate the numerator and denominator of the filter transfer function
    if ((len(a) >= 2) and (len(x) >= 2)) :
        y = signal.filtfilt(b, a, x)                                    # filter the signal
    return y 

# highpass filter
def hipass(x, samplerate, fp, fs, gpass, gstop):
    fn = samplerate / 2                                                 # the Nyquist species number fn is calculated using the sampling rate (number of samples / second) of the signal.
    wp = fp / fn                                                        # Normalized Passband End Frequency with Nyquist Frequency
    ws = fs / fn                                                        # Normalized Stopband End Frequency with Nyquist Frequency
    N, Wn = signal.buttord(wp, ws, gpass, gstop)                        # Calculate normalized frequency of order and Butterworth
    b, a = signal.butter(N, Wn, "high")                                 # Calculate the numerator and denominator of the filter transfer function
    y = signal.filtfilt(b, a, x)                                        # filter the signal
    return y

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
                
if __name__ == "__main__" :

    #
    # default parameters to filters
    #
    fp = 300                                                            # Passband end frequency[Hz]
    fs = 600                                                            # Stopband end frequency[Hz]
    gpass = 3                                                           # Passband end maximum loss[dB]
    gstop = 40                                                          # Minimum stop-band end loss[dB]
    samplerate = 25600                                                  # default sample rate 25.6KHz

    #
    # alternative settings
    #
    #fp = 700                                                           # Passband end frequency[Hz]
    #fs = 1500                                                          # Stopband end frequency[Hz]

    bandFreq = 800                                                      # treble bass reduce filter amount
    #bandFreq = 400                                                      # treble bass reduce filter amount

    ERR_NO_FILE = 1                                                     # you may query this with echo $? in shell
    ERR_INVALID_OPTION = 2  
    
# ========= check the options passed had at least 1 parameter (file) ===
    if (len(sys.argv) - 1) <= 0:
        print("Please pass the filename for the sound to filter, \n optionally you can specify the bands")
        sys.exit(ERR_NO_FILE)     
    
# ======== get the name of the file to check ===========================
    fileNam = "/mnt/c/linuxmirror/" + sys.argv[1]
    if os.path.isfile(fileNam) == False:
	    fileNam = fileNam + ".wav"
    if os.path.isfile(fileNam) == False:
        print("invalid file name or path %s" % fileNam)	
        sys.exit(ERR_NO_FILE)             

    # create the output filenames
    fileElements = split('.',fileNam)
    output_file_low  = fileElements[0] + "_low.wav" 
    output_file_high  = fileElements[0] + "_high.wav" 
    output_file_ds  = fileElements[0] + "_ds.wav" 

    #
    # using pydub convert the type if neccessary
    #
    if not fileElements[1].find("wav") == -1 :
        data3 = am.from_file(fileNam, format='wav')
    elif not fileElements[1].find("mp4") == -1 :
        data3 = am.from_file(fileNam, format='mp4')
    elif not fileElements[1].find("mp3") == -1 :
        data3 = am.from_file(fileNam, format='mp3')
    elif not fileElements[1].find("wma") == -1 :
        data3 = am.from_file(fileNam, format='wma')
    elif not fileElements[1].find("aac") == -1 :
        data3 = am.from_file(fileNam, format='aac')
    elif not fileElements[1].find("ogg") == -1 :
        data3 = am.from_file(fileNam, format='ogg')
    elif not fileElements[1].find("flv") == -1 :
        data3 = am.from_file(fileNam, format='flv')        

    data3 = data3.set_frame_rate(samplerate)
    data3 = data3.normalize(0.0)
    data3 = data3.low_pass_filter(bandFreq)                             # less treble
    data3 = data3.high_pass_filter(bandFreq)                            # less bass
    data3.export(output_file_ds, format="wav")

    data3 = openFile(output_file_ds)
    #  data3 = openFile(fileNam) <----- if you want to use raw original file to scipy rather than the one modified by pydub first
    
    #
    # using scipy
    #
    sig = data3[0]
    samplerate = data3[1]
    L = data3[2]    
     
    # Execute a low-pass function
    data_lofilt = lowpass(sig, samplerate, fp, fs, gpass, gstop)
    saveFile(data_lofilt, samplerate, 16, output_file_low, 1)

    # Execute a high-pass function and reverse the bands
    fpold=fp
    fp=fs 
    fs=fpold
    data_hifilt = hipass(sig, samplerate, fp, fs, gpass, gstop)
    saveFile(data_hifilt, samplerate, 16, output_file_high, 1)


