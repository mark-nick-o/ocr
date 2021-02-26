#!/bin/bash
 
#text=`xsel -o`
 
#if [ "$text" == "" ]; then
#	exit 0
#fi
 
translated=`/home/mark/pics/yatranslate.py "$text"`
 
lang="`echo $translated | cut -d "~" -f1`"
text="`echo $translated | cut -d "~" -f2`"

# sudo apt install libnotify-bin 
#notify-send "$lang" "$text"
echo "$text"

#  sudo apt-get install libnotify-bin xsel
#  notify-send -u critical "$(xsel -o)" "$(wget -U "Mozilla/5.0" -qO - "http://translate.google.com/translate_a/t?client=t&text=$(xsel -o | sed "s/[\"'<>]//g")&sl=auto&tl=en" | sed 's/\[\[\[\"//' | cut -d \" -f 1)"
