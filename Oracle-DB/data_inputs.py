import os

current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)

#CONSTANTS
SYSLOG_SVR_IP = "10.0.0.5" #define the syslog server IP address
SYSLOG_SVR_PORT = 514    #define the syslog server port 
STATE_FILE = os.path.join(parent_dir,'.state')    #state file that keeps track of the last logs sent to syslog server
TABLES_FILE = os.path.join(parent_dir,'tables.txt') #file to insert the table names you want the script to target

# ORACLE DATABASE DETAILS  
ORACLE_USERNAME = 'script'
ORACLE_HOSTNAME = 'oracle-db'
ORACLE_LISTENER_PORT = 1521
ORACLE_SERVICE_NAME = 'oratest1'

#ORACLE AUDIT TABLE COLUMN NAMES
# List of column names to include in the SQL query
'''
columns_to_select = [
    'AUDIT_TYPE',
    'SESSIONID',
    'PROXY_SESSIONID',
    'OS_USERNAME',
    'USERHOST',
    'TERMINAL',
    'INSTANCE_ID',
    'DBID',
    'AUTHENTICATION_TYPE',
    'DBUSERNAME',
    'EXTERNAL_USERID',
    'GLOBAL_USERID',
    'CLIENT_PROGRAM_NAME',
    'ENTRY_ID',
    'STATEMENT_ID',
    'EVENT_TIMESTAMP',
    'ACTION_NAME',
    'OS_PROCESS',
    'TRANSACTION_ID',
    'SCN',
    'OBJECT_SCHEMA',
    'OBJECT_NAME',
    'SQL_TEXT',
    'SQL_BINDS',
    'SYSTEM_PRIVILEGE_USED',
    'SYSTEM_PRIVILEGE',
    'AUDIT_OPTION',
    'ROLE',
    'TARGET_USER',
    'EXCLUDED_USER',
    'CURRENT_USER',
    'UNIFIED_AUDIT_POLICIES',
    'RLS_INFO'
]
'''
columns_to_select = [
    'JOB_TITLE',
    'DEPARTMENT',
    'MACHINE_NAME',
    'MACHINE_SERIAL_NUMBER', 
]


ORACLE_DSN = f"{ORACLE_HOSTNAME}:{ORACLE_LISTENER_PORT}/{ORACLE_SERVICE_NAME}"
