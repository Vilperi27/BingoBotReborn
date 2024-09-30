import json
import os

import discord
from discord import User
from discord.ui import View, Button

from active_context import base_user_folder
from utils import save_image, has_admin_role, send, register_all


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
            return await send(interaction, "Forbidden action.")

        guild_id = interaction.guild.id
        register_all(guild_id, self.team, self.submitter.id)
        await save_image(self.attachment, guild_id, self.submitter.id, self.tile, self.item, self.team)

        for button in self.children:
            button.disabled = True

        await interaction.message.edit(content=":white_check_mark: Approved! :white_check_mark:", view=self)
        await send(
            interaction,
            f"You have approved this submission!"
        )

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: Button):
        if not has_admin_role(interaction):
            return await send(interaction, "Forbidden action.")

        await send(interaction, f"You have rejected this submission!")

        for button in self.children:
            button.disabled = True

        await interaction.message.edit(content=":x: Rejected! :x:", view=self)


class RemoveButton(View):
    def __init__(self, guild_id: int, submission: dict, identifier: str, user_id: str, team: str = None):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.submission_type = submission['type']
        self.submission_value = submission['value']
        self.identifier = identifier
        self.user_id = user_id
        self.team = team

    @discord.ui.button(label="Remove", style=discord.ButtonStyle.danger)
    async def remove(self, interaction: discord.Interaction, button: Button):
        if not has_admin_role(interaction):
            return await send(interaction, "Forbidden action.")

        paths = [f"{base_user_folder}/{self.guild_id}/Users/{self.user_id}"]

        if self.team:
            paths.append(f"{base_user_folder}/{self.guild_id}/Teams/{self.team}")

        for path in paths:
            with open(path + '/entries.json', 'r') as json_file:
                data = json.load(json_file)

            for category, entries in data["entries"].items():
                for key, objects in entries.items():
                    data["entries"][category][key] = [obj for obj in objects if obj['identifier'] != self.identifier]

            try:
                os.remove(f"{path}/{self.identifier}.jpg")
                print('File removed')
            except Exception:
                pass

            with open(f"{path}/entries.json", 'w') as json_file:
                json_string = json.dumps(data)
                json_file.write(json_string)

        await send(
            interaction,
            f"Removed!"
        )

        for button in self.children:
            button.disabled = True

        await interaction.message.edit(content=":x: Removed! :x:", view=self)