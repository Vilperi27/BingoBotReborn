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

    # Load existing data from the JSON file if it exists
    try:
        with open(path, 'r') as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        # If the file doesn't exist, initialize the structure
        data = {'entries': {'tiles': {}, 'items': {}}}

    # Create the submission data
    submission_data = {
        'submitter': submitter_id,
        'submitted': datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
        'identifier': identifier
    }

    # Handle the tile submission
    if tile:
        # If the key for the tile doesn't exist, create an empty list for it
        if tile not in data['entries']['tiles']:
            data['entries']['tiles'][tile] = []
        # Append the new submission to the tile's list
        data['entries']['tiles'][tile].append(submission_data)

    # Handle the item submission
    if item:
        # If the key for the item doesn't exist, create an empty list for it
        if item not in data['entries']['items']:
            data['entries']['items'][item] = []
        # Append the new submission to the item's list
        data['entries']['items'][item].append(submission_data)

    # Write the updated data back to the file
    with open(path, 'w') as json_file:
        json.dump(data, json_file, indent=4)  # Indent added for readability


async def create_user_submit_entry(path: str, submitter_id: int, tile: str = None, item: str = None):
    generated_identifier = str(uuid.uuid4())
    path = path + '/entries.json'

    # Load existing data from the JSON file if it exists
    try:
        with open(path, 'r') as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        # If the file doesn't exist, initialize the structure
        data = {'entries': {'tiles': {}, 'items': {}}}

    # Create the submission data
    submission_data = {
        'submitter': submitter_id,
        'submitted': datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
        'identifier': generated_identifier
    }

    # Handle the tile submission
    if tile:
        # If the key for the tile doesn't exist, create an empty list for it
        if tile not in data['entries']['tiles']:
            data['entries']['tiles'][tile] = []
        # Append the new submission to the tile's list
        data['entries']['tiles'][tile].append(submission_data)

    # Handle the item submission
    if item:
        # If the key for the item doesn't exist, create an empty list for it
        if item not in data['entries']['items']:
            data['entries']['items'][item] = []
        # Append the new submission to the item's list
        data['entries']['items'][item].append(submission_data)

    # Write the updated data back to the file
    with open(path, 'w') as json_file:
        json.dump(data, json_file, indent=4)  # Indent added for readability

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


def get_completed_lines(matrix, as_data=False):
    fully_completed_rows = [row for row in matrix if all(cell == 'X' for cell in row)]
    fully_completed_columns = [list(column) for column in zip(*matrix) if all(cell == 'X' for cell in column)]
    fully_completed_diagonals = []

    main_diagonal = [matrix[i][i] for i in range(min(len(matrix), len(matrix[0]))) if matrix[i][i] == 'X']
    if len(main_diagonal) == min(len(matrix), len(matrix[0])):
        fully_completed_diagonals.append(main_diagonal)

    anti_diagonal = [matrix[i][len(matrix[0]) - 1 - i] for i in range(min(len(matrix), len(matrix[0]))) if matrix[i][len(matrix[0]) - 1 - i] == 'X']
    if len(anti_diagonal) == min(len(matrix), len(matrix[0])):
        fully_completed_diagonals.append(anti_diagonal)

    if as_data:
            return [len(fully_completed_rows), len(fully_completed_columns), len(fully_completed_diagonals)]
    return f'Rows completed: {len(fully_completed_rows)}', f'Columns completed: {len(fully_completed_columns)}', f'Diagonals completed: {len(fully_completed_diagonals)}'