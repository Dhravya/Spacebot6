import discord
from utility.text.censor_words import censor_letters


def description_generator(settings: dict):
    embed = discord.Embed(title="Automod Settings", color=0x2F3136)
    embed.description = f"""
        **Enabled?** {"<:checkmark:938814978142642196>" if settings["enabled"] else "<:crossno:938061321696575508>"}
        **Discord Invite Detection** {"<:checkmark:938814978142642196>" if settings["discord_invites"] else "<:crossno:938061321696575508>"}
        **Link detection** {"<:checkmark:938814978142642196>" if settings["links"] else "<:crossno:938061321696575508>"}
        **Mass mentions detection** {"<:checkmark:938814978142642196>" if settings["mass_mentions"] else "<:crossno:938061321696575508>"}
        **Image Spam detection** {"<:checkmark:938814978142642196>" if settings["image_spam"] else "<:crossno:938061321696575508>"}
        **Emoji spam detection** {"<:checkmark:938814978142642196>" if settings["emoji_spam"] else "<:crossno:938061321696575508>"}
        
        **Spam threshold** : `{settings["spam_threshold"]}`
        **Spam Interval**: `{settings["spam_interval"]}`
        This means that `{settings["spam_threshold"]}` messages every `{settings["spam_interval"]}` seconds are allowed
        **Capital Threshold**: `{settings["capital_threshold"]}`
        **Punishment**: Timeout for `{str(settings["punishment_timeout_minutes"])}` minutes
        
        **Ignored channels**: {" ".join(f"<#{channel}>" for channel in settings["ignored_channels"])}
        **Ignored users**: {" ".join(f"<@{user}>" for user in settings["ignored_users"])}
        **Ignored roles**: {" ".join(f"<@&{roleID}>" for roleID in settings["ignored_roles"])}
        **Blacklisted words**: `{censor_letters(" ".join(settings["ignored_words"]))}`
        """
    embed.set_thumbnail(
        url="https://cdn.discordapp.com/emojis/907486308006510673.webp?size=160&quality=lossless"
    )
    return embed
