#Aengus Patterson, 2022
#this converts a given file into a wav file format using MoviePy so no extra libraries are needed

#for checking if there is an audio stream
from pymediainfo import MediaInfo
#for converting any file into a wav
from moviepy.editor import *
#for reaming the audio file extention
from pathlib import Path


#this code block check if there is an audio stream
def is_audio_track(filename):
    media_info = MediaInfo.parse(filename)
    for track in media_info.tracks:
        if track.track_type == "Audio":
            return True
    return False

def is_video_track(filename):
    media_info = MediaInfo.parse(filename)
    for track in media_info.tracks:
        if track.track_type == "Video":
            return True
    return False

#pathlib was throwing some obscure error when I tried to do this using it, so here's the manual function
def rename_to_wav(filename):
    extention_start = filename.index(".")
    name =  filename[:extention_start]
    return (name + ".wav")

def convert_to_audio(filename):
    if Path(filename).suffix != ".wav":
        if is_audio_track(filename):
            clip = 0
            if is_video_track(filename):
                clip = VideoFileClip(filename)
            else:
                clip = AudioFileClip(filename)
            clip.audio.write_audiofile(rename_to_wav(filename))
        else:
            print ("no audio track; unable to grab audio and therefore can't do auto subtitles.")
            return False
    else:
        print ("file is already .wav. no conversion necessary")
    return rename_to_wav(filename)
#convert_to_audio("prod_test.mp4")
