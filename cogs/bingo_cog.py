import json
import os

import discord
from discord.ext import commands

from active_context import base_user_folder
from embeds import get_submission_embed
from utils import mention_user
from views import SubmissionButtons


class BingoCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def submit(self, ctx, tile: int):
        embed = await get_submission_embed(ctx, tile)
        queue_buttons = SubmissionButtons(tile=tile, submitter=ctx.author, image_url=ctx.message.attachments[0].url)
        await ctx.send(view=queue_buttons, embed=embed)

    @commands.command()
    async def get(self, ctx, tile: int, user_id: int):
        path = f"{base_user_folder}{ctx.message.guild.id}/Users/{user_id}"
        file_exists = os.path.isdir(path)

        # If the account and entry exists, get the given entry and return the submission image
        # With the name of the account, tile number and time of submission.
        if not file_exists:
            await ctx.send('User does not exist, make sure to use the correct UserID.')
            return
        else:
            with open(path + '/entries.json', 'r') as json_file:
                data = json.load(json_file)

            submission_time = "N/A"

            for entry in data["entries"]:
                if entry["tile"] == tile:
                    submission_time = entry["submitted"]
                    break

            with open(f'{path}/{tile}.jpg', 'rb') as f:
                picture = discord.File(f)
                await ctx.channel.send(
                    content='Name: %s\nTile: %s\nSubmitted: %s' % (mention_user(user_id), tile, submission_time),
                    file=picture,
                    silent=True
                )

    @commands.command()
    async def get_all(self, ctx, user_id: int):
        try:
            path = f"{base_user_folder}{ctx.message.guild.id}/Users/{user_id}"
            file_exists = os.path.isdir(path)

            # If account exists, get all the entries from the json-file.
            if not file_exists:
                await ctx.send('User does not exist, make sure to use the correct UserID.')
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
                    await ctx.send(f'Entries for {mention_user(user_id)} exist for tiles: {entries}', silent=True)
                else:
                    await ctx.send('No entries found')
        except Exception as e:
            print(e)

    @commands.command()
    async def remove(self, ctx, tile: int, user_id):
        try:
            path = f"{base_user_folder}{ctx.message.guild.id}/Users/{user_id}"
            file_exists = os.path.isdir(path)

            if not file_exists:
                await ctx.send('User does not exist, make sure to use the correct UserID.')
                return

            with open(path + '/entries.json', 'r') as json_file:
                data = json.load(json_file)

            if len(data['entries']) == 0:
                await ctx.send(f"The user {mention_user(user_id)} does not have any submissions.", silent=True)
                return

            for index, entry in enumerate(data['entries']):
                if entry['tile'] == tile:
                    del data['entries'][index]
                    with open(path + '/entries.json', 'w') as json_file:
                        json_string = json.dumps(data)
                        json_file.write(json_string)
                    break

                if index == len(data['entries']) - 1:
                    await ctx.send(f"Tile {tile} does not exist for user {mention_user(user_id)}", silent=True)
                    return

            os.remove(f'{path}/{tile}.jpg')

            await ctx.send(f"Tile {tile} removed for user {mention_user(user_id)}", silent=True)
        except Exception as e:
            print(e)


async def setup(client):
    bingo_utils = BingoCog(client)
    await client.add_cog(bingo_utils)