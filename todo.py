# 
# A simple tool to help you easily analayse TODOs spread across a whole project.
# 
# Author(s):     Lewis Deane
# License:       MIT
# Last Modified: 7/6/2016
# 

import os
import codecs

def main():
    cwd = os.getcwd()

    for path, subdirs, files in os.walk(cwd):
        for name in files:
            f = os.path.join(path, name)
            try:
                content = [line.rstrip('\n').rstrip('\r') for line in codecs.open(f, 'r', encoding='utf-8')]
            except:
                pass

            if len([x for x in content if "todo" in x.lower()]) > 0:
                print("\n### " + name + " ###")

                for i in range (0, len(content)):
                    line = content[i]

                    if "todo" in line.lower():
                        index = len(line.lower().split("todo")[0])
                        comment = line[index + 4:].strip()

                        # Try and print line above and below as well as line.
                        if i < len(content) - 1 and i > 0:
                            print("\n    '" + comment + "'\n")
                            print("    " + str(i) + " " + content[i - 1])
                            print("  > " + str(i + 1) + " " + line)
                            print("    " + str(i + 2) + " " + content[i + 1] + "\n")
                        # Try to print line below and line.
                        elif i > 0:
                            print("\n    '" + comment + "'\n")
                            print("    " + str(i) + " " + content[i - 1])
                            print("  > " + str(i + 1) + " " + line + "\n")
                        elif i < len(content) - 1:
                            print("\n    '" + comment + "'\n")
                            print("  > " + str(i + 1) + " " + line)
                            print("    " + str(i + 2) + " " + content[i + 1] + "\n")
                        else:
                            print("\n    '" + comment + "'\n")
                            print("  > " + str(i + 1) + " " + line + "\n")
                
                print("\n")

main()
