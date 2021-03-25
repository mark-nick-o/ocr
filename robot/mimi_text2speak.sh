#
# shell script to convert speach file to text using mimi REST API
# atm I'm using this to generate test fiels to be listened to and tested for mimi-asr and nictasr
#
set -x
MIMIHOME=/home/mark/pics
SOUNDFILEDIR=/mnt/c/linuxmirror
if [ -f $MIMIHOME/mimi.api ] 
then
    API_KEY=`cat $MIMIHOME/mimi.api | awk '-F,' '{print $11}' | awk '-F:' '{print $2}' | awk '-F"' '{print $2}'`
    echo using $API_KEY
else
   echo "get API key first"
   exit 1
fi
[ "$API_KEY" = "" ] && echo "no api key" && exit 2


#-d text=%E3%81%93%E3%82%93%E3%81%AB%E3%81%A1%E3%81%AF
#-d text=%77%68%61%74%73%20%68%61%70%70%65%6e%69%6e%67 
#-d text=%64%6f%65%73%20%74%68%69%73%20%77%6f%72%6b 
#-d text=%6a%61%70%61%6e%20%74%65%73%74 
#-d text=%77%61%74%65%72%20%61%6e%64%20%73%65%61 
#-d text=%73%63%6f%74%6c%61%6e%64 
#-d text=%62%6c%61%63%6b%20%61%6e%64%20%74%61%6e 
#-d text=%77%61%6C%65%73%20%61%6E%64%20%65%6E%67%6C%61%6E%64 
curl https://tts.mimi.fd.ai/speech_synthesis \
-H "Authorization: Bearer $API_KEY" \
-d text=%67%6F%20%6C%65%66%74 \
-d engine=nict \
-d lang=ja > $SOUNDFILEDIR/test8.wav
