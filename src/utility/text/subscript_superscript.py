superscript = "ᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏˡᵐⁿᵒᵖᵠʳˢᵗᵘᵛʷˣʸᶻᴬᴮᶜᴰᴱᶠᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾᵠᴿˢᵀᵁⱽᵂˣʸᶻ"
normal_text = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
subscript = "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎"


def convert_to_superscript(text: str):
    """Converts normal text to superscript"""
    result = ""
    for char in text:
        if char in normal_text:
            result += superscript[normal_text.index(char)]
        else:
            result += char
    return result
