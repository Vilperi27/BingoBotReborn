from datetime import datetime
import os
import json

import discord
import requests
from discord import Interaction

from active_context import base_user_folder, bingo_admin_roles
from errors import TileExistsError


async def register_user(guild_id, user_id, team: str = None):
    guild_path = f"{base_user_folder}{guild_id}"

    if not os.path.isdir(guild_path):
        os.mkdir(guild_path)
        os.mkdir(guild_path + '/Users')
        os.mkdir(guild_path + '/Teams')

    user_path = f"{base_user_folder}{guild_id}/Users/{user_id}"
    user_file_exists = os.path.isdir(user_path)

    if team:
        team_path = f"{base_user_folder}{guild_id}/Teams/{team}"
        team_file_exists = os.path.isdir(team_path)

        if not team_file_exists:
            os.mkdir(team_path)

            # Specify the path to point to a json-file
            path = team_path + '/team_details.json'
            with open(path, "a+") as f:
                data = {
                    'team_details': [
                        {
                            'name': team,
                            'created': datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                        }
                    ]
                }

                json_string = json.dumps(data)
                f.write(json_string)

    if not user_file_exists:
        os.mkdir(user_path)

        # Specify the path to point to a json-file
        path = user_path + '/user_details.json'
        with open(path, "a+") as f:
            data = {
                'user_details': [
                    {
                        'name': user_id,
                        'created': datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                    }
                ]
            }

            json_string = json.dumps(data)
            f.write(json_string)


async def create_submit_entry(path: str, tile: int, submitter: str, overwrite=False):
    path = path + '/entries.json'
    file_exists = os.path.isfile(path)

    # If file exists, append the new entry to the json file,
    # If no entries exist, create the json-file.
    if file_exists:
        with open(path, 'r') as json_file:
            data = json.load(json_file)

        tile_exists = False
        found_tile_index = -1

        for index, entry in enumerate(data['entries']):
            if entry['tile'] == tile:
                tile_exists = True
                found_tile_index = index
                break

        if tile_exists and not overwrite:
            raise TileExistsError("Tile already exists for that id.")

        if not tile_exists:
            data['entries'].append({
                'tile': tile,
                'submitter': submitter,
                'submitted': datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
            })
        else:
            data['entries'][found_tile_index]['tile'] = tile
            data['entries'][found_tile_index]['submitter'] = submitter
            data['entries'][found_tile_index]['submitted'] = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

        with open(path, 'w') as json_file:
            json_string = json.dumps(data)
            json_file.write(json_string)
    else:
        with open(path, "a+") as f:
            data = {
                'entries': [
                    {
                        'tile': tile,
                        'submitter': submitter,
                        'submitted': datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                    }
                ]
            }

            json_string = json.dumps(data)
            f.write(json_string)


async def save_image(ctx, submitter_id, tile, image_url, overwrite=False, team: str = None):
    user_path = f"{base_user_folder}{ctx.message.guild.id}/Users/{submitter_id}"

    try:
        img_data = requests.get(image_url).content
    except Exception:
        await ctx.response.send_message("No image provided, entry must have an image attached", ephemeral=True)
        return

    await create_submit_entry(user_path, tile, str(submitter_id), overwrite)

    if team:
        team_path = f"{base_user_folder}{ctx.message.guild.id}/Teams/{team}"
        await create_submit_entry(team_path, tile, str(submitter_id), overwrite)

    # If the account exists, create an image entry of the submission
    with open(user_path + '/' + str(tile) + '.jpg', 'wb') as handler:
        handler.write(img_data)
        handler.truncate()


def mention_user(user_id: int):
    return f'<@{user_id}>'


def has_admin_role(interaction):
    if isinstance(interaction, Interaction):
        user_roles = interaction.user.roles
    else:
        user_roles = interaction.author.roles

    for admin_role in bingo_admin_roles:
        if discord.utils.get(interaction.guild.roles, name=admin_role) in user_roles:
            return True
    return False