# called on swell data after using `reduce_time.py`
# gets rid of extraneous swell data that the ooi data doesn't cover
import sys


swell_file = sys.argv[1]
other_file = sys.argv[2] # ooi data
output_file = sys.argv[3]


sp = 0  # swell pointer

with open(swell_file, "r") as swellfile, open(other_file, "r") as otherfile, open(output_file, "w") as outfile:
    swell_data = swellfile.readlines()
    for line in otherfile:
        if (sp == 0):
            outfile.write(swell_data[0])
            first = False
            sp += 1
            continue
        datetime_other = line[:13]
        while (sp < len(swell_data)):
            datetime_swell = swell_data[sp][:13]
            if (datetime_swell == datetime_other):
                outfile.write(swell_data[sp])
                sp += 1
                break
            else:
                sp += 1
