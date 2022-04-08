import discord
from utility.db.database import Database
from utility.disc.embed_data import description_generator


class AutoModSettingsView(discord.ui.View):
    def __init__(self, ctx: discord.ApplicationContext, settings, database: Database):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.settings = settings
        self.database = database
        toggle_button = ToggleButton(self.settings, self.database, self.ctx)
        invite_detector = InviteDetectionButton(self.settings, self.database, self.ctx)
        link_detector = LinkDetectionButton(self.settings, self.database, self.ctx)
        mass_mention_detector = MassMentionDetectionButton(
            self.settings, self.database, self.ctx
        )
        image_spam_detector = ImageSpamDetectionButton(
            self.settings, self.database, self.ctx
        )
        emoji_spam_detector = EmojiSpamDetectionButton(
            self.settings, self.database, self.ctx
        )
        spam_detector = SpamDetectionButton(self.settings, self.database, self.ctx)
        self.add_item(spam_detector)
        self.add_item(invite_detector)
        self.add_item(link_detector)
        self.add_item(mass_mention_detector)
        self.add_item(image_spam_detector)
        self.add_item(emoji_spam_detector)
        self.add_item(toggle_button)


class SpamDetectionButton(discord.ui.Button):
    def __init__(self, settings, database: Database, ctx):
        super().__init__(label="Message Spam detection", row=1)
        self.settings = settings
        self.database = database
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild == True:
            await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True
            )

        await self.database.set_particular_automod_settings(
            interaction.guild.id,
            ["spam_threshold", 0 if self.settings["spam_threshold"] else 4],
        )
        await interaction.response.send_message(
            f"Message Spam detection set to {self.settings['spam_threshold']} every {self.settings['spam_interval']} seconds.",
            ephemeral=True,
        )

        self.settings = await self.database.get_automod_settings(
            str(interaction.guild.id)
        )
        embed = description_generator(self.settings)
        await interaction.message.edit(
            embed=embed,
            view=AutoModSettingsView(self.ctx, self.settings, self.database),
        )


class InviteDetectionButton(discord.ui.Button):
    def __init__(self, settings, database: Database, ctx):
        super().__init__(label="Toggle Invite Detection", row=1)
        self.settings = settings
        self.database = database
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild == True:
            await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True
            )

        await self.database.set_particular_automod_settings(
            interaction.guild.id,
            ["discord_invites", not self.settings["discord_invites"]],
        )
        await interaction.response.send_message(
            f"Invite detection set to {not self.settings['discord_invites']}",
            ephemeral=True,
        )

        embed = discord.Embed(title="Automod Settings", color=0x2F3136)
        self.settings = await self.database.get_automod_settings(
            str(interaction.guild.id)
        )
        embed = description_generator(self.settings)
        await interaction.message.edit(
            embed=embed,
            view=AutoModSettingsView(self.ctx, self.settings, self.database),
        )


class LinkDetectionButton(discord.ui.Button):
    def __init__(self, settings, database: Database, ctx):
        super().__init__(label="Toggle Link detection", row=2)
        self.settings = settings
        self.database = database
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild == True:
            await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True
            )

        await self.database.set_particular_automod_settings(
            interaction.guild.id, ["links", not self.settings["links"]]
        )
        await interaction.response.send_message(
            f"Link detection set to {not self.settings['links']}", ephemeral=True
        )

        self.settings = await self.database.get_automod_settings(
            str(interaction.guild.id)
        )
        embed = description_generator(self.settings)
        await interaction.message.edit(
            embed=embed,
            view=AutoModSettingsView(self.ctx, self.settings, self.database),
        )


class MassMentionDetectionButton(discord.ui.Button):
    def __init__(self, settings, database: Database, ctx):
        super().__init__(label="Mass mention detection", row=2)
        self.settings = settings
        self.database = database
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild == True:
            await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True
            )

        await self.database.set_particular_automod_settings(
            interaction.guild.id, ["mass_mentions", not self.settings["mass_mentions"]]
        )
        await interaction.response.send_message(
            f"Mass mention detection set to {not self.settings['mass_mentions']}",
            ephemeral=True,
        )

        self.settings = await self.database.get_automod_settings(
            str(interaction.guild.id)
        )
        embed = description_generator(self.settings)
        await interaction.message.edit(
            embed=embed,
            view=AutoModSettingsView(self.ctx, self.settings, self.database),
        )


class ImageSpamDetectionButton(discord.ui.Button):
    def __init__(self, settings, database: Database, ctx):
        super().__init__(label="Image Spam detection", row=3)
        self.settings = settings
        self.database = database
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild == True:
            await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True
            )

        await self.database.set_particular_automod_settings(
            interaction.guild.id, ["image_spam", not self.settings["image_spam"]]
        )
        await interaction.response.send_message(
            f"Image Spam detection set to {not self.settings['image_spam']}",
            ephemeral=True,
        )

        self.settings = await self.database.get_automod_settings(
            str(interaction.guild.id)
        )
        embed = description_generator(self.settings)
        await interaction.message.edit(
            embed=embed,
            view=AutoModSettingsView(self.ctx, self.settings, self.database),
        )


class EmojiSpamDetectionButton(discord.ui.Button):
    def __init__(self, settings, database: Database, ctx):
        super().__init__(label="Emoji Spam detection", row=3)
        self.settings = settings
        self.database = database
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild == True:
            await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True
            )

        await self.database.set_particular_automod_settings(
            interaction.guild.id, ["emoji_spam", not self.settings["emoji_spam"]]
        )
        await interaction.response.send_message(
            f"Emoji Spam detection set to {not self.settings['emoji_spam']}",
            ephemeral=True,
        )

        self.settings = await self.database.get_automod_settings(
            str(interaction.guild.id)
        )
        embed = description_generator(self.settings)
        await interaction.message.edit(
            embed=embed,
            view=AutoModSettingsView(self.ctx, self.settings, self.database),
        )


class ToggleButton(discord.ui.Button):
    def __init__(self, settings, database: Database, ctx):
        if settings["enabled"]:
            super().__init__(label="Disable", style=discord.ButtonStyle.red, row=4)
        else:
            super().__init__(label="Enable", style=discord.ButtonStyle.green, row=4)
        self.settings = settings
        self.database = database
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild == True:
            await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True
            )

        await self.database.toggle_automod(str(interaction.guild.id))
        b = self.settings["enabled"]

        self.settings = await self.database.get_automod_settings(
            str(interaction.guild.id)
        )

        embed = description_generator(self.settings)

        if b:
            await interaction.response.send_message(
                "AutoMod has been disabled.", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "AutoMod has been enabled.", ephemeral=True
            )

        await interaction.message.edit(
            embed=embed,
            view=AutoModSettingsView(self.ctx, self.settings, self.database),
        )
