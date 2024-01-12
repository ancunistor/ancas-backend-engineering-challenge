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

def print_average(running_time : datetime, translation_running_list : deque, average_data : dict):
    if (not translation_running_list):
        #the queue is empty, print average = 0
        print("{\"date\": \"" + running_time.strftime("%Y-%m-%d %H:%M:%S.%f") + "\", \"average_delivery_time\": 0}")
    else:
        #calculate the oldest time for the translations to be added to the average
        oldest_date = running_time - timedelta(minutes=average_data["window"])

        
        oldest_translation_item = translation_running_list[0]
        oldest_timestamp = datetime.strptime(oldest_translation_item["timestamp"], '%Y-%m-%d %H:%M:%S.%f')
        oldest_duration = int(oldest_translation_item["duration"])

        #remove all too old translations from the list
        #subtract the duration value from the sum
        #update number of items to calculate the average for
        while (oldest_timestamp < oldest_date):
            translation_running_list.popleft()
            average_data["sum"] = average_data["sum"] - oldest_duration
            average_data["items"] = average_data["items"] - 1
            if (not translation_running_list):
                #list is empty
                break
            oldest_translation_item = translation_running_list[0]
            oldest_timestamp = datetime.strptime(oldest_translation_item["timestamp"], '%Y-%m-%d %H:%M:%S.%f')
            oldest_duration = int(oldest_translation_item["duration"])

        if (translation_running_list):
            #the list has items, calculate and display the average
            average_delivery_time = average_data["sum"] / average_data["items"]
            print("{\"date\": \"" + running_time.strftime("%Y-%m-%d %H:%M:%S.%f") + "\", \"average_delivery_time\": " + str(average_delivery_time) + "}")
        else:
            #the list is empty, print average = 0
            print("{\"date\": \"" + running_time.strftime("%Y-%m-%d %H:%M:%S.%f") + "\", \"average_delivery_time\": 0}")
            
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

    #initialize linked list which contains last --window-size number minutes' translation delivered items
    translation_running_list = collections.deque()

    #initialize data for calculating the average
    average_data = {'sum' : 0, 'items' : 0, 'window' : window_size}

    if (translation_delivered_timestamp == running_time):
        #add translation delivered item to list and print it
        #add duration to sum and increase number of items, for average calculation

        translation_running_list.append(translation_delivered)
        average_data["sum"] = int(translation_delivered["duration"])
        average_data["items"] = 1
        print_average(running_time, translation_running_list, average_data)
    else :
        #print with 0 average and add translation delivered item to list
        #add duration to sum and increase number of items, for average calculation

        print_average(running_time, translation_running_list, average_data)
        translation_running_list.append(translation_delivered)
        average_data["sum"] = int(translation_delivered["duration"])
        average_data["items"] = 1

    #increase the running time by one minute
    running_time = running_time + timedelta(minutes=1)

    #continue to read the file, line by line
    while True:
        current_line = input_file.readline()
        
        if not current_line:
            break

        translation_delivered = json.loads(current_line)

        translation_delivered_timestamp = datetime.strptime(translation_delivered["timestamp"], '%Y-%m-%d %H:%M:%S.%f')

        while (translation_delivered_timestamp >= running_time):
            print_average(running_time, translation_running_list, average_data)
            running_time = running_time + timedelta(minutes=1)

        translation_running_list.append(translation_delivered)
        average_data["sum"] = average_data["sum"] + int(translation_delivered["duration"])
        average_data["items"] = average_data["items"] + 1

    input_file.close()

    print_average(running_time, translation_running_list, average_data)
