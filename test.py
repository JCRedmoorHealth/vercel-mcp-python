import os
import pandas as pd 
path = 'Board string'  # Ensure this matches the path used in get_board.py
file_path = os.path.join(path, "webinarAttendees.text")
with open(file_path, "r", encoding='utf-8') as file:
    # Read the contents of the file
    result = file.read()

print(result)