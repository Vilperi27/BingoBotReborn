import json
import os

from discord.ext import commands
import bot_intents
from enums import AdminMode

command_prefix = '/'
intents = bot_intents.get_bot_intents()
client = commands.Bot(
    command_prefix=command_prefix, intents=intents
)
bingo_admin_roles = ["Leaders", "General", "Moderator", "Bingo Master"]
admin_users = [700413669011488810, 184022692867997697, 201768152982487041]
admin_mode = AdminMode.ID
base_user_folder = os.path.dirname(__file__)


async def read_json_data(json_file):
    with open(json_file, 'r') as file:
        return json.load(file)


async def write_json_data(json_file, data):
    with open(json_file, 'w') as file:
        json.dump(data, file)