from typing import Sequence


def strong_british_accent(text: Sequence):
    """Converts your given string/array to a kind-of strong british accent (if you're nonsensical about it...)"""

    def brit(brsentence):

        brsentence = brsentence.replace("it was ", "it was quite ")

        # Words relating to ppl
        brsentence = (
            brsentence.replace("friend", "mate")
            .replace("pal", "mate")
            .replace("buddy", "mate")
            .replace("person", "mate")
            .replace("man", "mate")
            .replace("people", "mates")
        )

        # Some weird past tense stuff i don't even know
        brsentence = brsentence.replace("standing", "stood")
        brsentence = brsentence.replace("sitting", "sat")

        # Pronunciations of syllables
        brsentence = brsentence.replace("o ", "oh ")
        brsentence = brsentence.replace("ee", "ea")
        brsentence = (
            brsentence.replace("er ", "-a ")
            .replace("er", "-a")
            .replace("or ", "-a ")
            .replace("or", "-a")
            .replace("ar ", "-a ")
            .replace("ar", "-a")
        )

        brsentence = brsentence.replace("a", "ah")

        return brsentence

    if not isinstance(text, str):
        britished_msgs = map(brit, text)

        return britished_msgs

    msg = brit(text)
    return msg
