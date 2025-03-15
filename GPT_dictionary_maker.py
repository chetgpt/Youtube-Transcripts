import tkinter as tk
from tkinter import filedialog
from langdetect import detect
import re
from collections import Counter
from nltk import ngrams

def select_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    return file_path

def detect_language(text):
    try:
        return detect(text)
    except:
        return None

def get_ngrams(text, n=2):
    words = text.split()
    return ngrams(words, n)

def process_file(file_path):
    encodings = ['utf-8', 'latin-1', 'windows-1252']
    content = None

    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                content = file.read()
            break  # If successful, exit the loop
        except UnicodeDecodeError:
            pass  # If an error occurs, try the next encoding

    if content is None:
        print("Failed to read the file with common encodings.")
        return [], Counter(), Counter()

    sentences = re.split(r'(?<=[.!?])\s+', content)
    indonesian_sentences = []
    word_count = Counter()
    bigram_count = Counter()

    for sentence in sentences:
        if detect_language(sentence) == 'en':
            indonesian_sentences.append(sentence)
            word_count.update(sentence.split())
            bigram_count.update(get_ngrams(sentence))

    return indonesian_sentences, word_count, bigram_count

def save_results(indonesian_sentences, word_count, bigram_count):
    with open('indonesian_sentences.txt', 'w', encoding='utf-8') as file:
        file.write('\n'.join(indonesian_sentences))

    with open('indonesian_word_frequency.txt', 'w', encoding='utf-8') as file:
        for word, freq in word_count.most_common():
            file.write(f"{word}: {freq}\n")

    with open('indonesian_bigram_frequency.txt', 'w', encoding='utf-8') as file:
        for bigram, freq in bigram_count.most_common():
            file.write(f"{' '.join(bigram)}: {freq}\n")

    print("Files saved: indonesian_sentences.txt, indonesian_word_frequency.txt, indonesian_bigram_frequency.txt")

def main():
    file_path = select_file()
    if file_path:
        indonesian, word_count, bigram_count = process_file(file_path)
        save_results(indonesian, word_count, bigram_count)
    else:
        print("No file selected")

if __name__ == "__main__":
    main()
