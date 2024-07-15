import os

def read_log_file(file_path):
    if not os.path.exists(file_path):
        return f"Error: The file {file_path} does not exist."
    try:
        with open(file_path, 'r') as file:
            data = [line for line in file if line.strip()]
        return data
    except Exception as e:
        return f"An error occurred while reading the file: {e}"

file_path = 'audit.log'
for line in file_path:
        print(line, end='')