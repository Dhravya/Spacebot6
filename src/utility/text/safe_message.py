import discord
import re


def safe_message(text: str) -> str:
    msg = text.replace("@everyone", "everyone").replace("@here", "here")

    # Remove mentions
    for mention in re.findall(r"<@!?(\d+)>", msg):
        msg = msg.replace(f"<@!{mention}>", "")

    return msg
