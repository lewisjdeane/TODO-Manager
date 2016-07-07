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

CONTEXT = True
WRITE   = False

# Define global variables which manage whether or not the user is choosing to search/ignore specific filetypes and directories.
EXCLUDE_DIRS  = True
EXCLUDE_FILES = True

# Define global variables to hold the filetypes and directories that should be searched/ignored later in the parse.
DIRS  = []
FILES = []

# Allow user to search a flat hierarchy of specified dirs. I.e. if "." is provided, just search cwd not any subdirs.
FLAT = False

# Define the default symbol that the program should search for.
SYMBOL = "TODO"

VALID = ["--no-context", "--write", "+df", "+d", "-d", "+f", "-f", "-s"]


# This is where the program kicks off.
def parse():
	global ARGS
	global CONTEXT
	global DIRS
	global EXCLUDE_FILES
	global EXCLUDE_DIRS
	global FILES
	global FLAT
	global SYMBOL
	global WRITE


	command = "todo " + " ".join(ARGS) + "\n\n"

	# We first parse the params passed to the program which allows the user to specify directories to search/avoid and similarly with file types.
	parse_args()
	
	# Get the current working directory so we can use relative paths.
	cwd = os.getcwd()

	# Apply a bit of manipulation to allow user to specify current directory (relative root dir).
	DIRS = [cwd + d if d != "." else cwd for d in DIRS]
	DIRS = [d.replace('\\', '/') for d in DIRS]

	output = ""

	# Now traverse whole tree.
	for path, dirs, files in os.walk(cwd):
		for name in files:
			if name != "TODO.mdown":
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
				if EXCLUDE_DIRS:
					proceed = proceed and not any(f.startswith(x) for x in DIRS)
				else:
					if FLAT:
						proceed = proceed and any(x + "/" + name == f for x in DIRS)
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
					if len([x for x in content if SYMBOL in x]) > 0:
						# Print out filename.
						output += "\n### " + f + " ###"

						# Now we find the todos and print them out.
						for i in range (0, len(content)):
							line = content[i]

							if SYMBOL in line:
								index = len(line.split(SYMBOL)[0])
								comment = line[index + len(SYMBOL):].strip()

								output += "\n\n  > " + SYMBOL + " " + comment + "\n\n"
								
								if CONTEXT:
									# Try and print line above and below as well as line.
									if i < len(content) - 1 and i > 0:
										output += "    " + str(i) + " " + content[i - 1] + "\n"
										output += "    " + str(i + 1) + " " + line + "\n"
										output += "    " + str(i + 2) + " " + content[i + 1] + "\n\n"
									# Try to print line below and line.
									elif i > 0:
										output += "    " + str(i) + " " + content[i - 1] + "\n"
										output += "    " + str(i + 1) + " " + line + "\n\n"
									# Try to print line above and line.
									elif i < len(content) - 1:
										output += "    " + str(i + 1) + " " + line + "\n"
										output += "    " + str(i + 2) + " " + content[i + 1] + "\n\n"
									# Otherwise we simpyl print the line.
									else:
										output += "    " + str(i + 1) + " " + line + "\n\n"
						
						output += "\n"

	if WRITE:
		# Write output to a TODO.txt file
		f = open("TODO.mdown", "wb")
		f.write((command + output).encode("utf8"))
		f.close()
	else:
		print(output)


# Parses the command line args and updates the global vars accordingly.
def parse_args():
	global ARGS
	global CONTEXT
	global EXCLUDE_FILES
	global EXCLUDE_DIRS
	global DIRS
	global FILES
	global FLAT
	global VALID
	global WRITE


	# Allow the shorthand notation for searching within the current dir of 'todo .' instead of 'todo +df .'
	if len(ARGS) > 0:
		if ARGS[0] == ".":
			ARGS = ["+df", "."] + ARGS[1:]

	d_index = -1
	f_index = -1

	p = []

	for c in VALID:
		if c in ARGS:
			start = ARGS.index(c)
			if c in ["--no-context", "--write"]:
				p.append((c, []))
			else:
				params = get_params(ARGS[start + 1:])
				p.append((c, params))

	set_args(p)


def get_params(l):
	global VALID

	x = []

	for i in l:
		if i in VALID:
			return x
		else:
			x.append(i)

	return x


def set_args(p):
	global CONTEXT
	global EXCLUDE_FILES
	global EXCLUDE_DIRS
	global DIRS
	global FILES
	global FLAT
	global SYMBOL
	global WRITE

	for x in p:
		if x[0] == "--no-context":
			CONTEXT = False
		if x[0] == "--write":
			WRITE = True
		if x[0] == "+df":
			FLAT = True
			EXCLUDE_DIRS = False
			DIRS = x[1]
		if x[0] == "+d":
			EXCLUDE_DIRS = False
			DIRS = x[1]
		if x[0] == "-d":
			EXCLUDE_DIRS = True
			DIRS = x[1]
		if x[0] == "+f":
			EXCLUDE_FILES = False
			FILES = x[1]
		if x[0] == "-f":
			EXCLUDE_FILES = True
			FILES = x[1]
		if x[0] == "-s":
			SYMBOL = x[1][0]


# Call the main parse function.
parse()
