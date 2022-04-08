import random


def censor_letters(word):
    """
    This function censors the letters in the word.
    """
    censored_word = ""
    for letter in word:
        if random.randint(0, 1):
            censored_word += "*"
        else:
            censored_word += letter
    return censored_word
