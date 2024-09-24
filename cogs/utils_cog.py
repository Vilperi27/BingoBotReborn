from discord.ext import commands

import active_context
from enums import AdminMode


class UtilCog(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def set_admin_mode(self, ctx, mode: int):
        if not ctx.author.id == 201768152982487041:
            await ctx.send("Nice try")
            return

        active_context.admin_mode = AdminMode(mode)
        await ctx.send(f"Admin mode set to {AdminMode(mode).name}")


async def setup(client):
    util_cog = UtilCog(client)
    await client.add_cog(util_cog)