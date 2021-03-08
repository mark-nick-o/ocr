:
#[ "$3" == "DEBUG" ] && set -x
#
# Run the tesseract ocr and print the result on file if you omit  
# extension you get .jpg file
#
# if you need co-ordinates in the image for a text you can use hocr option 
# with tesseract to give an xml output called .hocr
#
[ $# -eq 0 ] && { echo "Usage: $0 filename <option: language jpn, spa, fra, deu, ita, rus alternate engine : ocrad >"; exit 1; }

HOME=/home/mark/pics
NOTWITHAT=0
NOTWITHDOT=0
NUMCHAR=0

case $2 in

  # sudo apt-get install tesseract-ocr-ita
  Japan | jpn)
    [ -f $1-jpn.txt ] && rm $1-jpn.txt 
    numFields=`echo $1 | awk '-F.' '{ print NF }'`
    [ "$numFields" -eq 1 ] && [ -f /mnt/c/linuxmirror/$1.jpg ] && tesseract /mnt/c/linuxmirror/$1.jpg $1-jpn -l jpn
    [ "$numFields" -eq 2 ] && [ -f /mnt/c/linuxmirror/$1 ] && tesseract /mnt/c/linuxmirror/$1 $1-jpn -l jpn
    # use dict to translate
    [ -f $1-jpn.txt ] && dict -d fd-jpn-eng `cat $1-jpn.txt` && rm $1-jpn.txt
    # could also use trans (look below if you want to choose the translator engine)
    # [ -f $1-jpn.txt ] && trans `cat $1-jpn.txt` && rm $1-jpn.txt
    ;;

  # sudo apt-get install tesseract-ocr-spa
  Spain | spa | es)
    echo "spain"
    #[ -f $1-spa.txt ] && rm $1-spa.txt 
    numFields=`echo $1 | awk '-F.' '{ print NF }'`
    [ "$numFields" -eq 1 ] && [ -f /mnt/c/linuxmirror/$1.jpg ] && tesseract /mnt/c/linuxmirror/$1.jpg $1-spa -l spa
    [ "$numFields" -eq 2 ] && [ -f /mnt/c/linuxmirror/$1 ] && tesseract /mnt/c/linuxmirror/$1 $1-spa -l spa
    # use dict to translate
    [ -f $1-spa.txt ] && dict -d fd-spa-eng `cat $1-spa.txt` #&& rm $1-spa.txt
    # could also use trans (look below if you want to choose the translator engine)
    # [ -f $1-spa.txt ] && trans `cat $1-spa.txt` && rm $1-spa.txt
    ;;

  # sudo apt-get install tesseract-ocr-fra
  France | fra | fr)
    [ -f $1-fra.txt ] && rm $1-fra.txt 
    numFields=`echo $1 | awk '-F.' '{ print NF }'`
    [ "$numFields" -eq 1 ] && [ -f /mnt/c/linuxmirror/$1.jpg ] && tesseract /mnt/c/linuxmirror/$1.jpg $1-fra -l fra
    [ "$numFields" -eq 2 ] && [ -f /mnt/c/linuxmirror/$1 ] && tesseract /mnt/c/linuxmirror/$1 $1-fra -l fra
    # use dict to translate - noticed you might have joined words which skipped trans engine so did a grep for :- (word contains "lait")
    [ -f $1-fra.txt ] && dict -d fd-fra-eng `cat $1-fra.txt` 
    [ -f $1-fra.txt ] && cat $1-fra.txt | tr [:lower:] [:upper:] | grep LAIT && [ $? -eq 0 ] && echo Milk && rm $1-fra.txt
    # could also use trans (look below if you want to choose the translator engine)
    # [ -f $1-spa.txt ] && trans es: `cat $1-spa.txt` && rm $1-spa.txt
    ;;

  # sudo apt-get install tesseract-ocr-deu
  Germany | deu | Deutschland | ge)
    [ -f $1-deu.txt ] && rm $1-deu.txt 
    numFields=`echo $1 | awk '-F.' '{ print NF }'`
    [ "$numFields" -eq 1 ] && [ -f /mnt/c/linuxmirror/$1.jpg ] && tesseract /mnt/c/linuxmirror/$1.jpg $1-deu -l deu
    [ "$numFields" -eq 2 ] && [ -f /mnt/c/linuxmirror/$1 ] && tesseract /mnt/c/linuxmirror/$1 $1-deu -l deu
    # use dict to translate - noticed you might have joined words which skipped trans engine so did a grep for :- (word contains "milch")
    [ -f $1-deu.txt ] && dict -d fd-deu-eng `cat $1-deu.txt` 
    #
    # ---- here im making correction for dict --------------------------
    #      using rules and linux
    #
    # we needed to eliminate office@naturjoghurt.at
    # because it is a email and not a product
    # likewise a web address needs eliminating such as this
    # www.fruchtjoghurt.de
    # because we can get partial we just say never a @ or . but we could say
    # @ and a . or 2 . makes it true
    # we check if we didnt get a @ or a . in that word before we ensure it is checked for yoghurt
    #
    # this would work for normal documents, but because it is a stream
    # which iterates as we read from the ocr at different angles of picture
    # we need to consider one pass might give us DNATURJOGHURT_
    # for example therefore we set a turn it off eliminate flag if we get the 
    # email seen.
    #
    [ -f $1-deu.txt ] && cat $1-deu.txt | tr [:lower:] [:upper:] | grep JOGHURT > $HOME/foundWord.txt   # dict missed it for example fruchtjoghurt was not known
    [ -s $HOME/foundWord.txt ] && NUMCHAR=`wc -c $HOME/foundWord.txt | awk '{ print $1 }'`
    if [ "$NUMCHAR" -gt 6 ]                                             # it wasnt a cariage return (was at least 6 chars long)
    then
        NOTWITHAT=`cat $HOME/foundWord.txt | awk '-F@' '{print NF}'`
        NOTWITHDOT=`cat $HOME/foundWord.txt | awk '-F.' '{print NF}'`
        #if !([ "$NOTWITHAT" -eq 2 ] && [ "$NOTWITHDOT" -eq 2 ]) ; then echo "Yogurt" ; fi  # not @ and a . in match word (might mean a email or webaddress)
        if [ "$NOTWITHAT" -eq 1 ] && [ "$NOTWITHDOT" -eq 1 ] ; then echo "Yogurt" ; else echo "RemovYog" ; cp $HOME/foundWord.txt $HOME/this.txt ; fi      # not @ or a . (might mean a email or webaddress)
        rm $HOME/foundWord.txt
    else
        NUMCHAR=0
    fi
    [ -f $1-deu.txt ] && cat $1-deu.txt | tr [:lower:] [:upper:] | grep VOLLMILCH && [ $? -eq 0 ] && echo "Whole Milk"   # dict wrongly says unskimmed ? okay if voll milch
    [ -f $1-deu.txt ] && cat $1-deu.txt | tr [:lower:] [:upper:] | grep ROHMILCH && [ $? -eq 0 ] && echo "Raw Milk" && rm $1-deu.txt && exit # dict missed it
    [ -f $1-deu.txt ] && cat $1-deu.txt | tr [:lower:] [:upper:] | grep MILCH && [ $? -eq 0 ] && echo Milk 
    [ -f $1-deu.txt ] && rm $1-deu.txt
    # could also use trans (look below if you want to choose the translator engine default:google requires net connection)
    # [ -f $1-deu.txt ] && trans de: `cat $1-deu.txt` && rm $1-deu.txt
    ;;

  # sudo apt-get install tesseract-ocr-ita
  Italy | ita | Italia | it)
    [ -f $1-ita.txt ] && rm $1-ita.txt 
    numFields=`echo $1 | awk '-F.' '{ print NF }'`
    [ "$numFields" -eq 1 ] && [ -f /mnt/c/linuxmirror/$1.jpg ] && tesseract /mnt/c/linuxmirror/$1.jpg $1-ita -l ita
    [ "$numFields" -eq 2 ] && [ -f /mnt/c/linuxmirror/$1 ] && tesseract /mnt/c/linuxmirror/$1 $1-ita -l ita
    # use dict to translate - noticed you might have joined words which skipped trans engine so did a grep for :- (word contains "latte")
    [ -f $1-ita.txt ] && dict -d fd-ita-eng `cat $1-ita.txt`
    [ -f $1-ita.txt ] && cat $1-ita.txt | tr [:lower:] [:upper:] | grep "SOLO NATURA" && [ $? -eq 0 ] && echo Organic 
    [ -f $1-ita.txt ] && cat $1-ita.txt | tr [:lower:] [:upper:] | grep "CIOCCOLATO" && [ $? -eq 0 ] && echo Chocolate
    [ -f $1-ita.txt ] && cat $1-ita.txt | tr [:lower:] [:upper:] | grep LATTE && [ $? -eq 0 ] && echo Milk && rm $1-ita.txt
    # could also use trans (look below if you want to choose the translator engine default:google requires net connection)
    # [ -f $1-ita.txt ] && trans it: `cat $1-ita.txt` && rm $1-ita.txt
    ;;
    
  # sudo apt-get install tesseract-ocr-rus        
  Russia | "Russian Federation" | rus | "Soviet Union")
    [ -f $1-rus.txt ] && rm $1-rus.txt 
    numFields=`echo $1 | awk '-F.' '{ print NF }'`
    [ "$numFields" -eq 1 ] && [ -f /mnt/c/linuxmirror/$1.jpg ] && tesseract /mnt/c/linuxmirror/$1.jpg $1-rus -l rus
    [ "$numFields" -eq 2 ] && [ -f /mnt/c/linuxmirror/$1 ] && tesseract /mnt/c/linuxmirror/$1 $1-rus -l rus
    # use dict to translate (dont seem to have the dictionary)
    # [ -f $1-rus.txt ] && dict -d fd-rus-eng `cat $1-rus.txt` && rm $1-rus.txt
    # could also use trans (look below if you want to choose the translator engine) however returns shooter for молоко(milk)
    # [ -f $1-rus.txt ] && trans ru: `cat $1-rus.txt` && rm $1-rus.txt
    #
    # if you have a paid yandex account you can use it.
    #
    # /home/mark/pics/yatranslate_notify.sh `cat $1-rus.txt`
    #
    # put some basic words in the python code so just translate to lower case 
    #
    [ -f $1-rus.txt ] && cat $1-rus.txt && rm $1-rus.txt
    ;;

   # choose to use the ocrad ocr instead
  ocrad)
    numFields=`echo $1 | awk '-F.' '{ print NF }'`
    [ "$numFields" -eq 1 ] && [ -f /mnt/c/linuxmirror/$1.pnm ] && ocrad --format=utf8 /mnt/c/linuxmirror/$1.pnm 
    [ "$numFields" -eq 2 ] && [ -f /mnt/c/linuxmirror/$1 ] && ocrad --format=utf8 /mnt/c/linuxmirror/$1 
    ;;
    
   # choose to use the tensorflow ocr instead
  keras)
    python $HOME/keras_emnist.py $1
    ;;
    
  *)
    [ -f $1-eng.txt ] && rm $1-eng.txt 
    numFields=`echo $1 | awk '-F.' '{ print NF }'`
    [ "$numFields" -eq 1 ] && [ -f /mnt/c/linuxmirror/$1.jpg ] && tesseract /mnt/c/linuxmirror/$1.jpg $1-eng -l eng
    [ "$numFields" -eq 2 ] && [ -f /mnt/c/linuxmirror/$1 ] && tesseract /mnt/c/linuxmirror/$1 $1-eng -l eng
    [ -f $1-eng.txt ] && cat $1-eng.txt && rm $1-eng.txt
    ;;
esac

# ============= notes on translation ===================================
#
# if you want to read another language text and translate it
# you should use that engine
# trans -R -> gives country code
# example spanish es, welsh cy
# trans es: "Igualdad, fraternidad y libertad" 
#
# call the tesseract in that language is best
#
# to get all
# sudo apt-get install tesseract-ocr-all
# or on various countries
# sudo apt-get install tesseract-ocr-jpn
# sudo apt-get install tesseract-ocr-rus
# sudo apt-get install tesseract-ocr-fra
# sudo apt-get install tesseract-ocr-spa
#
# tesseract /mnt/c/linuxmirror/$1 $1-es -l es
# trans es: `cat $1-es.txt` > CW146-eng.txt
#
#[ -f $1-eng.txt ] && trans `cat $1-eng.txt`
#
# example to use each engine to translate english to japanese
#
# for engine in google bing yandex apertium; do \
#    echo "$engine"; \
#    trans -f en -t ja -e $engine -no-init -verbose "just testing"; \
# done
#
# or with apertium
# sudo apt install apertium apertium-en-es
# echo "Hola Mundo." | apertium -a es-en
#
# or This seemed to work quicker it then uses local dictionary
#
# sudo apt-get install dictd
# sudo apt-get install dict-freedict-eng-fra
# sudo apt-get install dict-freedict-eng-spa
# sudo apt-get install dict-freedict-eng-rus
#
# dict -d fd-spa-eng "leche"
#
# [ -f $1-eng.txt ] && dict -d fd-spa-eng `cat $1-eng.txt`
#

