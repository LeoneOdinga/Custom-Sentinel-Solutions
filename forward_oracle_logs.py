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
def read_state(table_name):
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
    state = read_state(table_name)
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

    # Define the list of oracle database tables to target
    oracle_database_tables = list_of_oracle_tables()

    # Define a state dictionary to keep track of the last sent logs for each table
    state = {}

    # Read the state file for each table
    for table in oracle_database_tables:
        if table != "":
            state = read_state(table)
            print(state)
        else:
            print("Cannot fetch the state of the speficied table. Table Missing!")

    # Prompt the user for the Oracle DB password
    ORACLE_PASSWORD = getpass.getpass("Enter Oracle DB Password: ")

    try:
        # Connect to Oracle database
        connection = connect_to_oracle(ORACLE_USERNAME, ORACLE_PASSWORD, ORACLE_DSN)

        # Create a cursor object
        cursor = connection.cursor()

        # For each table name, run the sql query and send the results to syslog

        for table in oracle_database_tables:
            if table != "":
                # Define the SQL query and offset query results with last rows read
                last_rows_read = state.get(table,0)
                sql_query = f"SELECT * FROM {table} OFFSET {last_rows_read} ROWS"
                #Execute the query
                rows = execute_query(cursor,sql_query)
                #Print and send each row data to syslog server
                for row in rows:
                    #tag each row data with the table name
                    print(f"SUCCESSFULLY SENT {row} FROM TABLE: {table}")
                    logger.info(f"{table}: {row}")

                #update the state file with the new state data
                update_state(table, last_rows_read+len(rows))
            else:
                print("No Oracle Tables Defined!")
                break

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