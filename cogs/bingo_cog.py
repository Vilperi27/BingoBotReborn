import json
import os

import discord
from discord.ext import commands

from active_context import base_user_folder
from embeds import get_submission_embed
from utils import mention_user, has_admin_role, register_team
from views import SubmissionButtons, OverwriteButtons


class BingoCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def register_team(self, ctx, *user_id_or_team):
        if not has_admin_role(ctx):
            await ctx.send("Forbidden action.", silent=True)
            return

        team = " ".join(user_id_or_team[:])
        if len(team) == 0:
            await ctx.send("No name given", silent=True)
            return

        await register_team(ctx.message.guild.id, team)
        await ctx.send(f"Team with the name of {team} was registered!")

    @commands.command()
    async def submit(self, ctx, tile: int, *user_id_or_team):
        if team := " ".join(user_id_or_team[:]):
            path = f"{base_user_folder}{ctx.message.guild.id}/Teams/{team}"
            file_exists = os.path.isdir(path)
            if not file_exists:
                await ctx.send("Team does not exist.", silent=True)
                return

        path = f"{base_user_folder}{ctx.message.guild.id}/Users/{ctx.author.id}/{tile}.jpg"
        file_exists = os.path.isfile(path)

        embed = await get_submission_embed(ctx, tile, team, file_exists)

        if file_exists:
            submit_buttons = OverwriteButtons(
                tile=tile,
                submitter=ctx.author,
                image_url=ctx.message.aFttachments[0].url,
                team=team
            )
        else:
            submit_buttons = SubmissionButtons(
                tile=tile,
                submitter=ctx.author,
                image_url=ctx.message.attachments[0].url,
                team=team
            )

        await ctx.send(view=submit_buttons, embed=embed)

    @commands.command()
    async def get(self, ctx, tile: int, *user_id_or_team):
        user_id_or_team = " ".join(user_id_or_team[:])

        if isinstance(user_id_or_team, str):
            path = f"{base_user_folder}{ctx.message.guild.id}/Teams/{user_id_or_team}"
        else:
            path = f"{base_user_folder}{ctx.message.guild.id}/Users/{user_id_or_team}"
        file_exists = os.path.isdir(path)

        # If the account and entry exists, get the given entry and return the submission image
        # With the name of the account, tile number and time of submission.
        if not file_exists:
            await ctx.send('User or team does not exist, make sure to use the correct id or name.')
            return
        else:
            with open(path + '/entries.json', 'r') as json_file:
                data = json.load(json_file)

            submission_time = "N/A"
            submitter = None

            for entry in data["entries"]:
                if entry["tile"] == tile:
                    submitter = entry["submitter"]
                    submission_time = entry["submitted"]
                    break

            image_path = f"{base_user_folder}{ctx.message.guild.id}/Users/{submitter}"

            with open(f'{image_path}/{tile}.jpg', 'rb') as f:
                picture = discord.File(f)
                await ctx.channel.send(
                    content='Submitter: %s\nTile: %s\nSubmitted: %s' % (mention_user(submitter), tile, submission_time),
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
            await ctx.send('User or team does not exist, make sure to use the correct id or name.')
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
                    await ctx.send(f'Entries for {user_id_or_team} exist for tiles: {entries}', silent=True)
                else:
                    await ctx.send(f'Entries for {mention_user(user_id_or_team)} exist for tiles: {entries}', silent=True)
            else:
                await ctx.send('No entries found')

    @commands.command()
    async def remove(self, ctx, tile: int, *user_id_or_team):
        user_id_or_team = " ".join(user_id_or_team[:])

        if not has_admin_role(ctx):
            await ctx.send("Forbidden action.", silent=True)
            return

        if isinstance(user_id_or_team, str):
            path = f"{base_user_folder}{ctx.message.guild.id}/Teams/{user_id_or_team}"
            is_team = True
        else:
            path = f"{base_user_folder}{ctx.message.guild.id}/Users/{user_id_or_team}"
            is_team = False

        file_exists = os.path.isdir(path)

        if not file_exists:
            await ctx.send('User or team does not exist, make sure to use the correct id or name.')
            return

        with open(path + '/entries.json', 'r') as json_file:
            data = json.load(json_file)

        if len(data['entries']) == 0:
            await ctx.send(f"{user_id_or_team} does not have any submissions.", silent=True)
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
        await ctx.send(f"Tile {tile} removed for {user_id_or_team}", silent=True)


async def setup(client):
    bingo_utils = BingoCog(client)
    await client.add_cog(bingo_utils)
