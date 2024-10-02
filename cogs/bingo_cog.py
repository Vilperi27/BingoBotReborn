import io
import json
import math

import cv2
import discord
from PIL import Image
from discord import app_commands
from discord.ext import commands

import osrs_item_ids
from active_context import base_user_folder
from embeds import get_submission_embed
from utils import mention_user, has_admin_role, register_team, send, team_exists, get_submissions, get_completed_lines
from views import SubmissionButtons, RemoveButton


class BingoCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="register", description="Submit a tile image for a team or user.")
    @app_commands.describe(team="Team name")
    async def register(self, interaction, team: str):
        if not has_admin_role(interaction):
            return await send(interaction, "Forbidden action.")

        try:
            register_team(interaction.guild.id, team)
        except Exception:
            return await send(interaction, f"Team already exists!", ephemeral=True)

        await send(interaction, f"Team with the name of {team} was registered!", ephemeral=True)

    @app_commands.command(name="submit", description="Submit a tile image for a team or user.")
    @app_commands.describe(attachment="Image for the submission", tile="The tile number to submit (optional)", item="Item name (optional)", team="Team name or User ID (optional)")
    async def submit(self, interaction: discord.Interaction, attachment: discord.Attachment, tile: str = None, item: str = None, team: str = None):
        if tile is None and item is None:
            return await send(
                interaction,
                "You must provide either a tile number and/or an item."
            )

        if item:
            try:
                osrs_item_ids.get_item_by_name(item)
            except KeyError:
                return await send(
                    interaction,
                    "Item does not exist"
                )

        if team and not team_exists(interaction.guild.id, team):
            return await send(interaction, "Team does not exist.", ephemeral=True)

        embed = await get_submission_embed(interaction, attachment, tile, item, team)

        submit_buttons = SubmissionButtons(
            tile=tile,
            item=item,
            submitter=interaction.user,
            attachment=attachment,
            team=team
        )

        # Send the message with buttons and the embed
        await send(interaction, embed=embed, view=submit_buttons)

    @app_commands.command(name="complete", description="Complete a tile for a user or a team")
    @app_commands.describe(tile="Tile number", team="Team name")
    async def complete(self, interaction, tile: int, team: str):
        if not has_admin_role(interaction):
            return await send(interaction, "Forbidden action.")

        team_path = f"{base_user_folder}/{interaction.guild.id}/Teams/{team}"
        path = team_path + '/entries.json'

        # Load existing data from the JSON file if it exists
        try:
            with open(path, 'r') as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
            return await send(interaction, f"Team not found!", ephemeral=True)

        data['entries']['completed_tiles'].append(tile)

        with open(path, 'w') as json_file:
            json.dump(data, json_file, indent=4)  # Indent added for readability

        await send(interaction, f"Tile {tile} completed for the team {team}!", ephemeral=True)

    @app_commands.command(name="get", description="Get a submission for a specific item or tile")
    @app_commands.describe(tile="Tile number if item name is not provided (optional)", item="Item name if tile is not provided (optional)", team="Team name if userID is not provided (optional)", user_id="User ID if team name is not provided (optional)")
    async def get(self, interaction, tile: str = None, item: str = None, team: str = None, user_id: str = None):
        if not tile and not item:
            return await send(
                interaction,
                "You must provide either a tile number or an item."
            )

        if tile and item:
            return await send(
                interaction,
                "Please only provide either tile number or an item name."
            )

        if user_id and team:
            return await send(
                interaction,
                "Please only provide either user ID or an team name."
            )

        guild_id = interaction.guild.id

        if item:
            try:
                osrs_item_ids.get_item_by_name(item)
            except KeyError:
                return await send(
                    interaction,
                    "Item does not exist"
                )

        if team:
            path = f"{base_user_folder}/{guild_id}/Teams/{team}"
        else:
            path = f"{base_user_folder}/{guild_id}/Users/{user_id}"

        if tile:
            submission_type = 'Tile'
            submission = {'type': 'tiles', 'value': tile}
        else:
            submission_type = 'Item'
            submission = {'type': 'items', 'value': item}

        await interaction.response.send_message("Fetching submissions...", silent=True)

        submissions = get_submissions(path, submission)

        if len(submissions) == 0:
            return await interaction.edit_original_response(content="No submissions found.")

        for sub in submissions:
            submitter = sub['submitter']
            submitted = sub['submitted']
            identifier = sub['identifier']
            submission_value = submission['value']

            image_path = f"{base_user_folder}/{guild_id}/Users/{submitter}/{identifier}.jpg"

            with open(f'{image_path}', 'rb') as image:
                picture = discord.File(image)

                remove_button = RemoveButton(
                    guild_id=guild_id,
                    submission=submission,
                    identifier=identifier,
                    user_id=submitter,
                    team=team,
                )
                submitter = await self.client.fetch_user(submitter)

                # Send the message with buttons and the embed
                await interaction.channel.send(
                    content=f'Submitter: {submitter}\n'
                            f'{submission_type}: {submission_value}\n'
                            f'Submitted: {submitted}',
                    view=remove_button,
                    file=picture,
                    silent=True
                )

        return await interaction.edit_original_response(content=f"{len(submissions)} submissions found.")

    @app_commands.command(name="board", description="Get the current board status for a team")
    @app_commands.describe(team="Team name")
    async def board(self, interaction, team: str):
        team_path = f"{base_user_folder}/{interaction.guild.id}/Teams/{team}"
        path = team_path + '/entries.json'

        # Load existing data from the JSON file if it exists
        try:
            with open(path, 'r') as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
            return await send(interaction, f"Team not found!", ephemeral=True)

        entries = data['entries']['completed_tiles']

        init_offset_x = 140
        init_offset_y = 185
        steps_x = [9, 9, 0]
        steps_y = [11, 12, 0]
        board_size = 3
        matrix = [['' for _ in range(board_size)] for _ in range(board_size)]

        if entries:
            entries = sorted(entries, key=int)

        if entries:
            for value in entries:
                value = int(value)
                value -= 1
                x = value % board_size
                y = math.floor(value / board_size)
                matrix[y][x] = 'X'

        completed_rows = get_completed_lines(matrix)

        image = cv2.imread('MollysRaidBingo.png')

        offset_y = init_offset_y

        for index_r, row in enumerate(matrix):
            offset_x = init_offset_x
            for index_c, value in enumerate(row):
                if value == 'X':
                    image = cv2.rectangle(image, (offset_x, offset_y), (offset_x + 235, offset_y + 228), (0, 255, 0),
                                          5)
                offset_x += steps_x[index_c] + 235

            offset_y += steps_y[index_r] + 228

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        im_pil = Image.fromarray(image)

        with io.BytesIO() as image_binary:
            im_pil.save(image_binary, 'PNG')
            image_binary.seek(0)
            await interaction.response.send_message(
                content='\n'.join(completed_rows),
                file=discord.File(fp=image_binary, filename='image.png'),
                silent=True
            )


async def setup(client):
    bingo_utils = BingoCog(client)
    await client.add_cog(bingo_utils)
