import os
import logging
from logging.handlers import SysLogHandler

'''Delcare Constants'''
SYSLOG_SVR_IP = '10.0.0.5'
SYSLOG_SVR_PORT ='514'
FILE_PATH = 'audit.log'
SERVER_NAME = 'OSXTEST1'

'''Return a list of log file lines read'''
def read_log_file(file_path):
    if not os.path.exists(file_path):
        return f"Error: The file {file_path} does not exist."
    try:
        with open(file_path, 'r') as file:
            data = [line for line in file if line.strip()]
        return data
    except Exception as e:
        return f"An error occurred while reading the file: {e}"

def set_up_logging():
    try:
        sysloghandler = SysLogHandler(address=(SYSLOG_SVR_IP, SYSLOG_SVR_PORT))
        logger = logging.getLogger()
        logger.addHandler(sysloghandler)
        logger.setLevel(logging.INFO)
        return logger
    
    except Exception as e:
        print(f"An Error Occured: {e}")

def send_data_to_syslog_server():
    logger = set_up_logging()
    log_file = read_log_file(FILE_PATH)

    if isinstance(log_file, str):
        print(log_file)
        return

    for line in log_file:
        log_message = f"{SERVER_NAME}: {line.strip()}"
        print(log_message)
        logger.info(log_message)

send_data_to_syslog_server()