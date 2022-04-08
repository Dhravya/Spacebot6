from typing import Sequence
import random


def owofy(text: Sequence, *, wanky: bool = False):
    """translates your given text to owo!"""

    def last_replace(s, old, new):
        li = s.rsplit(old, 1)
        return new.join(li)

    def text_to_owo(textstr):

        exclamations = ("?", "!", ".", "*")

        prefixes = [
            "Haii UwU ",
            "Hiiiiii 0w0 ",
            "Hewoooooo >w< ",
            "*W* ",
            "mmm~ uwu ",
            "Oh... Hi there {} ".format(random.choice(["·///·", "(。O⁄ ⁄ω⁄ ⁄ O。)"])),
        ]  # I need a life, help me

        subs = {
            "why": "wai",
            "Why": "Wai",
            "Hey": "Hai",
            "hey": "hai",
            "ahw": "ao",
            "Hi": "Hai",
            "hi": "hai",
            "you": "u",
            "L": "W",
            "l": "w",
            "R": "W",
            "r": "w",
        }

        textstr = random.choice(prefixes) + textstr
        if not textstr.endswith(exclamations):
            textstr += " uwu"

        smileys = [";;w;;", "^w^", ">w<", "UwU", r"(・`ω\´・)"]

        if not wanky:  # to prevent wanking * w *
            textstr = textstr.replace("Rank", "Ⓡank").replace("rank", "Ⓡank")
            textstr = textstr.replace("Lank", "⒧ank").replace("lank", "⒧ank")

        textstr = last_replace(textstr, "there!", "there! *pounces on u*")

        for key, val in subs.items():
            textstr = textstr.replace(key, val)

        textstr = last_replace(textstr, "!", "! {}".format(random.choice(smileys)))
        textstr = last_replace(
            textstr, "?", "? {}".format(random.choice(["owo", "O·w·O"]))
        )
        textstr = last_replace(textstr, ".", ". {}".format(random.choice(smileys)))

        vowels = ["a", "e", "i", "o", "u", "A", "E", "I", "O", "U"]

        if not wanky:
            textstr = textstr.replace("Ⓡank", "rank").replace("⒧ank", "lank")

        for v in vowels:
            if "n{}".format(v) in textstr:
                textstr = textstr.replace("n{}".format(v), "ny{}".format(v))
            if "N{}".format(v) in textstr:
                textstr = textstr.replace(
                    "N{}".format(v), "N{}{}".format("Y" if v.isupper() else "y", v)
                )

        return textstr

    if not isinstance(text, str):
        owoed_msgs = map(text_to_owo, text)

        return owoed_msgs

    return text_to_owo(text)
