import discord
from discord.ui import View, Button

from utils import register_user, save_image, has_admin_role


class SubmissionButtons(View):
    def __init__(self, tile: int, item: str, submitter: discord.User, attachment, team: str = None):
        super().__init__(timeout=None)
        self.tile = tile
        self.item = item
        self.submitter = submitter
        self.attachment = attachment
        self.team = team

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.success)
    async def approve(self, interaction: discord.Interaction, button: Button):
        try:
            if not has_admin_role(interaction):
                await interaction.response.send_message("Forbidden action.", ephemeral=True)
                return

            await register_user(interaction.guild.id, self.submitter.id, self.team)
            await save_image(interaction, self.submitter.id, self.tile, self.item, self.attachment, team=self.team)
            await interaction.response.send_message(
                f"You have approved this submission!",
                ephemeral=True
            )

            for button in self.children:
                button.disabled = True

            await interaction.message.edit(content=":white_check_mark: Approved! :white_check_mark:", view=self)
        except Exception as e:
            print(e)

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
    def __init__(self, tile: int, item: str, submitter: discord.User | str, attachment, team: str = None):
        super().__init__(timeout=None)
        self.tile = tile
        self.item = item
        self.submitter = submitter
        self.attachment = attachment
        self.team = team

    @discord.ui.button(label="Overwrite", style=discord.ButtonStyle.primary)
    async def overwrite(self, interaction: discord.Interaction, button: Button):
        if not has_admin_role(interaction):
            await interaction.response.send_message("Forbidden action.", ephemeral=True)
            return

        await register_user(interaction.guild.id, self.submitter.id, self.team)
        await save_image(interaction, self.submitter.id, self.tile, self.item, self.attachment, True, self.team)
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