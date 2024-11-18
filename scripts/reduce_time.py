# Reduce the csv files to only include every 6 hours.
# Purpose is to try to create some consistency/pattern in the data
# rather than the kind of random collection of times

import sys
import re

input_file = sys.argv[1]
output_file = sys.argv[2]


with open(input_file, "r") as infile, open(output_file, "w") as outfile:
    search_strings = [r"03:[0-9]{2}:[0-9]{2}Z,",
                      r"09:[0-9]{2}:[0-9]{2}Z,",
                      r"15:[0-9]{2}:[0-9]{2}Z,",
                      r"21:[0-9]{2}:[0-9]{2}Z," ]
    # start at 9am
    time_index = 1

    first = True
    for line in infile:
        # write the first line of the file
        if (first):
            outfile.write(line)
            first = False
        # write this line if correct time
        elif bool(re.search(search_strings[time_index], line)):
            outfile.write(line)
            time_index = 0 if time_index == 3 else time_index + 1

