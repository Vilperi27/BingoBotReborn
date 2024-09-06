import discord


async def get_submission_embed(ctx, tile_number):
    if not ctx.message.attachments:
        await ctx.send("Please attach an image with your submission!")
        return

    attachment = ctx.message.attachments[0]

    if not attachment.content_type.startswith('image/'):
        await ctx.send("Please submit a valid image!")
        return

    embed = discord.Embed(title=f"Submission for tile {tile_number}", description=f"Submitted by {ctx.author.mention}")
    embed.set_image(url=attachment.url)
    embed.description = f"Submission for tile {tile_number}"
    embed.colour = discord.Colour.light_grey()
    embed.set_footer(
        text=f"Bingo admin will approve or reject your submission."
    )
    return embed