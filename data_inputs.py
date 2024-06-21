#CONSTANTS
SYSLOG_SVR_IP = "10.0.0.5" #define the syslog server IP address
SYSLOG_SVR_PORT = 514    #define the syslog server port 
STATE_FILE = '.state'    #state file that keeps track of the last logs sent to syslog server
TABLES_FILE = 'tables.txt' #file to insert the table names you want the script to target

# ORACLE DATABASE DETAILS  
ORACLE_USERNAME = 'script'
ORACLE_HOSTNAME = 'oracle-db'
ORACLE_LISTENER_PORT = 1521
ORACLE_SERVICE_NAME = 'oratest1'

ORACLE_DSN = f"{ORACLE_HOSTNAME}:{ORACLE_LISTENER_PORT}/{ORACLE_SERVICE_NAME}"