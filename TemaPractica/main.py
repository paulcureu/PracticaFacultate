import collections
import re
import sys
import time

# Reconfigure stdout to handle UTF-8 encoding for printing special characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def read_words(file_path, is_dex=False):
    """Reads words from a file, handling different formats."""
    words = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip().lower()
                if not line:
                    continue
                
                if is_dex:
                    if line.startswith('>') or line.startswith('<'):
                        line = line[1:].strip()
                    if line:
                        words.append(line)
                else:  # Handles both old and new format for cuvinte_de_verificat.txt
                    if ';' in line:
                        parts = line.split(';')
                        if len(parts) == 3:
                            word = parts[2].strip()
                            if word:
                                words.append(word)
                    else:
                        words.append(line)
        return words
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return []

def is_valid_word(word):
    """Check if a word contains only Romanian alphabet characters or hyphens."""
    return bool(re.match(r'^[a-zăâîșț-]+$', word))


def get_letter_frequencies(words):
    """Calculates the frequency of each letter in a list of words."""
    letter_pattern = re.compile(r'[a-zăâîșț]')
    frequencies = collections.defaultdict(int)
    for word in words:
        for letter in set(letter_pattern.findall(word)):
            frequencies[letter] += 1
    return frequencies

def solve_hangman(secret_word, dictionary):
    """
    Solves a Hangman puzzle and returns the number of guesses and success status.
    Returns: (number_of_guesses, was_successful)
    """
    word_len = len(secret_word)
    
    possible_words = [word for word in dictionary if len(word) == word_len and is_valid_word(word)]

    if not possible_words:
        return 0, False

    guessed_letters = set()
    incorrect_letters = set()
    max_incorrect_guesses = 6
    
    display_word = ['_' if c != '-' else '-' for c in secret_word]

    while '_' in display_word and len(incorrect_letters) < max_incorrect_guesses:
        if not possible_words:
            break

        frequencies = get_letter_frequencies(possible_words)
        
        guess = ''
        sorted_freq = sorted(frequencies.items(), key=lambda x: (-x[1], x[0]))

        for letter, freq in sorted_freq:
            if letter not in guessed_letters:
                guess = letter
                break
        
        if not guess:
            break
        
        guessed_letters.add(guess)

        if guess in secret_word:
            for i, letter in enumerate(secret_word):
                if letter == guess:
                    display_word[i] = guess
        else:
            incorrect_letters.add(guess)

        # Refine the list of possible words
        temp_possible_words = []
        for word in possible_words:
            match = True
            if any(incorrect_letter in word for incorrect_letter in incorrect_letters):
                match = False
            
            if match:
                for i in range(word_len):
                    if display_word[i] != '_' and display_word[i] != word[i]:
                        match = False
                        break

            if match:
                temp_possible_words.append(word)
        
        possible_words = temp_possible_words

    was_successful = '_' not in display_word
    return len(guessed_letters), was_successful

def main():
    """
    Main function to run the Hangman solver and report statistics.
    """
    words_to_guess = read_words('cuvinte_de_verificat.txt')
    dictionary = read_words('dex.txt', is_dex=True)

    if not words_to_guess or not dictionary:
        print("Could not proceed. Please check for previous error messages.")
        return

    for word in words_to_guess:
        if word not in dictionary:
            dictionary.append(word)

    start_time = time.time()
    total_guesses = 0
    successful_solves = 0
    num_words = len(words_to_guess)

    for word in words_to_guess:
        guesses, was_successful = solve_hangman(word, dictionary)
        total_guesses += guesses
        if was_successful:
            successful_solves += 1
    
    end_time = time.time()
    total_time = end_time - start_time
    average_time = total_time / num_words if num_words > 0 else 0

    print(f"Timp total pentru a încerca rezolvarea a {num_words} de cuvinte: {total_time:.2f} secunde.")
    print(f"Media de timp per cuvânt: {average_time:.4f} secunde.")
    print(f"Numărul total de litere încercate: {total_guesses}.")
    print(f"Cuvinte ghicite cu succes: {successful_solves}/{num_words}.")

if __name__ == "__main__":
    main()