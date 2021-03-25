#
# shell script to convert speach file to text using mimi REST API
#
#set -x
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

curl https://tra.mimi.fd.ai/machine_translation \
-H "Authorization: Bearer $API_KEY" \
-d text=%E6%82%A8%E5%A5%BD \
-d source_lang=zh \
-d target_lang=ja
