import os
import logging
from logging.handlers import SysLogHandler

'''Delcare Constants'''
SYSLOG_SVR_IP = '10.0.0.5'
SYSLOG_SVR_PORT =514
FILE_NAME = 'audit.log'
SERVER_NAME = 'OSXTEST1'
STATE_FILE = '.state'

'''Return a list of log file lines read'''
def read_log_file(file_path):
    if not os.path.exists(file_path):
        print_error(f"Error: The file {file_path} does not exist.")
        return
    try:
        with open(file_path, 'r') as file:
            data = [line for line in file if line.strip()]
        return data
    except Exception as e:
        print_error(f"An error occurred while reading the file: {e}")
        return
    
'''Create a state file if the file does not exist'''
def create_state_file():
    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, "w") as f:
            print_ok("State file created!")
            pass
'''Read the current state of the file and store it in a dictionary'''
def read_state():
    state = {};
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            for line in f:
                parts = line.strip().split(":")
                if len(parts) == 2:
                   file_name, last_rows_read = parts
                   state[file_name] = int(last_rows_read)
    return state

'''Updates the state file with the last rows read'''
def update_state(file_name, last_rows_read):
    state = read_state()
    state[file_name] = last_rows_read
    with open(STATE_FILE, "w") as f:
        for file, rows in state.items():
            f.write(f"{file}:{rows}\n")

def set_up_logging():
    try:
        sysloghandler = SysLogHandler(address=(SYSLOG_SVR_IP, SYSLOG_SVR_PORT))
        logger = logging.getLogger()
        logger.addHandler(sysloghandler)
        logger.setLevel(logging.INFO)
        return logger
    
    except Exception as e:
        print_error(f"An Error Occured: {e}")

def send_data_to_syslog_server():
    logger = set_up_logging()
    log_file = read_log_file(FILE_NAME)

    if isinstance(log_file, str):
        print(log_file)
        return
    
    state = read_state()
    last_rows_read = state.get(FILE_NAME, 0)
    new_lines = log_file[last_rows_read:]

    for line in new_lines:
        log_message = f"{SERVER_NAME}: {line.strip()}"
        print_ok(log_message)
        logger.info(log_message)
    
    update_state(FILE_NAME, len(log_file))

def print_error(input_str):
    print("\033[1;31;40m" + input_str + "\033[0m")

def print_ok(input_str):
    print("\033[1;32;40m" + input_str + "\033[0m")

def main():
    create_state_file()
    send_data_to_syslog_server()

if __name__ == "__main__":
    main()