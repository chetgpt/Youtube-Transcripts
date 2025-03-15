import os
import tkinter as tk
from tkinter import filedialog

def count_tokens(text):
    """Estimate the number of tokens in the text."""
    return len(text.split())

def get_file_size(file_path):
    """Returns the size of the file in bytes."""
    return os.path.getsize(file_path)

def clean_text(text):
    """Performs basic cleaning of the text."""
    cleaned_text = ''.join(char for char in text if char.isprintable())
    cleaned_text = cleaned_text.lower()
    return cleaned_text

def read_file_with_encoding(file_path):
    """Tries to read a file with various encodings."""
    encodings = ['utf-8', 'iso-8859-1', 'windows-1252']  # Add more if needed
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Unable to decode file {file_path} with provided encodings.")

# Create a Tkinter root window (hidden as we just need the file dialog)
root = tk.Tk()
root.withdraw()  # Hide the main window

# Ask the user to select a folder
directory = filedialog.askdirectory(title="Select Folder Containing .txt Files")

# Check if a directory was selected
if not directory:
    print("No folder selected. Exiting script.")
else:
    # Maximum number of tokens for each combined file
    max_tokens = 500000  

    # File counter for naming the output files
    file_counter = 1

    # List to keep track of combined file details (token count and file size)
    combined_files_info = []

    # Initialize the token count of the current combined file
    current_token_count = 0

    # Start with the first output file
    current_file_path = os.path.join(directory, f'combined_{file_counter}.txt')
    current_file = open(current_file_path, 'w')

    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        # Check if the file is a .txt file
        if filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)

            try:
                # Read, clean, and estimate the number of tokens in this file
                content = clean_text(read_file_with_encoding(file_path))
                file_token_count = count_tokens(content)

                # Check if adding this file would exceed the maximum token limit
                if current_token_count + file_token_count > max_tokens:
                    # Close the current file and record its details
                    current_file.close()
                    combined_files_info.append((current_token_count, get_file_size(current_file_path)))

                    # Start a new combined file
                    file_counter += 1
                    current_file_path = os.path.join(directory, f'combined_{file_counter}.txt')
                    current_file = open(current_file_path, 'w')
                    current_token_count = 0

                # Write the cleaned content to the current combined file
                current_file.write(content + "\n")
                current_token_count += file_token_count

            except ValueError as e:
                print(e)

    # Close the last output file and record its details
    current_file.close()
    combined_files_info.append((current_token_count, get_file_size(current_file_path)))

    # Print the details of each combined file
    for i, (tokens, size) in enumerate(combined_files_info, 1):
        print(f"Combined file {i}: {tokens} tokens, {size} bytes")

    print(f"Completed. Created {file_counter} combined file(s) in '{directory}'.")
