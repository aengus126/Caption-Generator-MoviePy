#Aengus Patterson, 2023
#sometimes when importing the subtitles, there's an additional line that has the line number.
#this aims to get rid of that so the scrip generator can work properly.

import os
from tkinter import filedialog
import tkinter


root = tkinter.Tk()
root.withdraw()

file_path = filedialog.askopenfilename()

try:
    subs_file = open(file_path)
except:
    print("couldn't open video path.")
    exit()
previous_blank  = True
previous_time = False
add_line = True
lines = []
for line in subs_file:
    add_line = True
    if line == "\n":
        previous_blank = True
        previous_time = False
    elif "-->" in line:
        previous_time = True
        previous_blank = False
        #this changes the comma to a ".", because the website i use does that.
        if "," in line:
            line = line.replace(",", ".")
    elif previous_blank:
        add_line = False
        previous_blank = False
    if add_line:
        lines.append(line)
subs_file.close()
#remove the file 
os.remove(file_path)
#replace it with a txt version
print (file_path.split(sep="."))
print (lines)
name, extention = file_path.split(sep=".")
file_path = name + ".txt"
subs_file = open(file_path,"w")
subs_file.writelines(lines)
subs_file.close()
