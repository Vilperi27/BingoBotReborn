import discord
from discord.ui import View, Button

from active_context import bingoadmin_role
from errors import TileExistsError
from utils import register_user, save_image


class SubmissionButtons(View):
    def __init__(self, tile: int, submitter: discord.User, image_url):
        super().__init__(timeout=None)
        self.tile = tile
        self.submitter = submitter
        self.image_url = image_url

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.success)
    async def approve(self, interaction: discord.Interaction, button: Button):
        role = discord.utils.get(interaction.guild.roles, name=bingoadmin_role)

        if role not in interaction.user.roles:
            await interaction.response.send_message("Forbidden action.", ephemeral=True)
            return

        await register_user(interaction.guild.id, self.submitter.id)

        try:
            await save_image(interaction, self.submitter.id, self.tile, self.image_url)
        except TileExistsError as e:
            await interaction.response.send_message(
                f"Submission for the tile already exists. Please use !remove command first",
                ephemeral=True
            )

        await interaction.response.send_message(
            f"You have approved this submission!",
            ephemeral=True
        )

        for button in self.children:
            button.disabled = True

        await interaction.message.edit(view=self)

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: Button):
        role = discord.utils.get(interaction.guild.roles, name=bingoadmin_role)

        if role not in interaction.user.roles:
            await interaction.response.send_message("Forbidden action.", ephemeral=True)
            return

        await interaction.response.send_message(
            f"You have rejected this submission!",
            ephemeral=True
        )

        for button in self.children:
            button.disabled = True

        await interaction.message.edit(view=self)

    