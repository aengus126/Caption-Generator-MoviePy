#Aengus Patterson, 2022
#this generates a video using a script generated with a different program.
#it's main function is to give engaging captions to the video.
#this is version 2 that uses less global variables and a more understandable approach

# Import everything needed to edit video clips
from moviepy.editor import *
#import json to parse the array
import json



#all the clips. Starts with the main video clip.
clips = []
#the max words in a line before it get's split
max_words = 2 
#a total shift up or down to all the text
text_shift = 170 
font_size = 80
line_space = 1 
#this will be set by the main file that strings all these together 
#it's used for shortining the last string of text to the video length
video_duration = 0
outline = True
#outline color is set to the oposite of text_color and only used if outline is true
outline_color = "black"
outline_factor = 1
#the following two vars determin if and how long expanding text should go for
expand_text = False
expand_time = .05
#when using this as a standalone file, for whatever reason, there should be a sample video file
filename = "sample_video.mp4"
background_footage = True
background_file = "footage/gta.mp4"
#start and end times of text can be delayed if the captions are kinda off
sub_delay = 0


#this function returns sizes of a clip to make it expand. very helpful for retention.
def expand_clip(t, width, height, clip_duration):
    #width_step * duration is the full width, so this is like the inverse or whatever
    width_step = width / clip_duration
    #similar to width_step, but it's proportional to height instead.
    height_step = height / clip_duration
    #by taking the current time * the current width step, we get the current width
    new_width = (t * width_step) + 1
    #same with the height. current clip time * current height step = desired height
    new_height = (t * height_step) + 1
    #return them as a list or a tuple or whatever it is
    return [new_width, new_height]



#returns an array of vertical offsets for a given set of lines, that way the lines don't overlap. 
def determin_positions(lines):
    offsets = []
    #the center line is the one that remains centered (center is a number representation)
    center = (len(lines) / 2)
    i = 0
    while i < len(lines):
        #some voodoo math that gives an appropriate offset. takes into consideration the linespace, font size, and overall text shift.
        offsets.append(int((i - center) * font_size * line_space * 2.3) - text_shift)
        i += 1
    return offsets


#creates a set of TextClips 
def generate_text_clips(text_segments, text_colors, start, end):
    #all the vertical positions, represented by offests from the center. 
    vertical_positions = determin_positions(text_segments)
    end += sub_delay
    start += sub_delay
    if end > video_duration and video_duration != 0:
        end = video_duration
    duration = end - start
    if expand_text:
        start += expand_time
        duration -= expand_time
    i = 0
    for i in range (len(text_segments)):
        line = text_segments[i]
        color = text_colors[i]
        #the actual text to be assigned to the text clip
        text_property = ""
        #generates the text based on the words in the line array
        for word in line:
            text_property += word + " "
        new_clip = TextClip(text_property, color=color, font="Impact", stroke_color=outline_color, stroke_width=(int(outline) * font_size / 30 * outline_factor), fontsize=font_size).set_position("center")
        #this is more voodoo magic to determin what kind of margin to give the clip so that it will be vertically offset
        if vertical_positions[i] < 0:
            new_clip = new_clip.margin(bottom=-vertical_positions[i], opacity=0)
        elif vertical_positions[i] != 0:
            new_clip = new_clip.margin(top=vertical_positions[i], opacity=0)
        if expand_text:
            expanding_clip = new_clip.set_start(start - expand_time).set_duration(expand_time)
            width, height = expanding_clip.size
            expanding_clip = expanding_clip.resize(lambda t: expand_clip(t, width, height, expand_time))
            clips.append(expanding_clip)
        new_clip = new_clip.set_start(start)
        new_clip = new_clip.set_duration(duration)
        clips.append(new_clip)
        i += 1


def split_text(data_array):
    text = data_array[0]
    #contains arrays, each of which is a line, and each of which contains a set of words.
    text_segments = []
    #contains the colors of each array/line in text_segments
    text_colors = []
    #if the previous word added to the most recent line has a different color 
    #than the current text line, then the next word has to go to a different line
    last_color = ""
    #convert the text into an array of words
    text_array = text.split()
    #array splitting algorithm. assigns the current color, and then creates a new line in text_segments or adds to the 
    #most recent array/line in text_segments.
    for i in text_array:
        #the next for loop determins if i is an emphasized word and changes current_color accordingly
        current_color = data_array[3]
        for j in data_array[4]:
            if i.lower() == j.lower():
                current_color = data_array[5]
        #if the last lines color is the same as current, and the length is less than max words, then add to that line
        if last_color == current_color and len(text_segments[-1]) < max_words:
            text_segments[-1].append(i)
        #otherwise, create a new line with the word
        else:
            text_segments.append([i])
            text_colors.append(current_color)
        last_color = current_color
    generate_text_clips(text_segments, text_colors, data_array[1], data_array[2])


#this function parses through each line, gathers the data, and stores it into arrays.
def gather_data():
    i = 1
    script = open("script.txt", "r")
    for line in script.readlines():
        try:
            data_array = json.loads(line)
            emphasized_words = data_array[4].split(sep=" ")
            data_array[4] = emphasized_words
            split_text(data_array)
            i += 1
        except:
            #this commonly happens when a) a typo or b) an empty line
            print ("couldn't parse following line:")
            print (line)
    script.close()


def create_output_name():
    relative_path_array = filename.split(sep="/")
    relative_path = ""
    for i in range(len(relative_path_array) - 1):
        relative_path += relative_path_array[i] + "/"
    name, extention = relative_path_array[-1].split(sep=".")
    relative_path += name + " with captions.mp4"
    return relative_path
    

#adds the main clip plus potentially some background footage.
def initialize_clips():
    clip = VideoFileClip(filename)
    #if background_footage:




def start():
    #first add the source video to the clips array
    clip = VideoFileClip(filename)
    clips.append(clip)
    print ("processing...")
    gather_data()
    video = CompositeVideoClip(clips=clips)
    video.write_videofile(create_output_name(), codec='mpeg4', bitrate='4500k', audio_codec="aac")

#start()