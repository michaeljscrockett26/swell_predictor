import sys
import re

input_file = sys.argv[1]

with open(input_file, 'r') as infile:
    for line in infile:
        # Replace the first 4 occurrences of old_char
        line = re.sub(" ", "-", line, count=2)
        line = re.sub(" ", "T", line, count=1)
        line = re.sub(" ", ":", line, count=1)
        line = re.sub(" ", ":00Z,", line, count=1)
        print(line, end="")
