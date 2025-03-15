import re
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import os
from tqdm import tqdm
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

def read_file(file_path):
    """
    Tries to read a file with different encodings.
    """
    encodings = ['utf-8', 'latin-1', 'ISO-8859-1']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Unable to read the file with the provided encodings: {encodings}")

def process_indonesian_text():
    """
    Processes Indonesian text from the selected file.
    """
    # Set up the root Tkinter window
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Open file dialog to choose a file
    file_path = filedialog.askopenfilename()
    if not file_path:
        print("No file selected. Exiting.")
        return

    print("Reading file...")

    # Read the file with different encodings
    try:
        text = read_file(file_path)
    except ValueError as e:
        print(e)
        return

    print("Processing text...")

    # Initialize a progress bar
    pbar = tqdm(total=100)

    # Initialize the Indonesian stemmer
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()

    # Stemming the text
    stemmed_text = stemmer.stem(text)

    # Update progress bar
    pbar.update(50)

    # Add punctuation (if needed)
    corrected_text_with_punctuation = re.sub(r"([a-zA-Z])(\n)", r"\1.\n", stemmed_text)

    # Format for clarity
    formatted_text = re.sub(r"(\n)", r"\n- ", corrected_text_with_punctuation)

    # Create an index or table of contents
    lines = formatted_text.split('\n')
    toc = "Table of Contents\n"
    for i, line in enumerate(lines):
        if line.strip() and i < 50:  # Limiting TOC to first 50 lines for simplicity
            toc += f"{i+1}. {line[:30]}{'...' if len(line) > 30 else ''}\n"

    final_text = toc + "\n\n" + formatted_text

    # Update progress bar
    pbar.update(50)

    # Set the output file path (in the same directory as the input file)
    directory, _ = os.path.split(file_path)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file_path = os.path.join(directory, f"processed_text_{timestamp}.txt")

    # Save the output to the new file
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(final_text)

    # Complete the progress bar
    pbar.close()

    print(f"Processed text saved to {output_file_path}")

process_indonesian_text()
