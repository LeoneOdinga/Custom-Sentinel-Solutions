#CONSTANTS
SYSLOG_SVR_IP = "10.0.0.5" #define the syslog server IP address
SYSLOG_SVR_PORT = 514    #define the syslog server port 
STATE_FILE = '.state'    #state file that keeps track of the last logs sent to sentinel
TABLES_FILE = 'tables.txt' #file to insert the table names you want the script to target

# ORACLE DATABASE DETAILS
ORACLE_USERNAME = "script"
ORACLE_DSN = "oracle-db:1521/oratest1"

# ORACLE TABLE NAMES
table_name = "SYS.ORG" 

