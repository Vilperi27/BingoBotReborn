import discord
from discord import User
from discord.ui import View, Button

from utils import register_user, save_image, has_admin_role, send, team_exists, user_exists, guild_exists, \
    register_guild, register_team, register_all


class SubmissionButtons(View):
    def __init__(self, attachment: discord.Attachment, submitter: User, tile: str = None, item: str = None, team: str = None):
        super().__init__(timeout=None)
        self.attachment = attachment
        self.submitter = submitter
        self.tile = tile
        self.item = item
        self.team = team

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.success)
    async def approve(self, interaction: discord.Interaction, button: Button):
        if not has_admin_role(interaction):
            return await send(interaction, "Forbidden action.", ephemeral=True)

        guild_id = interaction.guild.id
        register_all(guild_id, self.team, self.submitter.id)
        await save_image(self.attachment, guild_id, self.submitter.id, self.tile, self.item, self.team)

        for button in self.children:
            button.disabled = True

        await interaction.message.edit(content=":white_check_mark: Approved! :white_check_mark:", view=self)
        await send(
            interaction,
            f"You have approved this submission!",
            ephemeral=True
        )

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: Button):
        if not has_admin_role(interaction):
            await interaction.response.send_message("Forbidden action.", ephemeral=True)
            return

        await interaction.response.send_message(
            f"You have rejected this submission!",
            ephemeral=True
        )

        for button in self.children:
            button.disabled = True

        await interaction.message.edit(content=":x: Rejected! :x:", view=self)


class OverwriteButtons(View):
    def __init__(self, tile: int, submitter: discord.User | str, attachment, team: str = None):
        super().__init__(timeout=None)
        self.tile = tile
        self.submitter = submitter
        self.attachment = attachment
        self.team = team

    @discord.ui.button(label="Overwrite", style=discord.ButtonStyle.primary)
    async def overwrite(self, interaction: discord.Interaction, button: Button):
        if not has_admin_role(interaction):
            await interaction.response.send_message("Forbidden action.", ephemeral=True)
            return

        await register_user(interaction.guild.id, self.submitter.id, self.team)
        await save_image(interaction, self.submitter.id, self.tile, self.attachment, self.team)
        await interaction.response.send_message(
            f"You have approved and overwritten this submission!",
            ephemeral=True
        )

        for button in self.children:
            button.disabled = True

        await interaction.message.edit(content=":white_check_mark: Approved and overwritten! :white_check_mark:", view=self)

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: Button):
        if not has_admin_role(interaction):
            await interaction.response.send_message("Forbidden action.", ephemeral=True)
            return

        await interaction.response.send_message(
            f"You have rejected this submission!",
            ephemeral=True
        )

        for button in self.children:
            button.disabled = True

        await interaction.message.edit(content=":x: Rejected! :x:", view=self)