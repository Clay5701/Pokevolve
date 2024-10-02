import discord
from discord import app_commands
from discord.ext import commands
import random
from util.pokedb import fetch_companion, create_trainer, push_update, get_channel, trainerxp_add, fetch_trainer
from util.pokeapi import fetch_evolution

class Level(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Leveling is online.')

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        guild_id = message.guild.id
        user_id = message.author.id
        
        poke_data = fetch_companion(guild_id, user_id)

        if poke_data is None:
            create_trainer(guild_id, user_id)

        poke_id = poke_data[0][7]

        if poke_id == 0:
            return
        
        poke_xp = poke_data[0][4]
        level_up_xp = poke_data[0][5]
        poke_level = poke_data[0][6]
        poke_name = poke_data[0][3]

        new_poke_xp = poke_xp + random.randint(0, 4)

        if new_poke_xp >= level_up_xp:
            new_poke_xp -= level_up_xp
            poke_level += 1
            new_level_up_xp = (2 * poke_level ** 2 + 7 * poke_level + 15) - (2 * (poke_level-1) ** 2 + 7 * (poke_level-1) + 15)

            evolution = fetch_evolution(poke_name, poke_level)

            channel_name = get_channel(guild_id)
            channel = discord.utils.get(message.guild.channels, name=channel_name)

            if not channel:
                channel = message.channel

            if evolution:
                await channel.send(f'{message.author.mention} Your companion {poke_name.capitalize()} has reached level {poke_level} and evolved into **{evolution.capitalize()}**!')
                push_update(guild_id, user_id, poke_id, pokemon=evolution, xp=new_poke_xp, level_up_xp=new_level_up_xp, level=poke_level)
                level_up = trainerxp_add(guild_id, user_id, amount=45)
            else:
                await channel.send(f'{message.author.mention} Your companion {poke_name.capitalize()} has reached level {poke_level}!')
                push_update(guild_id, user_id, poke_id, xp=new_poke_xp, level_up_xp=new_level_up_xp, level=poke_level)
                level_up = trainerxp_add(guild_id, user_id, amount=15)
            
            if level_up == 1:
                trainer_data = fetch_trainer(guild_id, user_id)
                await channel.send(f'{message.author.mention} has leveled up to level **{trainer_data[3]}**!')

        push_update(guild_id, user_id, poke_id, xp=new_poke_xp)

async def setup(bot):
    await bot.add_cog(Level(bot))