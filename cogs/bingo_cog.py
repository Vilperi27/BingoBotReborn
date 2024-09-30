import json
import os

import discord
from discord import app_commands
from discord.ext import commands

import osrs_item_ids
from active_context import base_user_folder
from embeds import get_submission_embed
from utils import mention_user, has_admin_role, register_team, send, team_exists, get_submissions
from views import SubmissionButtons, RemoveButton


class BingoCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="register", description="Submit a tile image for a team or user.")
    @app_commands.describe(team="Team name")
    async def register(self, ctx, team: str):
        if not has_admin_role(ctx):
            return await send(ctx, "Forbidden action.")

        try:
            register_team(ctx.guild.id, team)
        except Exception:
            return await send(ctx, f"Team already exists!", ephemeral=True)

        await send(ctx, f"Team with the name of {team} was registered!", ephemeral=True)

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

                # Send the message with buttons and the embed
                await interaction.channel.send(
                    content=f'Submitter: {mention_user(submitter)}\n'
                            f'{submission_type}: {submission_value}\n'
                            f'Submitted: {submitted}',
                    view=remove_button,
                    file=picture,
                    silent=True
                )

        return await interaction.edit_original_response(content=f"{len(submissions)} submissions found.")


async def setup(client):
    bingo_utils = BingoCog(client)
    await client.add_cog(bingo_utils)
