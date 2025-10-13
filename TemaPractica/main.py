import random
from collections import Counter
import time
import sys
import codecs

# Force stdout to use UTF-8 encoding to prevent errors on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def get_guesser_dictionary():
    """Reads all words from the large dictionary file for the guesser."""
    try:
        with open('lista-cuvinte-ale-limbii-romane.txt', 'r', encoding='utf-8') as file:
            content = file.read()
        
        content = content.replace('þ', 'ț').replace('º', 'ș').replace('ã', 'ă')
        words = [word.lower() for word in content.split() if word.isalpha()]
        return words
    except FileNotFoundError:
        print("Eroare: Fișierul 'lista-cuvinte-ale-limbii-romane.txt' nu a fost găsit.")
        return []

def get_secret_word_data():
    """Reads the secret words and their initial patterns from the verification file."""
    secret_data = []
    try:
        with open('cuvinte_de_verificat.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
        for line in lines:
            parts = line.strip().split(';')
            if len(parts) == 3:
                word = parts[2].lower()
                pattern = parts[1].lower().replace('*', '_')
                secret_data.append((word, pattern))
        return secret_data
    except FileNotFoundError:
        print("Eroare: Fișierul 'cuvinte_de_verificat.txt' nu a fost găsit.")
        return []

class Guesser:
    def __init__(self, word_list):
        self.full_word_list = word_list
        self.possible_words = []
        self.guessed_letters = set()

    def start_new_game(self, word_length, initial_pattern):
        self.possible_words = [word for word in self.full_word_list if len(word) == word_length]
        self.guessed_letters = set()
        
        print(f"Ghicitorul a fost informat că cuvântul are {word_length} litere.")
        print(f"Șablonul inițial este: {initial_pattern}")

        # Process the initial hint
        initial_letters = sorted(list(set(initial_pattern.replace('_', ''))))
        if initial_letters:
            print(f"Procesare indicii inițiale: { ', '.join(initial_letters) }")
            for letter in initial_letters:
                self.guessed_letters.add(letter)
                self.update_knowledge(initial_pattern, letter)
        
        print(f"După procesarea indiciilor, au mai rămas {len(self.possible_words)} cuvinte posibile.")

    def get_best_guess(self):
        if not self.possible_words:
            return None

        all_letters = "".join(self.possible_words)
        remaining_letters = [letter for letter in all_letters if letter not in self.guessed_letters]
        
        if not remaining_letters:
            return None

        letter_counts = Counter(remaining_letters)
        best_letter = letter_counts.most_common(1)[0][0]
        self.guessed_letters.add(best_letter)
        return best_letter

    def update_knowledge(self, pattern, last_guess):
        if not self.possible_words:
            return

        new_possible_words = []
        
        if last_guess in pattern:
            for word in self.possible_words:
                match = True
                for i, letter in enumerate(pattern):
                    if letter != '_' and word[i] != letter:
                        match = False
                        break
                    elif letter == '_' and word[i] == last_guess:
                        match = False
                        break
                if match:
                    new_possible_words.append(word)
        else:
            new_possible_words = [word for word in self.possible_words if last_guess not in word]
            
        self.possible_words = new_possible_words

def main():
    start_time = time.time()
    guesser_dictionary = get_guesser_dictionary()
    if not guesser_dictionary:
        return

    secret_word_data = get_secret_word_data()
    if not secret_word_data:
        return

    total_attempts_overall = 0
    total_words = len(secret_word_data)
    words_guessed_count = 0
    words_failed = []

    print(f"Am găsit {total_words} de cuvinte pentru a le ghici. Începem...")
    print("-" * 40)

    # Loop over all words
    for idx, (secret_word, initial_pattern) in enumerate(secret_word_data):
        
        display_pattern = initial_pattern
        attempts = 0

        guesser = Guesser(guesser_dictionary)
        # The start_new_game in the original code prints a lot. I will keep it.
        print(f"Jocul {idx + 1}/{total_words} - Cuvânt: {secret_word.upper()}")
        guesser.start_new_game(len(secret_word), initial_pattern)
        
        fallback_alphabet = "aăâbcdefghiîjklmnopqrsștțuvwxyz"

        # Game loop for one word
        while display_pattern != secret_word:
            attempts += 1
            
            guess = guesser.get_best_guess()

            if guess is None:
                fallback_guess = None
                for letter in fallback_alphabet:
                    if letter not in guesser.guessed_letters:
                        fallback_guess = letter
                        break
                
                if fallback_guess is None:
                    print(f"EROARE la cuvântul '{secret_word}': Toate literele au fost încercate, dar cuvântul nu a fost găsit.")
                    break 
                
                guess = fallback_guess
                guesser.guessed_letters.add(guess)

            # This is the logic from the original file for updating the pattern
            if guess in secret_word:
                new_pattern = ""
                for i, letter in enumerate(secret_word):
                    if secret_word[i] == guess or display_pattern[i] != '_':
                        new_pattern += secret_word[i]
                    else:
                        new_pattern += "_"
                display_pattern = new_pattern
            
            # This is the call to the (buggy) algorithm
            guesser.update_knowledge(display_pattern, guess)
        
        # After the word is guessed (or failed)
        if display_pattern == secret_word:
            words_guessed_count += 1
            total_attempts_overall += attempts
            print(f"--> Cuvântul '{secret_word.upper()}' a fost ghicit în {attempts} încercări.")
            print("-" * 40)
        else:
            # This branch is taken if the inner loop breaks on error
            words_failed.append(secret_word)
            print(f"--> Cuvântul '{secret_word.upper()}' NU a fost ghicit.")
            print("-" * 40)

    # Final summary
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n====================")
    print("Procesare finalizată!")
    print(f"Timp total: {duration:.2f} secunde")
    print(f"Cuvinte ghicite: {words_guessed_count}/{total_words}")
    if words_failed:
        print(f"Cuvinte care nu au fost ghicite ({len(words_failed)}):")
        for word in words_failed:
            print(f"  - {word.upper()}")

    if words_guessed_count > 0:
        average_attempts = total_attempts_overall / words_guessed_count
        print(f"Total încercări (pentru cuvintele ghicite): {total_attempts_overall}")
        print(f"Medie de încercări pe cuvânt: {average_attempts:.2f}")


if __name__ == "__main__":
    main()
