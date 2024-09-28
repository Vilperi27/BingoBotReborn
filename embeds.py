import discord

from utils import send


async def get_submission_embed(ctx, attachment, tile, item, team):
    if not attachment.content_type.startswith('image/'):
        return await send(ctx, "Please submit a valid image!")

    if team:
        title = f"Submission for the team {team}"
    else:
        title = f"Submission for {ctx.user}"

    description = ""

    if tile:
        description += f"Tile: {tile}\n"
    if item:
        description += f"Item: {item}\n"

    description += f"Submitted by {ctx.user.mention}"

    embed = discord.Embed(
        title=title,
        description=description
    )
    embed.set_image(url=attachment.url)
    embed.colour = discord.Colour.light_grey()
    embed.set_footer(
        text=f"Bingo admin will approve or reject your submission."
    )

    return embed