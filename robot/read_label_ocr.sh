:
#[ "$3" == "DEBUG" ] && set -x
#
# Run the tesseract ocr and print the result on file if you omit  
# extension you get .jpg file
#

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
    [ -f $1-deu.txt ] && cat $1-deu.txt | tr [:lower:] [:upper:] | grep MILCH && [ $? -eq 0 ] && echo Milk && rm $1-deu.txt
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
    # if you have a paid yandex account
    #
    # /home/mark/pics/yatranslate_notify.sh `cat $1-rus.txt`
    [ -f $1-rus.txt ] && cat $1-rus.txt && rm $1-rus.txt
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

