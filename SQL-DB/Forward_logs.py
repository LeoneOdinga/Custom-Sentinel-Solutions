import pymssql
import logging
import logging.handlers
import socket
import os
import json

# Paths to the configuration files
SERVER_CONFIG_FILE = 'C:\\Users\\Hankkssel\\Documents\\Combined\\Login\\Server_Login.json'

# Directory where the table configuration files are stored
TABLES_CONFIG_DIR = 'C:\\Users\\Hankkssel\\Documents\\Combined\\Tables'

# Syslog server details
syslog_server = '10.0.0.5'
syslog_port = 514  # default syslog port

# State file path in Documents folder
STATE_FILE = os.path.join(os.path.expanduser('~'), 'Documents', 'SQL101')

# Function to load server configurations from a JSON file
def load_server_configs():
    with open(SERVER_CONFIG_FILE, 'r') as f:
        return json.load(f)

# Function to load table configurations from text files
def load_table_configs():
    table_configs = []
    for config in load_server_configs():
        server_name = config['server']
        table_config_file = os.path.join(TABLES_CONFIG_DIR, f"{server_name.lower().replace('-', '_')}.txt")
        with open(table_config_file, 'r') as f:
            for line in f:
                db_name, table_name = line.strip().split(':')
                table_configs.append({
                    'server': config['server'],
                    'user': config['user'],
                    'password': config['password'],
                    'database': db_name,
                    'table': table_name
                })
    return table_configs

# Function to create a state file if it does not exist
def create_state_file(table_configs):
    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, "w") as f:
            for config in table_configs:
                f.write(f"{config['table']}:0\n")
        print("State file created!")

# Function to read the current state from the file
def read_state():
    state = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            for line in f:
                parts = line.strip().split(":")
                if len(parts) == 2:
                    table_name, last_rows_read = parts
                    state[table_name] = int(last_rows_read)
    return state

# Function to update the state file with the last rows read
def update_state(table_name, last_rows_read):
    state = read_state()
    state[table_name] = last_rows_read
    with open(STATE_FILE, "w") as f:
        for table, rows in state.items():
            f.write(f"{table}:{rows}\n")

# Function to fetch data from the database for a given configuration
def fetch_data_from_db(config):
    try:
        state = read_state()
        last_processed_id = state.get(config['table'], 0)

        connection = pymssql.connect(
            server=config['server'],
            user=config['user'],
            password=config['password'],
            database=config['database']
        )
        cursor = connection.cursor()
        
        cursor.execute(f"SELECT * FROM {config['table']}")
        rows = cursor.fetchall()
        connection.close()
        
        return rows
    except pymssql.Error as e:
        print("Error fetching data:", e)
        return []

# Function to send data to the syslog server
def send_to_syslog(data, config):
    logger = logging.getLogger('SyslogLogger')
    logger.setLevel(logging.INFO)
    syslog_handler = logging.handlers.SysLogHandler(address=(syslog_server, syslog_port))
    formatter = logging.Formatter('%(asctime)s %(message)s')
    syslog_handler.setFormatter(formatter)
    logger.addHandler(syslog_handler)

    # Get the IP address and hostname of the machine
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)

    state = read_state()
    last_rows_read = state.get(config['table'], 0)

    if len(data) > last_rows_read:
        new_data = data[last_rows_read:]
        for row in new_data:
            # Customize the message format to include IP address, hostname, and server name
            message = f"{hostname} ({ip_address}) [{config['server']}] | {config['table']} | " + ' | '.join(map(str, row))
            logger.info(message)
            print(f"{hostname} ({ip_address}) [{config['server']}] | {config['table']} | {row}")
        
        # Update the state with the total number of rows processed
        update_state(config['table'], last_rows_read + len(new_data))
        
        # Print the number of new rows logged
        print(f"{len(new_data)} new rows logged for {config['table']} from {config['server']}.")
    else:
        print(f"No new rows to log for {config['table']} from {config['server']}.")

# Main function
def main():
    server_configs = load_server_configs()
    table_configs = load_table_configs()
    create_state_file(table_configs)
    
    for config in table_configs:
        # Fetch data from the database, skipping already processed rows
        data = fetch_data_from_db(config)
        
        if data:
            send_to_syslog(data, config)

if __name__ == "__main__":
    main()
