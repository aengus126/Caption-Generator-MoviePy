#Aengus Patterson, December 15 2022
#This is a procedural program that connects 3 other programs with the goal of 
#generating a single video with advanced captions.

import generate_video_v2
import auto_caption_grabber
import convert_file_to_wav
#for removing the wav file
import os

#some gui for stuff like the file dialogue
from tkinter import filedialog
import tkinter


root = tkinter.Tk()
root.withdraw()

print ("open the file that you would like to add captions to")

file_path = filedialog.askopenfilename()
if file_path == "":
    exit()

wav_path = convert_file_to_wav.convert_to_audio(file_path)
if wav_path == False:
    print ("Error: there is no audio in the file selected")
    exit()

def get_yes():
    input_string = input().lower()
    if input_string == "yes" or input_string == "y":
        return True
    else:
        return False


print ("\n")
print ("-auto-generating captions-")
auto_caption_grabber.filename = wav_path
print ("do you wish to generate captions? Choose this unless you already hit yes before. y/n default: yes")
if get_yes():
    print ("generate captions with speech recognition? y for yes, n to import yt captions file")
    if not get_yes():
        auto_caption_grabber.yt_subtitle_import = True
        auto_caption_grabber.subtitle_path = filedialog.askopenfilename()
    print ("do you want to adjust some caption generator settings? y/n")
    if get_yes():
        print ("the speach recognizer grabs phrases in chunks of x seconds. how long should x be? default: 3")
        auto_caption_grabber.chunk_frequency = float(input())
        print ("each chunk gets divided x times to form sub-chunks. what should x be? defualt: 3")
        auto_caption_grabber.chunk_factor = float(input())
        white_black_input = ""
        #TODO allow for more options.
        while white_black_input != "white" and white_black_input != "black":
            print ("what should the default text color be? white/black")
            white_black_input = input().lower()
        auto_caption_grabber.default_color = white_black_input
        print ("during the script review, you can can decide which words will be emphasized, which will be colored differently. what should the default color be for them?")
        #TODO restrict options a little so no mis-inputs are made
        auto_caption_grabber.default_emphasized_color = input()
    auto_caption_grabber.start()

print ("\n")
print ("a script has just been made in this applications directory, called script.txt. review it and make changes, add emphasized words, and change start/end times.")
print ('syntax for each chunk is: "Every word in these quotation marks", start_time, end_time, "text color", "emphasized words, "emphasized color"')
print ('enter "yes" or "y" when you have finished making changes.')
input_string = ""
while input_string != "yes" and input_string != "y":
    input_string = input().lower()

generate_video_v2.filename = file_path
generate_video_v2.video_duration = auto_caption_grabber.get_audio_duration() / 1000
print ("\n")
print ("-video generation-")
print ("do you want to adjust some video generation settings? y/n")
if get_yes():
    print ("each chunk is split into lines. each line can only contain x words. what should x be? default: 2")
    generate_video_v2.max_words = int(input())
    print ("you can adjust the text to be further up or down. a value of 70 just about centers it. what would you like?")
    generate_video_v2.text_shift = int(input())
    print ("what font size do you want? default: 80")
    generate_video_v2.font_size = int(input())
    print ("lines are seperated by a factor of x. what would you like x to be? default: 1")
    generate_video_v2.line_space = float(input())
    print ("do you want the text to have an outline? y/n")
    if get_yes():
        generate_video_v2.outline = True
        print ("what color should the outline be? default: black")
        generate_video_v2.outline_color = input()
        print ("you can adjust the outline to be thicker by a factor of x. what would you like x to be? default: 1")
        generate_video_v2.outline_factor = float(input())
    else:
        generate_video_v2.outline = False
    print ("the text can expand quickly to make it more flashy. do you want it to do this? y/n")
    if get_yes():
        generate_video_v2.expand_text = True
        print ("how long do you want the clip to expand for? default: 0.05")
        generate_video_v2.expand_time = float(input())
    print ("how many seconds should the video subtitles be delayed for? (a negative value is accepted) default: 0")
    generate_video_v2.sub_delay = float(input())

generate_video_v2.start()
os.remove(wav_path)