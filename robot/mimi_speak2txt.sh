#
# shell script to convert speach file to text using mimi REST API
#
set -x
MIMIHOME=/home/mark/pics
SOUNDFILEDIR=/mnt/c/linuxmirror
[ $# -eq 0 ] && echo "Usage:: $0 <soundfilename>" && exit 0
MIMIPROCESS=nict-asr
[ $# -eq 2 ] && MIMIPROCESS=$2
if [ -f $MIMIHOME/mimi.api ] 
then
    API_KEY=`cat $MIMIHOME/mimi.api | awk '-F,' '{print $11}' | awk '-F:' '{print $2}' | awk '-F"' '{print $2}'`
    echo using $API_KEY
else
   echo "get API key first"
   exit 1
fi
[ "$API_KEY" = "" ] && echo "no api key" && exit 2

echo $MIMIPROCESS
# call rest API change language as you're audio atm works best in japanese (testing in progress)
#-H "x-mimi-process:nict-asr" 
curl https://service.mimi.fd.ai \
-H "Content-Type: audio/x-pcm;bit=16;rate=16000;channels=1" \
-H "x-mimi-process:$MIMIPROCESS" \
-H "Authorization: Bearer $API_KEY" \
-H "x-mimi-input-language: ja" \
--data-binary @$SOUNDFILEDIR/$1

# reply {"type": "asr#nictlvcsr", "session_id": "ea530534-84e4-11eb-964f-42010a920fc6", "status": "recog-finished", "response": [{"result": "ワッツ|ワッツ|ワッツ|名詞-固有名詞|||人名-姓|"},{"result": "ハプニング|ハプニング|ハプニング|名詞-一般||||"},{"result": "|||SENT-START-END||||"},{"result": "|||UTT-END||||"}]}
# Invalid mimi API access token
