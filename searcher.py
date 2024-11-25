#!/usr/bin/env python
# Copyright 2024 Jerry Zheng jzheng7@bu.edu
# Copyright 2024 Thomas Kelly kellthom@bu.edu
import sys
import os
import fnmatch
import datetime
import calendar

cmds = sys.argv
mode = ["off", "", "off", "", "off", "", "off", ""]

def parse_arguments(args):
    arg_map = { '-filename_mode': 0,
        '-c': 1,
        '-filetype_mode': 2,
        '-t': 3,
        '-date_mode': 4,
        '-date': 5,
        '-content_mode': 6,
        '-content': 7 }

    # Iterate over the arguments to update the mode array
    for i in range(1, len(args), 2):
        if args[i] in arg_map and i + 1 < len(args):
            mode[arg_map[args[i]]] = args[i + 1]

            # Automatically turn on the mode if the value is provided
            if arg_map[args[i]] % 2 == 1:
                mode[arg_map[args[i]] - 1] = "on"


    # Ensure modes that weren't provided are turned "off"
    for key in [0, 2, 4, 6]:
        if mode[key + 1] == "":  # If the corresponding value is empty
            mode[key] = "off"  # Turn off the mode


#################################################
# Check for name match
def check_name(name, key):
    return fnmatch.fnmatch(name, key)


#################################################

#################################################
# Check for type match
def check_type(file, type):
    return type == os.path.splitext(file)[1]


#################################################

#################################################
# Check for date match
def check_date(file, lower, upper):
    file_time = os.path.getmtime(file)
    return file_time > lower and file_time < upper


#################################################

#################################################
# Check for content match
def check_contents(file, key):
    # Open the file and read all lines
    f = open(file, "r")
    lines = f.readlines()

    # Loop through lines and look for a match
    for line in lines:
        if key in line:
            f.close()
            return 1

    f.close()
    return 0


#################################################

####Todo: process time
#################################################
def process_user_time(time):
    num_slashes = time.count("/")
    num_dashes = time.count("-")

    # Range of Years: yyyy-yyyy
    if num_dashes == 1 and num_slashes == 0:
        year1 = int(time.split("-")[0])
        year2 = int(time.split("-")[1])

        first = datetime.datetime(year1, 1, 1, 0, 0, 0)
        last = datetime.datetime(year2, 12, 31, 23, 59, 59)
        return calendar.timegm(first.timetuple()), calendar.timegm(last.timetuple())

    # Single Year: yyyy
    if num_dashes == 0 and num_slashes == 0:
        first = datetime.datetime(int(time), 1, 1, 0, 0, 0)
        last = datetime.datetime(int(time), 12, 31, 23, 59, 59)
        return calendar.timegm(first.timetuple()), calendar.timegm(last.timetuple())

    # Range of Month and Year: mm/yyyy-mm/yyyy
    if num_dashes == 1 and num_slashes == 2:
        date1 = time.split("-")[0]
        date2 = time.split("-")[1]

        month1 = int(date1.split("/")[0])
        year1 = int(date1.split("/")[1])

        month2 = int(date2.split("/")[0])
        year2 = int(date2.split("/")[1])

        days_in_month = calendar.monthrange(year2, month2)[1]

        first = datetime.datetime(year1, month1, 1, 0, 0, 0)
        last = datetime.datetime(year2, month2, days_in_month, 23, 59, 59)
        return calendar.timegm(first.timetuple()), calendar.timegm(last.timetuple())

    # Single Month and Year: mm/yyyy
    if num_dashes == 0 and num_slashes == 1:
        month = int(time.split("/")[0])
        year = int(time.split("/")[1])

        days_in_month = calendar.monthrange(year, month)[1]

        first = datetime.datetime(year, month, 1, 0, 0, 0)
        last = datetime.datetime(year, month, days_in_month, 23, 59, 59)
        return calendar.timegm(first.timetuple()), calendar.timegm(last.timetuple())

    # Range of dates: mm/dd/yyyy-mm/dd/yyyy
    if num_dashes == 1 and num_slashes == 4:
        date1 = time.split("-")[0]
        date2 = time.split("-")[1]

        month1 = int(date1.split("/")[0])
        day1 = int(date1.split("/")[1])
        year1 = int(date1.split("/")[2])

        month2 = int(date2.split("/")[0])
        day2 = int(date2.split("/")[1])
        year2 = int(date2.split("/")[2])

        first = datetime.datetime(year1, month1, day1, 0, 0, 0)
        last = datetime.datetime(year2, month2, day2, 23, 59, 59)
        return calendar.timegm(first.timetuple()), calendar.timegm(last.timetuple())

    # Single Date: mm/dd/yyyy
    if num_dashes == 0 and num_slashes == 2:
        month = int(time.split("/")[0])
        day = int(time.split("/")[1])
        year = int(time.split("/")[2])

        first = datetime.datetime(year, month, day, 0, 0, 0)
        last = datetime.datetime(year, month, day, 23, 59, 59)
        return calendar.timegm(first.timetuple()), calendar.timegm(last.timetuple())

    return 0, 0


#################################################

if __name__ == '__main__':
    # Parse command line arguments
    if len(sys.argv) > 1:
        parse_arguments(sys.argv)

# Initialize list to store files
file_list = list()

# Walk down directory
for thedir, subdirs, thefiles in os.walk("."):

    # Loop through files
    for file in thefiles:

        # Check name
        name_match = mode[0] == "off" or check_name(thedir + "/" + file, mode[1])

        # Check type
        type_match = mode[2] == "off" or check_type(thedir + "/" + file, mode[3])

        # Check date
        date_match = mode[4] == "off" or check_date(thedir + "/" + file, process_user_time(mode[5])[0],
                                                    process_user_time(mode[5])[1])

        # Check contents
        content_match = mode[6] == "off" or check_contents(thedir + "/" + file, mode[7])

        # If we have a match, add it to the list
        if name_match and type_match and content_match and date_match:
            file_to_add = thedir + "/" + file
            file_list.append(file_to_add)

for elem in file_list:
    print(elem)