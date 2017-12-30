#!python3
# Code Challenge 02 - Word Values Part II - a simple game
# http://pybit.es/codechallenge02.html
from itertools import chain, permutations
import os
import random
import shelve

from data import DICTIONARY, LETTER_SCORES, POUCH

NUM_LETTERS = 7
UPPER_DICT = {word.upper() for word in DICTIONARY}


# re-use from challenge 01
def calc_word_value(word):
    """Calc a given word value based on Scrabble LETTER_SCORES mapping"""
    return sum(LETTER_SCORES.get(char.upper(), 0) for char in word)


# re-use from challenge 01
def max_word_value(words):
    """Calc the max value of a collection of words"""
    return max(words, key=calc_word_value)


def draw_letters():
    """Draw NUM_LETTERS random letters from pouch."""
    letters = random.sample(POUCH, NUM_LETTERS)
    print("Letters drawn: {}".format(', '.join(letters)))
    return letters


def ask_for_word(letters):
    user_input = input("Form a valid word: ").upper()
    if _validation(user_input, letters):
        return user_input


def _validation(user_input, letters):
    if not all([letters.count(c) >= user_input.count(c) for c in user_input]):
        raise ValueError(
            "You don't have the right letters to form '{}'".format(user_input))
    if user_input not in UPPER_DICT:
        raise ValueError("'{}' not found in dictionary.".format(user_input))

    return True


def _get_permutations_draw(letters):
    letter_permutations = chain.from_iterable(
        permutations(letters, r) for r in range(len(letters)+1))

    return ["".join(p) for p in letter_permutations if p]


def get_possible_dict_words(letters):
    return [lp for lp in _get_permutations_draw(letters) if lp in UPPER_DICT]


def evaluate_word(letters, user_word):
    uw_value = calc_word_value(user_word)
    print("Word chosen: {} (value: {})".format(user_word, uw_value))

    valid_words = get_possible_dict_words(letters)
    opt_word = max_word_value(valid_words)
    ow_value = calc_word_value(opt_word)

    print("Optimal word possible: {} (value: {}).".format(opt_word, ow_value))

    return uw_value, ow_value


def calculate_score(uw_value, ow_value):
    score = uw_value / ow_value * 100
    if _is_highscore(score):
        print(f"You scored: {score:.1f} (NEW HIGHSCORE)")
    else:
        print(f"You scored: {score:.1f}")

    return score


def _is_highscore(score):
    try:
        return score > max([hs[1] for hs in HIGHSCORE])
    except ValueError:
        return False


def save_highscore():
    with shelve.open("score.data") as db:
        db["highscore"] = HIGHSCORE


def load_highscore():
    with shelve.open("score.data") as db:
        return db.get("highscore", [])


def print_top_10():
    top_10 = sorted(HIGHSCORE[:10], reverse=True, key=lambda x: x[1])
    for i, hs in enumerate(top_10, 1):
        word, score = hs
        print(i, word, round(score, 1))


def main():
    letters = draw_letters()
    user_word = ask_for_word(letters)
    uw_value, ow_value = evaluate_word(letters, user_word)

    score = calculate_score(uw_value, ow_value)
    HIGHSCORE.append((user_word, score))
    print_top_10()
    save_highscore()


if __name__ == "__main__":
    HIGHSCORE = load_highscore()
    main()
