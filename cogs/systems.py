import discord
from discord import app_commands
from discord.ext import commands
from util.pokedb import push_channel, reset_channel

class Systems(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Systems is online.')

    @app_commands.command(name='announcement_channel', description='Change the bot\'s announcment channel')
    async def new_channel(self, interaction: discord.Interaction, channel: str=None):
        guild_id = interaction.guild.id

        if channel is None:
            await interaction.response.send_message('Announcement channel was set to default.')
            reset_channel(guild_id)

        bot_channel = discord.utils.get(interaction.guild.channels, name=channel)

        if bot_channel:
            await interaction.response.send_message(f'{bot_channel} was sucessfully set as the announcement channel!')
            push_channel(guild_id, channel)
        else:
            await interaction.response.send_message('No channel with that name was found!')

async def setup(bot):
    await bot.add_cog(Systems(bot))