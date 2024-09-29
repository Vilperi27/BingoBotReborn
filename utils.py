import uuid
from datetime import datetime
import os
import json

import discord
from discord import Interaction, Attachment
from discord.types.embed import Embed
from discord.ui import View

import active_context
from active_context import base_user_folder, bingo_admin_roles
from enums import AdminMode


def guild_exists(guild_id):
    return os.path.isdir(f"{base_user_folder}/{guild_id}")


def team_exists(guild_id: int, team: str):
    path = f"{base_user_folder}/{guild_id}/Teams/{team}"
    return os.path.isdir(path)


def user_exists(guild_id: int, user_id: int):
    path = f"{base_user_folder}/{guild_id}/Users/{user_id}"
    return os.path.isdir(path)


def register_guild(guild_id: int):
    guild_path = f"{base_user_folder}/{guild_id}"

    if not os.path.isdir(guild_path):
        os.mkdir(guild_path)

    if not os.path.isdir(f'{guild_path}/Users'):
        os.mkdir(guild_path + '/Users')

    if not os.path.isdir(f'{guild_path}/Teams'):
        os.mkdir(guild_path + '/Teams')


def register_team(guild_id: int, team: str):
    register_guild(guild_id)
    team_path = f"{base_user_folder}/{guild_id}/Teams/{team}"
    os.mkdir(team_path)
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


def register_user(guild_id, user_id, team: str = None):
    user_path = f"{base_user_folder}/{guild_id}/Users/{user_id}"
    os.mkdir(user_path)
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


def register_all(guild_id: int, team: str, submitter_id: int):
    if not guild_exists(guild_id):
        register_guild(guild_id)

    if team:
        if not team_exists(guild_id, team):
            register_team(guild_id, team)

    if not user_exists(guild_id, submitter_id):
        register_user(guild_id, submitter_id)


async def create_team_submit_entry(path: str, submitter_id: int, identifier: str, tile: str = None, item: str = None):
    path = path + '/entries.json'
    file_exists = os.path.isfile(path)

    # If file exists, append the new entry to the json file,
    # If no entries exist, create the json-file.
    if file_exists:
        with open(path, 'r') as json_file:
            data = json.load(json_file)

        submission_data = {
            'submitter': submitter_id,
            'submitted': datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
            'identifier': identifier
        }

        if tile:
            if not data['entries']['tiles'].get(tile):
                data['entries']['tiles'] = {tile: []}
            data['entries']['tiles'][tile].append(submission_data)

        if item:
            if not data['entries']['items'].get(item):
                data['entries']['items'] = {item: []}
            data['entries']['items'][item].append(submission_data)

        with open(path, 'w') as json_file:
            json_string = json.dumps(data)
            json_file.write(json_string)
    else:
        with open(path, "a+") as f:
            data = {
                'entries': {
                    'tiles': {},
                    'items': {}
                }
            }

            if tile:
                data['entries']['tiles'][tile] = [
                    {
                        'submitter': submitter_id,
                        'submitted': datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
                        'identifier': identifier
                    }
                ]

            if item:
                data['entries']['items'][item] = [
                    {
                        'submitter': submitter_id,
                        'submitted': datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
                        'identifier': identifier
                    }
                ]

            json_string = json.dumps(data)
            f.write(json_string)


async def create_user_submit_entry(path: str, submitter_id: int, tile: str = None, item: str = None):
    generated_identifier = str(uuid.uuid4())
    path = path + '/entries.json'
    file_exists = os.path.isfile(path)

    # If file exists, append the new entry to the json file,
    # If no entries exist, create the json-file.
    if file_exists:
        with open(path, 'r') as json_file:
            data = json.load(json_file)

        submission_data = {
            'submitter': submitter_id,
            'submitted': datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
            'identifier': generated_identifier
        }

        if tile:
            if not data['entries']['tiles'].get(tile):
                data['entries']['tiles'] = {tile: []}
            data['entries']['tiles'][tile].append(submission_data)

        if item:
            if not data['entries']['items'].get(item):
                data['entries']['items'] = {item: []}
            data['entries']['items'][item].append(submission_data)

        with open(path, 'w') as json_file:
            json_string = json.dumps(data)
            json_file.write(json_string)
    else:
        with open(path, "a+") as f:
            data = {
                'entries': {
                    'tiles': {},
                    'items': {}
                }
            }

            if tile:
                data['entries']['tiles'][tile] = [
                    {
                        'submitter': submitter_id,
                        'submitted': datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
                        'identifier': generated_identifier
                    }
                ]

            if item:
                data['entries']['items'][item] = [
                    {
                        'submitter': submitter_id,
                        'submitted': datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
                        'identifier': generated_identifier
                    }
                ]

            json_string = json.dumps(data)
            f.write(json_string)

    return generated_identifier


async def save_image(attachment: Attachment, guild_id: int, submitter_id: int, tile: str = None, item: str = None, team: str = None):
    user_path = f"{base_user_folder}/{guild_id}/Users/{submitter_id}"
    identifier = await create_user_submit_entry(user_path, submitter_id, tile, item)

    if team:
        team_path = f"{base_user_folder}/{guild_id}/Teams/{team}"
        await create_team_submit_entry(team_path, submitter_id, identifier, tile, item)

    await attachment.save(f'{user_path}/{identifier}.jpg')


def mention_user(user_id: int):
    return f'<@{user_id}>'


def has_admin_role(interaction):
    if active_context.admin_mode == AdminMode.ROLE:
        if isinstance(interaction, Interaction):
            user_roles = interaction.user.roles
        else:
            user_roles = interaction.author.roles

        for admin_role in bingo_admin_roles:
            if discord.utils.get(interaction.guild.roles, name=admin_role) in user_roles:
                return True

    if active_context.admin_mode == AdminMode.ID:
        if isinstance(interaction, Interaction):
            return interaction.user.id in active_context.admin_users
        else:
            return interaction.author.id in active_context.admin_users

    return False


async def send(interaction: Interaction, message: str = '', silent: bool = True, ephemeral: bool = True, embed: Embed = None, view: View = None):
    if view:
        await interaction.response.send_message(message, silent=silent, embed=embed, view=view)
    elif embed:
        await interaction.response.send_message(message, silent=silent, embed=embed)
    else:
        await interaction.response.send_message(message, silent=silent, ephemeral=ephemeral)


def get_submissions(path: str, submission: dict):
    submission_type = submission['type']
    value = submission['value']
    submissions = []

    with open(path + '/entries.json', 'r') as json_file:
        data = json.load(json_file)

    try:
        for entry in data["entries"][submission_type][value]:
            submissions.append(entry)
    except KeyError:
        pass

    return submissions

