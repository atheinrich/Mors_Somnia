import os
import glob
import datetime

# Path to the folder containing the .py files
folder_path = 'Archive2'  # Replace this with your actual folder path

# List all Python files in the folder
py_files = glob.glob(os.path.join(folder_path, '*.py'))

# Dictionary to store the file line count and modified date
file_info = {}

# Iterate through each .py file
for file in py_files:
    if os.path.isfile(file):  # Ensure it's a file
        
        # Get the 'Date modified'
        mod_time = os.path.getmtime(file)  # Modification time (Unix timestamp)
        mod_date = datetime.datetime.fromtimestamp(mod_time)  # Convert to readable date
        
        # Format date to 'dd-mm-yyyy'
        formatted_date = mod_date.strftime('%m-%d-%Y')
        
        # Count the lines of code
        with open(file, 'r', encoding='utf-8') as f:
            line_count = sum(1 for line in f if line.strip())  # Count non-empty lines
        
        # Store file info
        file_info[os.path.basename(file)] = (line_count, formatted_date)

# Output to text file
output_file_path = os.path.join(folder_path, 'file_info.txt')
with open(output_file_path, 'w', encoding='utf-8') as f:
    for filename, (line_count, mod_date) in file_info.items():
        f.write(f'{mod_date}\t{line_count}\n')

print(f'File information has been saved to {output_file_path}')
