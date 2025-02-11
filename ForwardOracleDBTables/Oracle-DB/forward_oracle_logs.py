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

'''Create a db_structure json file if it does not exist'''
def create_db_structure_file():
    if not os.path.exists(DB_STRUCTURE_FILE):
        with open(DB_STRUCTURE_FILE, "w") as f:
            print_ok("DB Json file created!")

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

def main():

    # Set up logging to syslog server
    if syslog_isAlive(SYSLOG_SVR_IP):
        logger = setup_logging()
        print_ok("Logging Setup Complete!")
    else:
        print("Cannot communicate with the syslog server. Check your network connection or make sure you are running the script with root privileges...")
        exit()	

    # Create a state file if the file does not exist
    create_state_file()
    
  
    create_db_structure_file()

    
    # Read the state for the tables
    state = read_state()

    # Prompt the user for the Oracle DB password
    ORACLE_PASSWORD = getpass.getpass("Enter Oracle DB Password: ")

    try:

        # Connect to Oracle database
        connection = connect_to_oracle(ORACLE_USERNAME, ORACLE_PASSWORD, ORACLE_DSN)

        # Create a cursor object
        cursor = connection.cursor()

        columns_to_select = []
        
        list_of_instances = get_instance_list(data)
         
        for instance in list_of_instances:
            instance_tables = get_instance_tables(data,instance)
            for table_name, columns in instance_tables.items():
                table = table_name
                columns_to_select = columns
                # Main Logic goes here
                if table != "":
                # Define the SQL query and offset query results with last rows read
                    last_rows_read = state.get(table,0)
                    sql_query = f"SELECT {', '.join(columns_to_select)} FROM {table}"

                    total_rows = execute_query(cursor,sql_query)
                    count_total_rows = len(total_rows)

                if count_total_rows < last_rows_read:
                    last_rows_read = 0
                    # print and send each row data to syslog server
                    for row in total_rows:
                        #tag each row data with the table name
                        print_ok(f"SUCCESSFULLY SENT {row} FROM TABLE: {table}")
                        logger.info(f"{table}: {row}")

                    update_state(table, last_rows_read+len(total_rows))

                elif count_total_rows > last_rows_read:
                    sql_query_offset = f"SELECT {', '.join(columns_to_select)} FROM {table} OFFSET {last_rows_read} ROWS"
                    #Execute the query
                    rows = execute_query(cursor,sql_query_offset)
                    #print and send each row data to syslog server
                    for row in rows:
                        #tag each row data with the table name
                        print_ok(f"SUCCESSFULLY SENT {row} FROM TABLE: {table}")
                        logger.info(f"{table}: {row}")
                    
                    update_state(table, last_rows_read+len(rows))
                else:
                    print_ok(f"No Data Read For Table: {table}")
                    print_notice(f"Total Rows Sent to Syslog: {last_rows_read}") 

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
