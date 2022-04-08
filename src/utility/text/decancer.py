import unicodedata, sys
import unicodedata


def strip_accents(s):
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )


print(strip_accents("ΛGΞИT ム ~ 𝘿𝙚𝙧𝙚𝙆"))
