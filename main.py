import discord
from discord.ext import commands
from typing import Final
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

async def main():
    async with bot:
        await load()
        await bot.start(token=TOKEN)

@bot.event
async def on_ready():
    print('Bot online.')

    try:
        sync_commands = await bot.tree.sync()
        print(f'Synced {len(sync_commands)} commands.')
    except Exception as e:
        print('An syncing error has occured: ', e)

asyncio.run(main())
