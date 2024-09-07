import discord
from discord.ext import commands

from active_context import command_prefix


class HelpCog(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def help(self, ctx):
        help_info = ''
        help_info += f'{command_prefix}submit tile - Submits an entry for a specific tile for the bingo admin to review.\nExample: {command_prefix}submit 7\n\n'
        help_info += f'You can get the user_id from right clicking the user on discord and selecting "Copy User ID"\n\n'
        help_info += f'{command_prefix}get tile user_id - Gets a specific tile entry for a user.\nExample: {command_prefix}get 7 201768152982487041\n\n'
        help_info += f'{command_prefix}get_all user_id - Gets all entries for a specific user.\nExample: {command_prefix}get_all 201768152982487041\n\n'
        help_info += f'{command_prefix}remove tile user_id - (ADMIN ONLY) Removes a specific tile for user.\nExample: {command_prefix}remove 7 201768152982487041\n\n'

        help_embed = discord.Embed(color=discord.Color.blurple(), description=help_info)
        await ctx.send(embed=help_embed)


async def setup(client):
    help_cog = HelpCog(client)
    await client.add_cog(help_cog)