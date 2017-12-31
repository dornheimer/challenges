#!python3
# Code Challenge 02 - Word Values Part II - a simple game
# http://pybit.es/codechallenge02.html
from itertools import chain, permutations
import os
import random
import shelve

from data import DICTIONARY, LETTER_SCORES, POUCH

NUM_LETTERS = 7


# re-use from challenge 01
def calc_word_value(word):
    """Calc a given word value based on Scrabble LETTER_SCORES mapping"""
    return sum(LETTER_SCORES.get(char.upper(), 0) for char in word)


# re-use from challenge 01
def max_word_value(words):
    """Calc the max value of a collection of words"""
    return max(words, key=calc_word_value).upper()


def draw_letters():
    """Draw NUM_LETTERS random letters from pouch."""
    letters = random.sample(POUCH, NUM_LETTERS)
    print("Letters drawn: {}".format(', '.join(letters)))
    return letters


def ask_for_word(letters, opt_word, ow_value):
    while True:
        user_input = input("Form a valid word: ").upper()
        if _validation(user_input, letters):
            return user_input

        get_hint(opt_word, ow_value)


def _validation(user_input, letters):
    if user_input == "*":
        return False

    if not all([letters.count(c) >= user_input.count(c) for c in user_input]):
        raise ValueError(
            "You don't have the right letters to form '{}'".format(user_input))
    if user_input.lower() not in DICTIONARY:
        raise ValueError("'{}' not found in dictionary.".format(user_input))

    return True


def _get_permutations_draw(letters):
    return chain.from_iterable(
        permutations(letters, r) for r in range(len(letters)+1))


def get_possible_dict_words(letters):
    permutations = ["".join(p).lower() for p in _get_permutations_draw(letters) if p]
    return set(permutations) & set(DICTIONARY)


def evaluate_word(letters, user_word, opt_word, ow_value):
    uw_value = calc_word_value(user_word)
    print("Word chosen: {} (value: {})".format(user_word, uw_value))
    print("Optimal word possible: {} (value: {}).".format(opt_word, ow_value))

    if len(user_word) == NUM_LETTERS or user_word == opt_word:
        bonus = True

    return uw_value


def get_hint(opt_word, ow_value):
    global HINT_COUNTER
    hint = {
        0: (f"Length of optimal word: {len(opt_word)}"),
        1: (f"Maximum possible value: {ow_value}"),
        2: (f"First letter of optimal word: {opt_word[0]}"),
        3: "Hints exhausted."
    }.get(min(HINT_COUNTER, 3))

    HINT_COUNTER += 1
    print(hint)


def calculate_score(uw_value, ow_value):
    score = uw_value / ow_value * 100
    message = f"You scored: {score:.1f}"

    hint_cost = min(HINT_COUNTER, 3) * 10
    if hint_cost:
        message += f" (-{hint_cost} hints)"
        score -= hint_cost

    if bonus:
        message += " (+20 bonus)"
        score += 20

    if _is_highscore(score): message += " (NEW HIGHSCORE)"

    print(message)

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
    print("{:*^40}".format(" HIGHSCORE "))
    for i, hs in enumerate(top_10, 1):
        word, score = hs
        print(i, word, round(score, 1))
    print("*" * 40)


def main():
    letters = draw_letters()
    valid_words = get_possible_dict_words(letters)
    opt_word = max_word_value(valid_words)
    ow_value = calc_word_value(opt_word)

    user_word = ask_for_word(letters, opt_word, ow_value)
    uw_value = evaluate_word(letters, user_word, opt_word, ow_value)

    score = calculate_score(uw_value, ow_value)
    HIGHSCORE.append((user_word, score))
    print_top_10()
    save_highscore()


if __name__ == "__main__":
    HIGHSCORE = load_highscore()
    HINT_COUNTER = 0
    bonus = False
    main()
