# 
# A simple tool to help you easily analayse TODOs spread across a whole project.
# 
# Author(s):     Lewis Deane
# License:       MIT
# Last Modified: 8/6/2016
# 

# TODO Allow user to customise number of lines visible and trigger char.

import codecs
import sys
import os


# Define global variable ARGS which we then parse.
ARGS = sys.argv[1:]

# Define global variables which manage whether or not the user is choosing to search/ignore specific filetypes and directories.
EXCLUDE_DIRS  = True
EXCLUDE_FILES = True

# Define global variables to hold the filetypes and directories that should be searched/ignored later in the parse.
DIRS  = []
FILES = []


# This is where the program kicks off.
def parse():
    global ARGS
    global EXCLUDE_FILES
    global EXCLUDE_DIRS
    global DIRS
    global FILES
    global TODOED

    # We first parse the params passed to the program which allows the user to specify directories to search/avoid and similarly with file types.
    parse_args()

    # Get the current working directory so we can use relative paths.
    cwd = os.getcwd()

    # Apply a bit of manipulation to allow user to specify current directory (relative root dir).
    DIRS = [cwd + d if d != "." else cwd for d in DIRS]
    DIRS = [d.replace('\\', '/') for d in DIRS]

    # Now traverse whole tree.
    for path, dirs, files in os.walk(cwd):
        for name in files:
            f = os.path.join(path, name)
            f = f.replace('\\', '/')

            # Boolean storing the value of whether or this file is valid based on the params the user provided.
            proceed = True

            # TODO Can speed these checks up, once false, we can break immediately.
            # First check if valid filetype.
            if EXCLUDE_FILES:
                proceed = proceed and not any(f.endswith(x) for x in FILES)
            else:
                proceed = proceed and any(f.endswith(x) for x in FILES)

            # Now check if in valid directory.
            # TODO This needs rewriting as '.' allows all files through, not just direct children as we'd like. I think this may just be an issue specific to '.'.
            if EXCLUDE_DIRS:
                proceed = proceed and not any(f.startswith(x) for x in DIRS)
            else:
                proceed = proceed and any(f.startswith(x) for x in DIRS)

            # Only search the file for a todo comment if it is a valid file.
            if proceed:
                # TODO Improve the error handling here.
                try:
                    content = [line.rstrip('\n').rstrip('\r') for line in codecs.open(f, 'r', encoding='utf-8')]
                except:
                    content = []
                    pass

                # If a todo exists we continue.
                if len([x for x in content if "TODO" in x]) > 0:
                    # Print out filename.
                    print("\n### " + f + " ###")

                    # Now we find the todos and print them out.
                    for i in range (0, len(content)):
                        line = content[i]

                        if "TODO" in line:
                            index = len(line.split("TODO")[0])
                            comment = line[index + 4:].strip()

                            # Try and print line above and below as well as line.
                            if i < len(content) - 1 and i > 0:
                                print("\n    TODO " + comment + "\n")
                                print("    " + str(i) + " " + content[i - 1])
                                print("  > " + str(i + 1) + " " + line)
                                print("    " + str(i + 2) + " " + content[i + 1] + "\n")
                            # Try to print line below and line.
                            elif i > 0:
                                print("\n    TODO " + comment + "\n")
                                print("    " + str(i) + " " + content[i - 1])
                                print("  > " + str(i + 1) + " " + line + "\n")
                            # Try to print line above and line.
                            elif i < len(content) - 1:
                                print("\n    TODO " + comment + "\n")
                                print("  > " + str(i + 1) + " " + line)
                                print("    " + str(i + 2) + " " + content[i + 1] + "\n")
                            # Otherwise we simpyl print the line.
                            else:
                                print("\n    TODO " + comment + "\n")
                                print("  > " + str(i + 1) + " " + line + "\n")
                    
                    print("\n")


# Parses the command line args and updates the global vars accordingly.
def parse_args():
    global ARGS
    global EXCLUDE_FILES
    global EXCLUDE_DIRS
    global DIRS
    global FILES

    d_index = -1
    f_index = -1

    # Try and find indices of the params.
    if "+d" in ARGS:
        d_index = ARGS.index("+d")
        EXCLUDE_DIRS = False
    if "-d" in ARGS:
        d_index = ARGS.index("-d")

    if "+f" in ARGS:
        f_index = ARGS.index("+f")
        EXCLUDE_FILES = False
    if "-f" in ARGS:
        f_index = ARGS.index("-f")

    # Once indices found/not found we then extract the relavent info for each param.
    if d_index != -1 and f_index == -1:
        DIRS = ARGS[d_index+1:]
    elif d_index == -1 and f_index != -1:
        FILES = ARGS[f_index+1:]
    elif d_index != -1 and f_index != -1:
        if d_index < f_index:
            DIRS = ARGS[d_index+1:f_index]
            FILES = ARGS[f_index+1:]
        else:
            FILES = ARGS[f_index+1:d_index]
            DIRS = ARGS[d_index+1:]

# Call the main parse function.
parse()
