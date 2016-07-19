# 
# A simple tool to help you easily analayse TODOs spread across a whole project.
# 
# Author(s):     Lewis Deane
# License:       MIT
# Last Modified: 19/7/2016
# 

# TODO Allow user to customise number of lines visible.
# TODO Add a .todoignore file for default things to ignore.
# TODO Find common amount of tabs, and remove the min

import codecs
import sys
import os


# Define global variable ARGS which we then parse.
ARGS = sys.argv[1:]

SHOW_CONTEXT  = True
WRITE_TO_FILE = False

# Define global variables which manage whether or not the user is choosing to
# search/ignore specific filetypes and directories.
EXCLUDE_DIRECTORIES = True
EXCLUDE_FILES       = True

# Define global variables to hold the filetypes and directories that should be
# searched/ignored later in the parse.
DIRECTORY_NAMES = []
FILE_EXTENSIONS = []

# Allow user to search a flat hierarchy of specified dirs.
# I.e. if "." is provided, just search cwd not any subdirs.
USE_FLAT_DIRECTORIES = False

# Specify the filename that should be written to if '--write' present.
OUTPUT_FILE_NAME = "TODO.mdown"

# Define the default symbol that the program should search for.
TRIGGER_SYMBOL = "TODO"

# Valid symbols to be used as params
VALID_ARGS = ["--no-context", "--write", "+df", "+d", "-d", "+f", "-f", "-s"]

# Specify no. of lines above and below the found line to include within context.
NUMBER_OF_LINES_ABOVE_BELOW_TO_TAKE = 1


# This is where the program kicks off.
def parse():
	global ARGS
	global DIRECTORY_NAMES
	global OUTPUT_FILE_NAME
	global TRIGGER_SYMBOL
	global WRITE_TO_FILE

	if ARGS != ["--rewrite"]:
		command = ["todo " + " ".join(ARGS)]
	else:
		command = [read_todo_command()]

	# We first parse the params passed to the program which allows the user to
	# specify directories to search/avoid and similarly with file types.
	parse_args()
	
	# Get the current working directory so we can use relative paths.
	cwd = os.getcwd()
	
	directory_paths = [cwd + directory_name if directory_name != "." else cwd
										 for directory_name in DIRECTORY_NAMES]
	directory_paths = [directory_path.replace('\\', '/')
	                   for directory_path in directory_paths]

	output_lines = []

	# Now traverse whole file tree.
	for path, dirs, files in os.walk(cwd):
		for file_name in files:
			if file_name != OUTPUT_FILE_NAME:
				file_path = os.path.join(path, file_name)
				file_path = file_path.replace('\\', '/')

				# Only search the file for a todo comment if it is a valid file.
				if file_meets_criteria(directory_paths, file_name, file_path):
					lines = []

					try:
						file = codecs.open(file_path, 'r', encoding='utf-8')
						lines = [strip_line(line) for line in file]
					except:
						pass

					if len([line for line in lines
						    if TRIGGER_SYMBOL in line]) > 0:
						output_lines += ["", "### " +
						                     file_path[len(cwd) + 1:] +
						                     " ###"]

						line_count = len(lines)

						for i in range (0, line_count):
							line = lines[i]

							if TRIGGER_SYMBOL in line:
								output_lines += build_output_for_todo(lines, i)

	if WRITE_TO_FILE:
		output_file = open(OUTPUT_FILE_NAME, "wb")
		output_file.write("\n".join((command + output_lines)).encode("utf8"))
		output_file.close()
	else:
		print("\n".join(output_lines))


# Parses the command line args and updates the global vars accordingly.
def parse_args():
	global ARGS
	global VALID_ARGS

	no_params_args = ["--no-context", "--write"]

	# Allow the shorthand notation for searching within the current dir of
	# 'todo .' instead of 'todo +df .'
	if len(ARGS) > 0:
		if ARGS[0] == ".":
			ARGS = ["+df", "."] + ARGS[1:]

	input_args_with_params = []

	for valid_arg in VALID_ARGS:
		if valid_arg in ARGS:
			start_index = ARGS.index(valid_arg)
			if valid_arg in no_params_args:
				input_args_with_params.append((valid_arg, []))
			else:
				params = get_params(ARGS[start_index + 1:])
				input_args_with_params.append((valid_arg, params))

	set_args(input_args_with_params)


def get_params(tokens):
	global VALID_ARGS

	params = []

	for token in tokens:
		if token in VALID_ARGS:
			return params
		else:
			params.append(token)

	return params


def set_args(args_with_params):
	global SHOW_CONTEXT
	global EXCLUDE_FILES
	global EXCLUDE_DIRECTORIES
	global DIRECTORY_NAMES
	global FILE_EXTENSIONS
	global USE_FLAT_DIRECTORIES
	global TRIGGER_SYMBOL
	global WRITE_TO_FILE

	for arg_with_params in args_with_params:
		arg    = arg_with_params[0]
		params = arg_with_params[1]

		if arg == "--no-context":
			SHOW_CONTEXT = False
		if arg == "--write":
			WRITE_TO_FILE = True
		if arg == "+df":
			DIRECTORY_NAMES      = params
			EXCLUDE_DIRECTORIES  = False
			USE_FLAT_DIRECTORIES = True
		if arg == "+d":
			DIRECTORY_NAMES     = params
			EXCLUDE_DIRECTORIES = False
		if arg == "-d":
			DIRECTORY_NAMES     = params
			EXCLUDE_DIRECTORIES = True
		if arg == "+f":
			EXCLUDE_FILES   = False
			FILE_EXTENSIONS = params
		if arg == "-f":
			EXCLUDE_FILES   = True
			FILE_EXTENSIONS = params
		if arg == "-s":
			TRIGGER_SYMBOL = params[0]


def read_todo_command():
	global ARGS

	try:
		file = codecs.open(OUTPUT_FILE_NAME, 'r', encoding='utf-8')
		lines = [strip_line(line) for line in file]
		ARGS = lines[0][5:].split()
		return lines[0]
	except:
		print("Error: Could not find last command.")
		raise


def strip_line(line):
	return line.rstrip('\n').rstrip('\r')


def file_meets_criteria(directory_paths, file_name, file_path):
	global EXCLUDE_DIRECTORIES
	global EXCLUDE_FILES
	global FILE_EXTENSIONS
	global USE_FLAT_DIRECTORIES

	file_ends_in_extension = any(file_path.endswith(extension)
	                           for extension in FILE_EXTENSIONS)

	if EXCLUDE_FILES and file_ends_in_extension:
		return False
	elif not EXCLUDE_FILES and not file_ends_in_extension:
		return False

	file_begins_with_directory_path = any(file_path.startswith(directory_path)
	                                    for directory_path in directory_paths)

	if EXCLUDE_DIRECTORIES and file_begins_with_directory_path:
		return False
	elif not EXCLUDE_DIRECTORIES:
		if not USE_FLAT_DIRECTORIES and not file_begins_with_directory_path:
			return False
		elif (USE_FLAT_DIRECTORIES and
		      not any(is_file_within_directory(directory_path, file_name,
		                                       file_path)
		            for directory_path in directory_paths)):
			return False

	return True


def is_file_within_directory(directory_path, file_name, file_path):
	return directory_path + "/" + file_name == file_path


def build_output_for_todo(lines, index):
	global NUMBER_OF_LINES_ABOVE_BELOW_TO_TAKE
	global TRIGGER_SYMBOL
	global SHOW_CONTEXT

	line = lines[index]

	trigger_index = len(line.split(TRIGGER_SYMBOL)[0])
	comment = line[trigger_index + len(TRIGGER_SYMBOL):].strip()
	
	output_lines = ["", (" " * 3) + "> " + TRIGGER_SYMBOL + " " + comment]
	
	if SHOW_CONTEXT:
		start_index = max(0, index - NUMBER_OF_LINES_ABOVE_BELOW_TO_TAKE)
		end_index   = min(len(lines) - 1, index +
		                                  NUMBER_OF_LINES_ABOVE_BELOW_TO_TAKE)
		
		line_numbers  = list(range(start_index + 1, end_index + 2))
		line_contents = lines[start_index:end_index + 1]

		output_lines += format_lines(line_numbers, line_contents)

	return output_lines


def format_lines(line_numbers, line_contents):
	max_line_number_length = max([len(str(line_number))
	                              for line_number in line_numbers])

	output_lines = [""]

	for i in range(0, len(line_numbers)):
		line_number  = str(line_numbers[i])
		line_content = line_contents[i]

		extra_spaces_needed = max_line_number_length - len(line_number)

		output_lines += [format_line(line_number, line_content,
		                             extra_spaces_needed)]

	output_lines += [""]

	return output_lines


def format_line(line_number, line_content, extra_spaces):
	spaces = (extra_spaces + 2) * " "
	return (" " * 10) + line_number + spaces + line_content


# Call the main parse function.
parse()
