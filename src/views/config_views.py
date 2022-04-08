import discord
from discord.ext import commands
from utility.constants.logging_const import channel_map


class LoggingConfigModal(discord.ui.Modal):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(title="Logging configuration")
        self.bot = bot

        self.add_item(
            discord.ui.InputText(
                style=discord.InputTextStyle.short,
                label="Channel ID for Message updates",
                placeholder="Type the channel ID, EX: 905904027058984960",
                custom_id="message_updates",
            )
        )

        self.add_item(
            discord.ui.InputText(
                style=discord.InputTextStyle.short,
                label="Channel ID for Member updates",
                placeholder="Type the channel ID, EX: 905904027058984960",
                custom_id="member_updates",
            )
        )

        self.add_item(
            discord.ui.InputText(
                style=discord.InputTextStyle.short,
                label="Channel ID for Role and channel updates",
                placeholder="Type the channel ID, EX: 905904027058984960",
                custom_id="role_channel_updates",
            )
        )

        self.add_item(
            discord.ui.InputText(
                style=discord.InputTextStyle.short,
                label="Channel ID for Guild updates",
                placeholder="Type the channel ID, EX: 905904027058984960",
                custom_id="guild_updates",
            )
        )

        self.add_item(
            discord.ui.InputText(
                style=discord.InputTextStyle.short,
                label="Channel ID for Moderation updates",
                placeholder="Type the channel ID, EX: 905904027058984960",
                custom_id="moderation_updates",
            )
        )

    async def callback(self, interaction: discord.Interaction):

        channels = {}
        for child in self.children:
            if child.custom_id is not None:
                channels[child.custom_id] = child.value

        for log_type in channels:
            channel = int(channels[log_type])

            if channel == "":
                continue
            try:
                channel_id = int(channel)
            except:
                embed = discord.Embed(
                    description="Invalid Channel ID", colour=discord.Colour.red()
                )
                await interaction.response.send_message(embed=embed)
                return
            try:
                channel = interaction.guild.get_channel(channel_id)
            except:
                embed = discord.Embed(
                    description="Channel not found", colour=discord.Colour.red()
                )
                await interaction.response.send_message(embed=embed)
                return
            if channel.type != discord.ChannelType.text:
                embed = discord.Embed(
                    description="Channel is not a text channel",
                    colour=discord.Colour.red(),
                )
                await interaction.response.send_message(embed=embed)
                return

            # Check if guild is in the database

            await self.bot.cursor.execute(
                "SELECT * FROM logging WHERE guild_id = %s",
                (str(interaction.guild.id),),
            )
            result = await self.bot.cursor.fetchone()

            if result is None:
                # Insert
                await self.bot.cursor.execute(
                    "INSERT INTO logging (guild_id) VALUES (%s)",
                    (str(interaction.guild.id),),
                )

            for column_name in channel_map[log_type]:
                try:
                    await self.bot.cursor.execute(
                        "UPDATE logging SET {} = {} WHERE guild_id = {}".format(
                            column_name, str(channel.id), str(interaction.guild.id)
                        )
                    )
                except:
                    pass
            await self.bot.conn.commit()

        await interaction.response.send_message("Logging configuration updated")
