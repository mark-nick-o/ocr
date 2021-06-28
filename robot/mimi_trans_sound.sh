:
#
# wrapper for running python script that is calling the mimi REST-API
# to convert sppech to text
# if the engine has been specified it uses that one only otherwise it trys
# each of the possible three
#
if [ $# -gt 1 ] 
then
    python sound_input_mimi2.py --sound2txt $1 $2
else
    python sound_input_mimi2.py --sound2txt $1 
    python sound_input_mimi2.py --sound2txt $1 nictasr
    python sound_input_mimi2.py --sound2txt $1 googleasr
fi
