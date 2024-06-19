import getpass
import oracledb
import logging
import os
from data_inputs import *
from logging.handlers import SysLogHandler

def setup_logging():
    """Configure logging to send logs to the syslog server."""
    sysloghandler = SysLogHandler(address=(SYSLOG_SVR_IP, SYSLOG_SVR_PORT))
    logger = logging.getLogger()
    logger.addHandler(sysloghandler)
    logger.setLevel(logging.INFO)
    return logger

def connect_to_oracle(username, password, dsn):
    """Connect to the Oracle database."""
    try:
        connection = oracledb.connect(user=username, password=password, dsn=dsn)
        return connection
    except Exception as e:
        print(f"An Error Ocurred: {e}")
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
            pass

'''Create a tables file if the file does not exist'''
def create_table_file():
    if not os.path.exists(TABLES_FILE):
        with open(TABLES_FILE, "w") as f:
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
        print(f"File Not Found!")
        return []
    
def main():
    # Set up logging

    logger = setup_logging()

    # Create a state file if the file does not exist
    create_state_file()

    #create a table file if the file does not exist
    create_table_file()
    
    # Read the state file
    state = read_state()

    # Prompt the user for the Oracle DB password
    ORACLE_PASSWORD = getpass.getpass("Enter Oracle DB Password: ")

    #Testing... Try printing the list of oracle tables
    for list in list_of_oracle_tables:
        print(list)

    try:
        # Connect to Oracle database
        connection = connect_to_oracle(ORACLE_USERNAME, ORACLE_PASSWORD, ORACLE_DSN)

        # Create a cursor object
        cursor = connection.cursor()

        # Define the SQL query and offset query results with last rows read
        last_rows_read = state.get(table_name, 0)
        sql_query = f"SELECT * FROM {table_name} OFFSET {last_rows_read} ROWS"

        # Execute the SQL query
        rows = execute_query(cursor, sql_query)

        # Print and log each row
        for row in rows:
            #tag each row data with the table name
            print(row)
            logger.info(f"{table_name}: {row}")

        #update the state file with the new state data
        update_state(table_name, last_rows_read+len(rows))

    except Exception as e:
        print(f"An error occured: {e}")

    finally:
        # Close the cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    main()