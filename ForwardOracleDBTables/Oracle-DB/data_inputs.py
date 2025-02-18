import os
import json

current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)

#CONSTANTS
SYSLOG_SVR_IP = "10.0.1.4" #define the syslog server IP address
SYSLOG_SVR_PORT = 514    #define the syslog server port 
STATE_FILE = os.path.join(parent_dir,'.state')    #state file that keeps track of the last logs sent to syslog server
TABLES_FILE = os.path.join(parent_dir,'tables.txt') #file to insert the table names you want the script to target
DB_STRUCTURE_FILE = os.path.join(parent_dir, 'db_structure.json') #json file to capture the table names, columns, for each oracle instance. 

# ORACLE DATABASE DETAILS  
ORACLE_USERNAME = 'script'
ORACLE_HOSTNAME = 'oracle-db-1.northeurope.cloudapp.azure.com'
ORACLE_LISTENER_PORT = 1521
ORACLE_SERVICE_NAME = 'oratest1'
ORACLE_DSN = f"{ORACLE_HOSTNAME}:{ORACLE_LISTENER_PORT}/{ORACLE_SERVICE_NAME}"

# Read JSON file
def load_json(filename):
    with open(filename, "r") as file:
        return json.load(file)

# Extract table names and column names
def extract_db_structure(data):
    db_structure = {}
    for instance in data["instances"]:
        instance_name = instance["instanceName"]
        db_structure[instance_name] = {}
        for table in instance["tables"]:
            table_name = table["tableName"]
            db_structure[instance_name][table_name] = table["columns"]
    return db_structure
 

#Store db structure in variable
data = load_json(DB_STRUCTURE_FILE)
db_structure = extract_db_structure(data)

#get list of instances
def get_instance_list(data):
    return [instance["instanceName"] for instance in data["instances"]]

#Get tables and columns for a specific instance
def get_instance_tables(data, instance_name):
    for instance in data["instances"]:
        if instance["instanceName"] == instance_name:
            return {table["tableName"]: table["columns"] for table in instance["tables"]}
    return {} #return empty dict if instance not found

