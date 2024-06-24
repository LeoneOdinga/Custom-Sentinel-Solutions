import getpass
import oracledb
import logging
from ping3 import ping
import os
from data_inputs import *
from logging.handlers import SysLogHandler

def setup_logging():
    """Configure logging to send logs to the syslog server."""
    try:
        sysloghandler = SysLogHandler(address=(SYSLOG_SVR_IP, SYSLOG_SVR_PORT))
        logger = logging.getLogger()
        logger.addHandler(sysloghandler)
        logger.setLevel(logging.INFO)
        return logger
    except Exception as e:
        print_error(f"An Error Occured: {e}")

def connect_to_oracle(username, password, dsn):
    """Connect to the Oracle database."""
    try:
        connection = oracledb.connect(user=username, password=password, dsn=dsn)
        print_ok("Connected to Oracle database!")
        return connection
    except Exception as e:
        print_error(f"An Error Ocurred: {e}")
        raise

def execute_query(cursor, sql_query):
    """Execute SQL query and return results."""
    try:
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        raise

'''Create a state file if the file does not exist'''
def create_state_file():
    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, "w") as f:
            print_ok("State file created!")
            pass

'''Create a tables file if the file does not exist'''
def create_table_file():
    if not os.path.exists(TABLES_FILE):
        with open(TABLES_FILE, "w") as f:
            print_ok("Tables file created!")
            pass

'''Read the current state of the file and store it in a dictionary'''
def read_state():
    state = {};
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            for line in f:
                parts = line.strip().split(":")
                if len(parts) == 2:
                   table_name, last_rows_read = parts
                   state[table_name] = int(last_rows_read)
    return state

'''Updates the state file with the last rows read'''
def update_state(table_name, last_rows_read):
    state = read_state()
    state[table_name] = last_rows_read
    with open(STATE_FILE, "w") as f:
        for table, rows in state.items():
            f.write(f"{table}:{rows}\n")

'''Returns a list of oracle table names defined in the tables file'''
def list_of_oracle_tables():
    try:
        with open(TABLES_FILE, 'r') as file:
            lines = file.readlines()
            return [line.strip() for line in lines]
    except FileNotFoundError:
        print_error(f"File Not Found!")
        return []
    
'''Test Connectivity to the syslog server before sending the logs'''
def syslog_isAlive(syslog_svr_ip):
    try:
        ping_result = ping(syslog_svr_ip, timeout=3)
        if isinstance(ping_result, float):
            return True 
        elif ping_result is False:
            return False  
        else:
            return False
    except Exception as e:
        print_error(f"An Error Ocurred: {e}")
        return False

def print_error(input_str):
    '''
    Print given text in red color for Error text
    :param input_str:
    '''
    print("\033[1;31;40m" + input_str + "\033[0m")


def print_ok(input_str):
    '''
    Print given text in green color for Ok text
    :param input_str:
    '''
    print("\033[1;32;40m" + input_str + "\033[0m")


def print_warning(input_str):
    '''
    Print given text in yellow color for warning text
    :param input_str:
    '''
    print("\033[1;33;40m" + input_str + "\033[0m")


def print_notice(input_str):
    '''
    Print given text in white background
    :param input_str:
    '''
    print("\033[0;30;47m" + input_str + "\033[0m")

'''Returns false if certain fields have not have values in data_inputs.py file and updates them with the correct values'''
def missing_data_inputs():
    verdict = True
    data_inputs_file_path = 'data_inputs.py'
    data_inputs =''
    with open(data_inputs_file_path,'r') as f:
        data_inputs = f.read()

    if ORACLE_USERNAME == '':
        verdict = False
        print("Please Enter Oracle username: ")
        username = input().strip()
        data_inputs = data_inputs.replace("ORACLE_USERNAME = ''", f"ORACLE_USERNAME = '{username}'")

    if ORACLE_HOSTNAME == '':
        verdict = False
        print("Please enter Oracle Hostname: ")
        hostname = input().strip()
        data_inputs = data_inputs.replace("ORACLE_HOSTNAME = ''", f"ORACLE_HOSTNAME = '{hostname}'")
    
    if ORACLE_SERVICE_NAME == '':
        verdict = False
        print("Pleae Enter Oracle Service Name: ")
        service_name = input().strip()
        data_inputs = data_inputs.replace("ORACLE_SERVICE_NAME = ''", f"ORACLE_SERVICE_NAME = '{service_name}'")
    
    if SYSLOG_SVR_IP == '':
        verdict = False
        print('Please Enter Syslog Server IP address: ')
        syslog_ip = input().strip()
        data_inputs = data_inputs.replace("SYSLOG_SVR_IP = ''", f"SYSLOG_SVR_IP = '{syslog_ip}'")
    
    with open(data_inputs_file_path, 'w') as f:
        f.write(data_inputs)
        print_ok("Script has been updated with the required constants!")

    return verdict

def main():

    # check if the data_inputs file contain missing values
    if not missing_data_inputs():
        missing_data_inputs()

    # Set up logging to syslog server
    if syslog_isAlive(SYSLOG_SVR_IP):
        logger = setup_logging()
        print_ok("Logging Setup Complete!")

    # Create a state file if the file does not exist
    create_state_file()

    #create a table file if the file does not exist
    create_table_file()

    # Define the list of oracle database tables to target
    oracle_database_tables = list_of_oracle_tables()
    
    # Read the state for the tables
    state = read_state()

    # Prompt the user for the Oracle DB password
    ORACLE_PASSWORD = getpass.getpass("Enter Oracle DB Password: ")

    try:

        # Connect to Oracle database
        connection = connect_to_oracle(ORACLE_USERNAME, ORACLE_PASSWORD, ORACLE_DSN)

        # Create a cursor object
        cursor = connection.cursor()

        # For each table name, run the sql query and send the results to syslog

        for table in oracle_database_tables:
            # Test connectivity to Syslog server before sending logs
            if not syslog_isAlive(SYSLOG_SVR_IP):
                print_error("Cannot connect to the syslog server. Make sure the Syslog Server is running!")
                break

            if table != "":
                # Define the SQL query and offset query results with last rows read
                last_rows_read = state.get(table,0)
                sql_query = f"SELECT * FROM {table} OFFSET {last_rows_read} ROWS"
                #Execute the query
                rows = execute_query(cursor,sql_query)

                if not rows:
                    print_ok(f"No Data Read For Table: {table}")
                    print_notice(f"Total Rows Sent to Syslog: {last_rows_read}")
                
                #Print and send each row data to syslog server
                for row in rows:
                    #tag each row data with the table name
                    print_ok(f"SUCCESSFULLY SENT {row} FROM TABLE: {table}")
                    logger.info(f"{table}: {row}")

                #update the state file with the new state data
                update_state(table, last_rows_read+len(rows))
            else:
                print_error("No Oracle Tables Defined!")
                break

    except Exception as e:
        print_error(f"An error occured: {e}")

    finally:
        # Close the cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    main()