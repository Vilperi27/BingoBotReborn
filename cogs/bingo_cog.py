import json
import os

import discord
from discord import app_commands
from discord.ext import commands

import osrs_item_ids
from active_context import base_user_folder
from embeds import get_submission_embed
from utils import mention_user, has_admin_role, register_team, send, team_exists
from views import SubmissionButtons


class BingoCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="register", description="Submit a tile image for a team or user.")
    @app_commands.describe(team="Team name")
    async def register(self, ctx, team: str):
        if not has_admin_role(ctx):
            return await send(ctx, "Forbidden action.")

        register_team(ctx.guild.id, team)
        await send(ctx, f"Team with the name of {team} was registered!", ephemeral=True)

    @app_commands.command(name="submit", description="Submit a tile image for a team or user.")
    @app_commands.describe(attachment="Image for the submission", tile="The tile number to submit (optional)", item="Item name (optional)", team="Team name or User ID (optional)")
    async def submit(self, interaction: discord.Interaction, attachment: discord.Attachment, tile: str = None, item: str = None, team: str = None):
        if tile is None and item is None:
            return await send(
                interaction,
                "You must provide either a tile number and/or an item.",
                ephemeral=True
            )

        if item:
            try:
                osrs_item_ids.get_item_by_name(item)
            except KeyError:
                return await send(
                    interaction,
                    "Item does not exist",
                    ephemeral=True
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

    @app_commands.command(name="get", description="Get a submission for a specific item or tile")
    @app_commands.describe(tile="Tile number if item name is not provided (optional)", item="Item name if tile is not provided (optional)", team="Team name if userID is not provided (optional)", user_id="User ID if team name is not provided (optional)")
    async def get(self, ctx, tile: int = None, item: str = None, team: str = None, user_id: str = None):
        if not tile and not item:
            await ctx.response.send_message(
                "You must provide either a tile number or an item.",
                ephemeral=True
            )
            return

        if tile and item:
            await ctx.response.send_message(
                "Only provide either tile number or item name.",
                ephemeral=True
            )
            return

        if team:
            path = f"{base_user_folder}{ctx.guild.id}/Teams/{team}"
        else:
            path = f"{base_user_folder}{ctx.guild.id}/Users/{user_id}"
        file_exists = os.path.isdir(path)

        # If the account and entry exists, get the given entry and return the submission image
        # With the name of the account, tile number and time of submission.
        if not file_exists:
            await ctx.response.send_message(
                'User or team does not exist, make sure to use the correct id or name.',
                ephemeral=True
            )
            return

        with open(path + '/entries.json', 'r') as json_file:
            data = json.load(json_file)

        submission_time = "N/A"
        submitter = None
        matching_files = []

        if tile:
            image_path = f"{base_user_folder}{ctx.guild.id}/Users/{user_id}"
            for entry in data["entries"]:
                if entry["tile"] == tile:
                    matching_files.append(f'{tile}.jpg')
                    submitter = entry["submitter"]
                    submission_time = entry["submitted"]
                    break
        else:
            for entry in data["entries"]:
                if item in str(entry["tile"]):
                    submitter = entry["submitter"]
                    submission_time = entry["submitted"]
                    break

            image_path = f"{base_user_folder}{ctx.guild.id}/Users/{submitter}"

            for filename in os.listdir(image_path):
                if item in filename:
                    matching_files.append(filename)

        tile_name = item if item else tile

        for file in matching_files:
            with open(f'{image_path}/{file}', 'rb') as f:
                picture = discord.File(f)
                await ctx.channel.send(
                    content='Submitter: %s\nTile: %s\nSubmitted: %s' % (mention_user(submitter), tile_name, submission_time),
                    file=picture,
                    silent=True
                )

    @commands.command()
    async def get_all(self, ctx, *user_id_or_team):
        user_id_or_team = " ".join(user_id_or_team[:])

        if isinstance(user_id_or_team, str):
            path = f"{base_user_folder}{ctx.message.guild.id}/Teams/{user_id_or_team}"
            is_team = True
        else:
            path = f"{base_user_folder}{ctx.message.guild.id}/Users/{user_id_or_team}"
            is_team = False
        file_exists = os.path.isdir(path)

        # If account exists, get all the entries from the json-file.
        if not file_exists:
            await ctx.response.send_message('User or team does not exist, make sure to use the correct id or name.')
            return
        else:
            with open(path + '/entries.json', 'r') as json_file:
                data = json.load(json_file)

            entries = []
            for entry in data['entries']:
                entries.append(entry['tile'])

            if entries:
                entries = sorted(entries, key=int)
                entries = ','.join(map(str, entries))

                if is_team:
                    await ctx.response.send_message(f'Entries for {user_id_or_team} exist for tiles: {entries}', silent=True)
                else:
                    await ctx.response.send_message(f'Entries for {mention_user(user_id_or_team)} exist for tiles: {entries}', silent=True)
            else:
                await ctx.response.send_message('No entries found')

    @commands.command()
    async def remove(self, ctx, tile: int, *user_id_or_team):
        user_id_or_team = " ".join(user_id_or_team[:])

        if not has_admin_role(ctx):
            await ctx.response.send_message("Forbidden action.", silent=True)
            return

        if isinstance(user_id_or_team, str):
            path = f"{base_user_folder}{ctx.message.guild.id}/Teams/{user_id_or_team}"
            is_team = True
        else:
            path = f"{base_user_folder}{ctx.message.guild.id}/Users/{user_id_or_team}"
            is_team = False

        file_exists = os.path.isdir(path)

        if not file_exists:
            await ctx.response.send_message('User or team does not exist, make sure to use the correct id or name.')
            return

        with open(path + '/entries.json', 'r') as json_file:
            data = json.load(json_file)

        if len(data['entries']) == 0:
            await ctx.response.send_message(f"{user_id_or_team} does not have any submissions.", silent=True)
            return

        submitter = None

        for index, entry in enumerate(data['entries']):
            if entry['tile'] == tile:

                if is_team:
                    submitter = entry['submitter']

                del data['entries'][index]
                with open(path + '/entries.json', 'w') as json_file:
                    json_string = json.dumps(data)
                    json_file.write(json_string)
                break

            if index == len(data['entries']) - 1:
                return

        if not is_team:
            os.remove(f'{path}/{tile}.jpg')

        if is_team:
            user_path = f"{base_user_folder}{ctx.message.guild.id}/Users/{submitter}"
            with open(user_path + '/entries.json', 'r') as json_file:
                data = json.load(json_file)

            for index, entry in enumerate(data['entries']):
                if entry['tile'] == tile:
                    del data['entries'][index]
                    with open(user_path + '/entries.json', 'w') as json_file:
                        json_string = json.dumps(data)
                        json_file.write(json_string)
                    break

                if index == len(data['entries']) - 1:
                    return

            os.remove(f'{user_path}/{tile}.jpg')
        await ctx.response.send_message(f"Tile {tile} removed for {user_id_or_team}", silent=True)


async def setup(client):
    bingo_utils = BingoCog(client)
    await client.add_cog(bingo_utils)
