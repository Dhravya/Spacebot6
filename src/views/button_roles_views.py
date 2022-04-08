import discord
from discord.ui import Modal, InputText
from utility.db.database import Database


class RoleButton(discord.ui.Button):
    def __init__(self, role: discord.Role):
        """
        A button for one role. `custom_id` is needed for persistent views.
        """
        super().__init__(
            label=role.name,
            style=discord.enums.ButtonStyle.primary,
            custom_id=str(role.id),
        )

    async def callback(self, interaction: discord.Interaction):
        """This function will be called any time a user clicks on this button.
        Parameters
        ----------
        interaction : discord.Interaction
            The interaction object that was created when a user clicks on a button.
        """
        # Figure out who clicked the button.
        user = interaction.user
        # Get the role this button is for (stored in the custom ID).
        role = interaction.guild.get_role(int(self.custom_id))

        if role is None:
            # If the specified role does not exist, return nothing.
            # Error handling could be done here.
            return

        # Add the role and send a response to the uesr ephemerally (hidden to other users).
        if role not in user.roles:
            # Give the user the role if they don't already have it.
            await user.add_roles(role)
            await interaction.response.send_message(
                f"🎉 You have been given the role {role.mention}", ephemeral=True
            )
        else:
            # Else, Take the role from the user
            await user.remove_roles(role)
            await interaction.response.send_message(
                f"❌ The {role.mention} role has been taken from you", ephemeral=True
            )


class ButtonRolesEmbedModal(Modal):
    def __init__(self, database: Database) -> None:
        super().__init__(title="Button Roles Embed")
        self.add_item(
            InputText(label="Embed Title", placeholder="Type the title of the embed")
        )
        self.database = database
        self.add_item(
            InputText(
                label="Embed Colour",
                placeholder="Hex code for the colour of the embed",
                style=discord.InputTextStyle.singleline,
                required=False,
            )
        )

        self.add_item(
            InputText(
                label="Embed Message",
                placeholder="Type the message you want in the embed.",
                style=discord.InputTextStyle.long,
            )
        )

        self.add_item(
            InputText(
                label="Role IDs",
                placeholder="Type the Role IDs separated by a space, eg: 930370255333752832 942483406476963900 etc.",
                style=discord.InputTextStyle.paragraph,
            )
        )

    async def callback(self, interaction: discord.Interaction):
        role_ids = []
        for role_id in self.children[3].value.split(" "):
            try:
                role_ids.append(int(role_id))
            except:
                embed = discord.Embed(
                    description="Invalid Role ID", colour=discord.Colour.red()
                )
                await interaction.response.send_message(embed=embed)
                return

        if len(role_ids) == 0:
            embed = discord.Embed(
                description="No Role IDs were given", colour=discord.Colour.red()
            )
            await interaction.response.send_message(embed=embed)
            return

        elif len(role_ids) > 10:
            embed = discord.Embed(
                description="Max 10 roles can be given", colour=discord.Colour.red()
            )
            await interaction.response.send_message(embed=embed)
            return
        view = discord.ui.View(timeout=None)
        for role_id in role_ids:
            # Get the role from the guild by ID.
            try:
                role = interaction.guild.get_role(role_id)
                await self.database.add_role(role_id, interaction.guild.id)
                view.add_item(RoleButton(role))

            except discord.errors.HTTPException:
                embed = discord.Embed(
                    description="@dhravya put error message here my head hurts",
                    colour=discord.Colour.red(),
                )
                await interaction.response.send_message(embed=embed)
                return

        try:
            colour = self.children[1].value[1:]
        except KeyError:
            colour = None
        if colour != None:
            try:
                colour = discord.Colour(int(colour, 16))
            except:
                embed = discord.Embed(
                    description="Invalid Colour", colour=discord.Colour.red()
                )
                await interaction.response.send_message(embed=embed)
                return
        else:
            colour = discord.Colour.default()
        embed = discord.Embed(
            title=self.children[0].value,
            description=self.children[2].value,
            colour=colour,
        )
        await interaction.response.send_message(embed=embed, view=view)


class ModalButton(discord.ui.Button):
    def __init__(self, databaseInstance: Database) -> None:
        super().__init__(label="Modal Button", style=discord.ButtonStyle.primary)
        self.databaseInstance = databaseInstance

    async def callback(self, interaction: discord.Interaction):
        modal = ButtonRolesEmbedModal(database=self.databaseInstance)
        await interaction.response.send_modal(modal)
