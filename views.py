import discord
from discord.ui import View, Button

from utils import register_user, save_image, has_admin_role


class SubmissionButtons(View):
    def __init__(self, tile: int, submitter: discord.User, image_url, team: str = None):
        super().__init__(timeout=None)
        self.tile = tile
        self.submitter = submitter
        self.image_url = image_url
        self.team = team

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.success)
    async def approve(self, interaction: discord.Interaction, button: Button):
        if not has_admin_role(interaction):
            await interaction.response.send_message("Forbidden action.", ephemeral=True)
            return

        await register_user(interaction.guild.id, self.submitter.id, self.team)
        await save_image(interaction, self.submitter.id, self.tile, self.image_url, team=self.team)
        await interaction.response.send_message(
            f"You have approved this submission!",
            ephemeral=True
        )

        for button in self.children:
            button.disabled = True

        await interaction.message.edit(content=":white_check_mark: Approved! :white_check_mark:", view=self)

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
    def __init__(self, tile: int, submitter: discord.User | str, image_url, team: str = None):
        super().__init__(timeout=None)
        self.tile = tile
        self.submitter = submitter
        self.image_url = image_url
        self.team = team

    @discord.ui.button(label="Overwrite", style=discord.ButtonStyle.primary)
    async def overwrite(self, interaction: discord.Interaction, button: Button):
        if not has_admin_role(interaction):
            await interaction.response.send_message("Forbidden action.", ephemeral=True)
            return

        await register_user(interaction.guild.id, self.submitter.id, self.team)
        await save_image(interaction, self.submitter.id, self.tile, self.image_url, True, self.team)
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