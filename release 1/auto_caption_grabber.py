#Aengus Patterson, 2022
#this grabs captions from a given audio file and generates a script with 
#the captions' approximated time's.
#
#alternatively (and preferably), you can just import pre-made captions because
#current speech recognition is very bad. 
#
#this code is absolutely devious and follows no logical format


#speech recognition libraries
import speech_recognition as sr 
#mediainfo library, to determin the length of the audio file
from pymediainfo import MediaInfo
#allows for the requesting internet stuff
import requests
#for writing stuff to the script file
import json  
#for splitting arrays
import numpy


#----there are a lot of global variables because I originally built this without any functions

#filename for which we do operations on
filename = "example.wav"
#object for speech recognition
r = sr.Recognizer()
#duration of audio, captured by MediaInfo module
audio_duration = 0.0
#the set of all audio bits
audio_chunk_array = []
#the length of each audio chunk
chunk_frequency = 3 #normally this would be obtained with an input
#this is a number that allows for a higher chunk frequency while still allowing lower word count by dividing chunk_frequency, called subchunking
chunk_factor = 3
#is user connected to internet or not; google speech api relies on it
internet_connection = False
#stores each raw, converted audio chunk.
full_text = []
#the defualt text color to store
default_color = "white"
#the default emphasized color to store
default_emphasized_color = "red"

#determins whether to use an imported subtitle txt file
yt_subtitle_import = False
#the path to said subtitle file
subtitle_path = ""


#this code just grabs the audio duration from the file, which is used to determin how many audio chunks should be made
#this is not a function because it's soul purpose is to set the duration
    #this sure looks like a function to me?
def get_audio_duration():
    media_info = MediaInfo.parse(filename)
    for track in media_info.tracks:
        if track.track_type == "Video":
            pass #last time i didn't include an if clause for a video track, the audio clause was skipped, idk
        elif track.track_type == "Audio":
            return track.to_data()['duration']


#this code block grabs chunks from the audio file, so they can be interpreted individually
def get_audio_chunks():
    i = 0
    with sr.AudioFile(filename) as source:
        while i <= ((audio_duration / 1000) / chunk_frequency * chunk_frequency):
            audio_chunk_array.append(r.record(source, duration=chunk_frequency))
            i += chunk_frequency

#this block of code checks for an internet connection, to determin to use google api. copied from geeksforgeeks.
def get_internet_connection():
    try:
        request = requests.get("https://www.geeksforgeeks.org", timeout=10)
        internet_connection = True
    
    except (requests.ConnectionError, requests.Timeout) as exception:
        internet_connection = False
        print ("no internet connection. resorting to less acurate sphinx voice recognizer")


#this block of code takes the chunks, interprets them, and then adds them to the full_text array, so they can be
#divided into seperete lines/subchunks and saved into script.txt later
def interpret_audio():
    for i in audio_chunk_array:
        try:
            if internet_connection:
                full_text.append(r.recognize_google(i))
            else:
                full_text.append(r.recognize_sphinx(i))
        except:
            full_text.append("_________")
            print("invalid: " + str(i))


#this is for when a youtube subtitle file is imported
#subs can be downloaded with https://www.downloadyoutubesubtitles.com
def import_yt_subs():
    sub_file = open(subtitle_path)
    script = open("script.txt", "w")
    #the raw text lines
    lines = []
    start_times = []
    end_times = []
    for line in sub_file:
        #this parses the time data for the following line
        if " --> " in line:
            starts, ends = line.split(sep=" --> ")
            s_hour, s_minute, s_second = starts.split(sep=":")
            e_hour, e_minute, e_second = ends.split(sep=":")
            start_time = round((float(s_hour) * 3600) + (float(s_minute) * 60) + float(s_second), 1)
            end_time = round((float(e_hour) * 3600) + (float(e_minute) * 60) + float(e_second), 1)
            #this will happen with the auto-generated captions sometimes, so this is an easy fix:
            if len(end_times) > 0:
                if start_time < end_times[-1]:
                    end_times[-1] = start_time
            start_times.append(start_time)
            end_times.append(end_time)

        elif line != "\n":
            lines.append(line)
    #this makes sure the start time is forced to actually start at 0 rather than halfway into the vid
    absolute_start = start_times[0]
    if absolute_start != 0:
        for i in range(len(start_times)):
            start_times[i] = start_times[i] - absolute_start
        for i in range(len(end_times)):
            end_times[i] = end_times[i] - absolute_start
    line_num = 0
    for line in lines:
        words_in_line = line.split()
        if len(words_in_line) > chunk_factor:
            print (line_num)
            overall_duration = end_times[line_num] - start_times[line_num]
            duration_step = overall_duration / chunk_factor
            subchunk_array = numpy.array_split(numpy.array(words_in_line),chunk_factor)
            subchunk_num = 0
            for i in subchunk_array:
                save_to_script(i, round(start_times[line_num] + (duration_step * subchunk_num), 1), round(start_times[line_num] + (duration_step * (subchunk_num + 1)), 1), script)
                subchunk_num += 1
        else:
            save_to_script(words_in_line, start_times[line_num], end_times[line_num], script)
        line_num += 1
    script.close()
    sub_file.close()



#----this section writes everything in subchunk_array to the scrip.txt file
#it's the only func (at time of writing) that's not called from start(); rather save_subchunks()
def save_to_script(subchunk, start, end, script):
    #array order: line of text, start time, end time, color type, important words, important word color
    #here we just convert the array of words to text so that it's easier to edit
    saved_text = ""
    for i in subchunk:
        saved_text += i + " "
    save_array = [saved_text, start, end, default_color, "", default_emphasized_color]
    script.write(json.dumps(save_array) + "\n")


#seperates all the chunks into further subchunks based on some voodoo math/logic and then begins to save them
def save_subchunks():
    #----this setction seperates all the chunks into subchunks, expressed in subchunk_array
    #the duration to write to the string
    current_duration = 0
    #the file used to write shit
    script = open("script.txt", "w")
    #the number of words in current chunk, so it can be used to calculate words per subchunk
    word_count = 0
    actual_chunk_duration = chunk_frequency / chunk_factor
    current_words = ""
    for text in full_text:
        #this is the variable for all the words in the current chunk, seperated into arrays for sub-chunking purposes.
        subchunk_array = []
        words = text.split()
        word_count = len(words)
        words_per_subchunk = round((word_count / chunk_factor))
        #if there are less words than splits in the chunks, then disregard any subchunking stuff.
        if word_count >= chunk_factor:
            #this is the subchunking part.
            for i in range(0, word_count, words_per_subchunk):
                subchunk_array.append(words[i:i+words_per_subchunk])
        else:
            subchunk_array.append(words)
        #if there is an extra subchunk (which will only consist of one word) then it's appended to the previous one and deleted
        #(this will just randomly happen sometimes)
        print (subchunk_array)
        if len(subchunk_array)  > chunk_factor :
            subchunk_array[-2].append(subchunk_array[-1][0])
            del subchunk_array[-1]
        #----this part prepares the subchunks/ chunks to be saved
        if word_count >= chunk_factor:
            for i in subchunk_array:
                save_to_script(i, current_duration, current_duration + (chunk_frequency / chunk_factor), script)
                current_duration += (chunk_frequency / chunk_factor)
        else:
            save_to_script(subchunk_array[0], current_duration, current_duration + chunk_frequency, script)
            current_duration += chunk_frequency
    script.close()
    
#calls the proper sequence of functions
def start():
    if yt_subtitle_import:
        import_yt_subs()
    else:
        global audio_duration 
        audio_duration = get_audio_duration()
        print ("processing...")
        get_audio_chunks()
        get_internet_connection()
        interpret_audio()
        save_subchunks()

