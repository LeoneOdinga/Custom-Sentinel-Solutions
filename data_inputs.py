#CONSTANTS
SYSLOG_SVR_IP = "10.0.0.5" # define the syslog server IP address
SYSLOG_SVR_PORT = 514    # define the syslog server port 
STATE_FILE = '.state'    # this is the name of the state file that would keep track of the last sent logs to sentinel

# ORACLE DATABASE DETAILS
ORACLE_USERNAME = "script"
ORACLE_DSN = "oracle-db:1521/oratest1"

# ORACLE TABLE NAMES
table_name = "SYS.ORG"   # for Multiple table names, we would need to store them in a list and update the driver code. This would be done during the scaling phase of the project

