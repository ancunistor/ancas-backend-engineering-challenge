# Python program which calculates average translation delivery times
# Input: - file with Delivered Translations info
#        - parameter for interval to average (minutes)
# Output: moving average delivery time of all translations for the past *interval to average* given as input

import os
import argparse
import json
from datetime import datetime, timedelta
import collections
from collections import deque

#checks if a file with a given path exists and is not empty
def is_non_zero_file(fpath):  
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0


#prints a minute-by-minute view of the last (maximum) "window_size" minutes of translations delivered
#translation_running_list - list with one entry per minute of: {"sum" : translation_delivered_duration_sum, "items" : number_of_translation_delivered_items}
#average_data - {"sum" : total_translation_delivered_duration_sum, "items" : total_number_of_translation_delivered_items}
#window_size - number of minutes to average delivered translations
#running_time - current minute
def print_average(translation_running_list : deque, average_data : dict, window_size : int, running_time : datetime):
    if (not translation_running_list):
        #the queue is empty, print average = 0
        print("{\"date\": \"" + running_time.strftime("%Y-%m-%d %H:%M:%S.%f") + "\", \"average_delivery_time\": 0}")
    else:
        if (len(translation_running_list) > window_size):
            removed_item = translation_running_list.popleft()
            average_data["sum"] = average_data["sum"] - removed_item["sum"]
            average_data["items"] = average_data["items"] - removed_item["items"]

        if (average_data["sum"] == 0):
            average = 0
        else:
            average = average_data["sum"] / average_data["items"]
            if (average == int(average)):
                average = int(average)
        print("{\"date\": \"" + running_time.strftime("%Y-%m-%d %H:%M:%S.%f") + "\", \"average_delivery_time\": " + str(average) +"}")

#uncomment line 54 to use the project test file
#call to test given sample: python3 average_delivery_time_calculator.py --input_file events.json --window_size 10
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script that accepts an input file name and a window size parameter"
    )
    parser.add_argument("--input_file", required=True, type=str)
    parser.add_argument("--window_size", required=True, type=int)
    args = parser.parse_args()

    input_file_name = args.input_file
    window_size = args.window_size

    #to comment out: used for testing with project test files  
    #input_file_name = os.path.join(os.path.dirname(__file__), "tests/files", input_file_name)

    #test input parameters
    if not is_non_zero_file(input_file_name):
        print("--input file " + input_file_name + " not found or empty")
        raise SystemExit(1)
    
    if window_size <= 0:
        print("window size incorrect, must be > 0")
        raise SystemExit(1)

    #start processing file
    input_file = open(input_file_name, 'r')

    #read first line to get the running_time start time
    current_line = input_file.readline()
    translation_delivered = json.loads(current_line)

    translation_delivered_timestamp = datetime.strptime(translation_delivered["timestamp"], '%Y-%m-%d %H:%M:%S.%f')
    running_time = translation_delivered_timestamp.replace(second=0, microsecond=0)

    #linked list which contains last --window-size number minutes' worth of translation delivered items
    translation_running_list = collections.deque()

    #int for calculating the sum of all the translation durations received per minute
    sum_per_minute = 0

    #int for calculating the number of translation durations received per minute
    number_per_minute = 0

    #data for average calculation
    average_data = {"sum": 0, "items": 0}

    #process first translation_delivered
    if (translation_delivered_timestamp == running_time):
        average_data["sum"] += int(translation_delivered["duration"])
        average_data["items"] += 1
        translation_running_list.append({"sum" : average_data["sum"], "items" : average_data["items"]})
        print_average(translation_running_list, average_data, window_size, running_time)

    else :
        print_average(translation_running_list, average_data, window_size, running_time)
        sum_per_minute += int(translation_delivered["duration"])
        number_per_minute = 1

    #increase the running time by one minute
    running_time = running_time + timedelta(minutes=1)

    #continue to read the file, line by line
    while True:
        current_line = input_file.readline()
        
        if not current_line:
            break

        translation_delivered = json.loads(current_line)

        translation_delivered_timestamp = datetime.strptime(translation_delivered["timestamp"], '%Y-%m-%d %H:%M:%S.%f')

        if (translation_delivered_timestamp == running_time):
            #minute interval complete

            sum_per_minute += int(translation_delivered["duration"])
            number_per_minute += 1

            #add minute interval calculation to list
            translation_running_list.append({"sum" : sum_per_minute, "items" : number_per_minute})

            #print minute average and increase running time
            print_average(translation_running_list, average_data, window_size, running_time)
            running_time = running_time + timedelta(minutes=1)


            average_data["items"] += number_per_minute
            average_data["sum"] += sum_per_minute

            number_per_minute = 0
            sum_per_minute = 0
        else: 
            if (translation_delivered_timestamp > running_time):
                #no translation_delivered events for a while
                #save calculated minute data and prepare for empty entries until translation_delivered_timestamp is reached
                translation_running_list.append({"sum" : sum_per_minute, "items" : number_per_minute})
                average_data["items"] += number_per_minute
                average_data["sum"] += sum_per_minute
                number_per_minute = 0
                sum_per_minute = 0
                running_time = running_time + timedelta(minutes=1)

                print_average(translation_running_list, average_data, window_size, running_time)

                while (translation_delivered_timestamp > running_time):
                    #add empty entries to list for catching up minutes
                    translation_running_list.append({"sum" : 0, "items" : 0})
                    print_average(translation_running_list, average_data, window_size, running_time)
                    running_time = running_time + timedelta(minutes=1)
                
                #caught up
                #adding bigger timestamp to running minute data
                sum_per_minute += int(translation_delivered["duration"])
                number_per_minute += 1
            else:
                #translation_delivered_timestamp < running_time
                #add duration and items to the minute calculations
                sum_per_minute += int(translation_delivered["duration"])
                number_per_minute += 1

    input_file.close()

    #add rest
    translation_running_list.append({"sum" : sum_per_minute, "items" : number_per_minute})
    average_data["items"] += number_per_minute
    average_data["sum"] += sum_per_minute
    print_average(translation_running_list, average_data, window_size, running_time)
