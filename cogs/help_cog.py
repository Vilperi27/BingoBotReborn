import discord
from discord.ext import commands

from active_context import command_prefix


class HelpCog(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def help(self, ctx):
        help_info = ''

        help_info += (f'{command_prefix}submit tile [team name, optional] - Submits an entry for a specific tile for '
                      f'the bingo admin to review.\nExample:\n{command_prefix}submit 7\nOr\n{command_prefix}submit 7 '
                      f'Magnificent Elves\n\n')

        help_info += (f'{command_prefix}get tile [user_id or team name] - Gets a specific tile entry for a user or '
                      f'team.\nExample:\n{command_prefix}get 7 201768152982487041\nOr\n{command_prefix}get 7 '
                      f'Magnificent Elves\n\n')

        help_info += (f'{command_prefix}get_all [user_id or team name] - Gets all entries for a specific '
                      f'user.\nExample:\n{command_prefix}get_all 201768152982487041\nOr\n{command_prefix}get_all '
                      f'Magnificent Elves\n\n')

        help_info += (f'{command_prefix}register_team [team name] - Registers a team with a specific name to the bingo '
                      f'bot.\nExample:\n{command_prefix}register_team Magnificent Elves\n\n')

        help_info += (f'{command_prefix}remove tile [user_id or team name] - (ADMIN ONLY) Removes a specific tile for '
                      f'user.\nExample:\n{command_prefix}remove 7 201768152982487041\nOr\n{command_prefix}remove 7 '
                      f'Magnificent Elves\n\n')

        help_info += (f'Note: You can get the user_id from right clicking the user on discord and selecting "Copy User '
                      f'ID"\n\n')

        help_embed = discord.Embed(color=discord.Color.blurple(), description=help_info)
        await ctx.send(embed=help_embed)


async def setup(client):
    help_cog = HelpCog(client)
    await client.add_cog(help_cog)