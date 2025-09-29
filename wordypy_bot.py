#!/usr/bin/env python3
"""
WordyPy Game: An AI bot that plays a Wordle-like game.

This script contains the classes to run a game of WordyPy, where an AI `Bot`
attempts to guess a secret five-letter word. The `GameEngine` provides
feedback for each guess as a list of `Letter` objects, which the `Bot` uses
to make smarter guesses in subsequent rounds.

Classes:
    Letter: Represents a single letter in a guess and its feedback status.
    Bot: The AI agent that filters a word list and makes guesses.
    GameEngine: Controls the game flow and evaluates the bot's guesses.
"""

import random



class Letter:
    """Represents a single letter from a guess and its feedback status. 

    This class acts as a data structure to hold a single character from a guess
    and the results of that guess (e.g., if it's in the word, if it's in the
    correct position). [cite: 2]

    Attributes:
        letter (str): The character itself (e.g., 'A').
        in_word (bool): True if the letter is in the target word.
        in_correct_place (bool): True if the letter is in the correct position.
    """

    def __init__(self, letter: str) -> None:
        """Initializes the Letter object with a character. 
        
        This is the constructor. When you create a Letter object, you give it a 
        character (e.g., 'A'), which it stores. The feedback attributes, in_word 
        and in_correct_place, are initialized to False because their true status 
        is unknown until the GameEngine evaluates them. 
        """
        self.letter: str = letter
        
        # The status flags start as False because the feedback for this letter
        # is unknown until the GameEngine evaluates it.
        self.in_word: bool = False
        self.in_correct_place: bool = False

    def __repr__(self) -> str:
        """Provides a developer-friendly string representation for debugging."""
        return f"Letter('{self.letter}', in_word={self.in_word}, in_correct_place={self.in_correct_place})"
    
    """is_in_word(self) and is_in_correct_place(self): 
           These are simple "getter" methods. 
           They don't change anything; they just return the current boolean value of their 
           corresponding attribute. The GameEngine uses these methods to check the feedback 
           for each letter.
    """
    def is_in_word(self) -> bool:
        """Returns the status of the in_word flag."""
        return self.in_word

    def is_in_correct_place(self) -> bool:
        """Returns the status of the in_correct_place flag."""
        return self.in_correct_place


class Bot:
    """The AI agent that filters a word list and makes guesses."""

    def __init__(self, word_list_file: str) -> None:
        """Initializes the Bot with a list of possible words.

        This constructor reads a specified text file, cleans up each word
        (by removing whitespace and converting to uppercase), and stores
        the resulting words in a list for the bot to use.

        Args:
            word_list_file (str): The path to a text file containing
                                  valid words, one per line.
        """
        # This list will hold all words the bot considers possible answers.
        # It is filtered down after each guess.
        self.word_list: list[str] = []
        
        # 'with open(...)' ensures the file is closed automatically after reading.
        with open(word_list_file, 'r') as file:
            for word in file:
                # .strip() removes whitespace/newlines and .upper() ensures
                # all words are uppercase to match the GameEngine's format.
                self.word_list.append(word.strip().upper())


    def make_guess(self) -> str:
        """Selects and returns a single word from the current list of possibilities.

        This method is called by the GameEngine at the start of each turn. As the
        word_list is filtered down by the record_guess_results method, the
        random choice made here becomes progressively more strategic.
        
        Returns:
            str: The bot's next guess.
        """
        # Use the random.choice() function to pick one word from the list
        # of words the bot currently thinks are possible.
        guess = random.choice(self.word_list)
        return guess


    def record_guess_results(self, guess: str, guess_results: list[Letter]) -> None:
        """Filters the bot's word list based on guess feedback.

        This method is the core logic of the bot. It iterates through its
        list of possible words, eliminating any word that violates the rules
        learned from the feedback provided by the GameEngine.

        Args:
            guess (str): The word that was just guessed.
            guess_results (list[Letter]): A list of Letter objects representing the
                                         feedback for the guess.
        """
        # Remove the guessed word from the list to prevent repeats.
        if guess in self.word_list:
            self.word_list.remove(guess)
        
        # Create a new, empty list to hold only the words that pass all the rules.
        new_possible_words = []

        # Check every remaining word against the feedback from the last guess.        
        for word in self.word_list:
            is_still_possible = True

            # This inner loop checks the current 'word' against each letter's feedback.            
            for i, feedback in enumerate(guess_results):
                char_in_guess = feedback.letter

                # Rule 1: Green letters (correct letter, correct place)
                if feedback.is_in_correct_place():
                    if word[i] != char_in_guess:
                        is_still_possible = False
                        break  # This word is invalid.
                
                # Rule 2: Yellow letters (correct letter, wrong place)
                elif feedback.is_in_word():
                    if char_in_guess not in word or word[i] == char_in_guess:
                        is_still_possible = False
                        break  # This word is invalid.
                
                # Rule 3: Grey letters (incorrect letter)
                else:
                    # A grey letter can be eliminated ONLY if it doesn't also appear
                    # as a green or yellow in the SAME guess (e.g., guess "ARRAY" for target "ALARM").
                    is_positive_somewhere = any(
                        char_in_guess == f.letter and f.is_in_word() for f in guess_results
                    )
                    if not is_positive_somewhere and char_in_guess in word:
                        is_still_possible = False
                        break  # This word is invalid.
            
            # If the word survived all the checks, add it to our new list.
            if is_still_possible:
                new_possible_words.append(word)
        
        # Finally, replace the old word list with the newly filtered, smaller list.
        self.word_list = new_possible_words


class GameEngine:
    """The GameEngine represents a new WordPy game to play."""

    def __init__(self):
        self.err_input = False
        self.err_guess = False
        self.prev_guesses = []  # record the previous guesses

    def play(
        self, bot, word_list_file: str = "words.txt", target_word: str = None
    ) -> None:
        """Plays a new game, using the supplied bot. By default the GameEngine
        will look in words.txt for the list of allowable words and choose one
        at random. Set the value of target_word to override this behavior and
        choose the word that must be guessed by the bot.
        """

        def format_results(results) -> str:
            """Small function to format the results into a string for quick
            review by caller.
            """
            response = ""
            for letter in results:
                if letter.is_in_correct_place():
                    response = response + letter.letter
                elif letter.is_in_word():
                    response = response + "*"
                else:
                    response = response + "?"
            return response

        def set_feedback(guess: str, target_word: str) -> tuple[bool, list[Letter]]:
            # whether the complete guess is correct
            # set it to True initially and then switch it to False if any letter doesn't match
            correct: bool = True

            letters = []
            for j in range(len(guess)):
                # create a new Letter object
                letter = Letter(guess[j])

                # check to see if this character is in the same position in the
                # guess and if so set the in_correct_place attribute
                if guess[j] == target_word[j]:
                    letter.in_correct_place = True
                    known_letters[j] = guess[j]  # record the known correct positions
                else:
                    # we know they don't have a perfect answer, so let's update
                    # our correct variable for feedback
                    correct = False

                # check to see if this character is anywhere in the word
                if guess[j] in target_word:
                    letter.in_word = True
                else:
                    unused_letters.add(guess[j])  # record the unused letters

                # add this letter to our list of letters
                letters.append(letter)

            return correct, letters

        # read in the dictionary of allowable words
        word_list: list(str) = list(
            map(lambda x: x.strip().upper(), open(word_list_file, "r").readlines())
        )
        # record the known correct positions
        known_letters: list(str) = [None, None, None, None, None]
        # set of unused letters
        unused_letters = set()

        # assign the target word to a member variable for use later
        if target_word is None:
            target_word = random.choice(word_list).upper()
        else:
            target_word = target_word.upper()
            if target_word not in word_list:
                print(f"Target word {target_word} must be from the word list")
                self.err_input = True
                return

        print(
            f"Playing a game of WordyPy using the word list file of {word_list_file}.\nThe target word for this round is {target_word}\n"
        )

        MAX_GUESSES = 6
        for i in range(1, MAX_GUESSES):
            # ask the bot for it's guess and evaluate
            guess: str = bot.make_guess()

            # print out a line indicating what the guess was
            print(f"Evaluating bot guess of {guess}")

            if guess not in word_list:
                print(f"Guessed word {guess} must be from the word list")
                self.err_guess = True
            elif guess in self.prev_guesses:
                print(f"Guess word cannot be the same one as previously used!")
                self.err_guess = True

            if self.err_guess:
                return

            self.prev_guesses.append(guess)  # record the previous guess

            for j, letter in enumerate(guess):
                if letter in unused_letters:
                    print(
                        f"The bot's guess used {letter} which was previously identified as not used!"
                    )
                    self.err_guess = True
                if known_letters[j] is not None:
                    if letter != known_letters[j]:
                        print(
                            f"Previously identified {known_letters[j]} in the correct position is not used at position {j}!"
                        )
                        self.err_guess = True

                if self.err_guess:
                    return

            # get the results of the guess
            correct, results = set_feedback(guess, target_word)

            # print out a line indicating whether the guess was correct or not
            print(f"Was this guess correct? {correct}")

            print(f"Sending guess results to bot {format_results(results)}\n")

            bot.record_guess_results(guess, results)

            # if they got it correct we can just end
            if correct:
                print(f"Great job, you found the target word in {i} guesses!")
                return

        # if we get here, the bot didn't guess the word
        print(
            f"Thanks for playing! You didn't find the target word in the number of guesses allowed."
        )
        return



# =====================================================================
# SCRIPT EXECUTION
# =====================================================================
if __name__ == "__main__":
    # -----------------------------------------------------------------
    # GAME CONTENT AND SETUP
    # -----------------------------------------------------------------
    # A list of words for the game.
    favorite_words = [
        # Original words
        "doggy", "drive", "daddy", "field", "state",
        # 50 new words
        "about", "above", "agent", "alarm", "alive", "alone", "anger", "apple",
        "apply", "argue", "avoid", "aware", "basic", "beach", "begin", "black",
        "blame", "blind", "block", "board", "brain", "bread", "break", "brief",
        "bring", "brown", "build", "cable", "catch", "chain", "chair", "chart",
        "check", "chief", "child", "claim", "class", "clean", "clear", "clock",
        "close", "cloud", "coach", "coast", "could", "count", "court", "cover",
        "craft", "cream", "crime"
    ]

    # Write this list to a temporary file for the bot to read.
    words_file = "temp_file.txt"
    with open(words_file, "w") as file:
        file.writelines("\n".join(favorite_words))

    # --- NEW: Select a random target word ---
    # Choose one word from the list to be the secret target for this game.
    target = random.choice(favorite_words)

    # -----------------------------------------------------------------
    # INITIALIZE AND START THE GAME
    # -----------------------------------------------------------------
    # Initialize the Bot and the GameEngine.
    bot = Bot(words_file)
    game = GameEngine()

    # Start the game, passing the bot and the randomly chosen target word.
    game.play(bot, word_list_file=words_file, target_word=target)
