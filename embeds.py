import discord


async def get_submission_embed(ctx, attachment, tile_number, item, team, overwrite=False):
    if not attachment:
        await ctx.response.send_message("Please attach an image with your submission!")
        return

    if not attachment.content_type.startswith('image/'):
        await ctx.response.send_message("Please submit a valid image!")
        return

    if item:
        submission = item
    else:
        submission = tile_number

    if team:
        embed = discord.Embed(
            title=f"Submission for {submission} for {team}",
            description=f"Submitted by {ctx.user.mention}"
        )
    else:
        embed = discord.Embed(
            title=f"Submission for {submission}",
            description=f"Submitted by {ctx.user.mention}"
        )
    embed.set_image(url=attachment.url)
    embed.colour = discord.Colour.light_grey()

    if overwrite:
        embed.set_footer(
            text=f"Submission already exists, please confirm the previous submission before overwriting. "
                 f"Bingo admin will approve and ovewrite or reject your submission."
        )
    else:
        embed.set_footer(
            text=f"Bingo admin will approve or reject your submission."
        )
    return embed