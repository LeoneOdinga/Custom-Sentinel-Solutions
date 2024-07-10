import json
import re

def read_log_file(file_path):
    """Reads the log file and captures all its data."""
    with open(file_path, 'r') as file:
        data = file.readlines()
    return data

def extract_features(log_data):
    """Extracts features and their values from log data."""
    log_entry = log_data[0].strip()  # Assuming the log file contains one log entry per line
    log_dict = {}

    # Extract TID, Timestamp, Unique Log Entry Identifier, and Log Level
    match = re.match(r"TID: \[(.*?)\] \[(.*?)\] \[(.*?)\] (INFO|DEBUG|ERROR|WARNING) \{(.*?)\} - Initiator : (.*?) \| Action: (.*?) \| Target : (.*?) \| Data : (.*?) \| Result : (.*?)", log_entry)
    if match:
        log_dict['TID'] = match.group(1)
        log_dict['Timestamp'] = match.group(2)
        log_dict['Unique Log Entry Identifier'] = match.group(3)
        log_dict['Log Level'] = match.group(4)
        log_dict['Log Category'] = match.group(5)
        log_dict['Initiator'] = match.group(6)
        log_dict['Action'] = match.group(7)
        log_dict['Target'] = match.group(8)
        
        # Extract Data as JSON
        data_json = match.group(9)
        data_dict = json.loads(data_json)
        log_dict.update(data_dict)
        
        log_dict['Result'] = match.group(10)

    return log_dict

def main():
    log_file_path = 'audit.log'  # Assuming the file is in the same directory
    log_data = read_log_file(log_file_path)
    log_dict = extract_features(log_data)
    print(json.dumps(log_dict, indent=4))

if __name__ == "__main__":
    main()
