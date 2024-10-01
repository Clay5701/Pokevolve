import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio
from util.encounter import Pokemon
from util.pokedb import add_pokemon, poke_fetch, release_pokemon, trainerxp_add, get_channel, fetch_trainer, create_trainer
from util.pokeapi import get_type

class PokemonCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Pokemon is online.')
    
    @app_commands.command(name='encounter', description='Encounter a wild pokemon!')
    async def encounter(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        user_id = interaction.user.id
        pokemon_data = Pokemon()
        trainer_data = fetch_trainer(guild_id, user_id)

        if trainer_data is None:
            create_trainer(guild_id, user_id)
            trainer_data = fetch_trainer(guild_id, user_id)

        region = trainer_data[6]
        trainer_level = trainer_data[3]
        pokemon_data.pokemon_sel(region, trainer_level)
        pokemon = pokemon_data.pokemon
        pokemon_level = pokemon_data.level

        await interaction.response.send_message(f'A wild {pokemon.capitalize()} (lvl {pokemon_level}) appeared! \nWould you like to catch it? (yes or no)', ephemeral=True)

        def check(message):
            return message.author == interaction.user and message.channel == interaction.channel

        try:
            msg = await self.bot.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await interaction.followup.send('You took too long to respond. The pokemon got away!', ephemeral=True)
        
        if msg.content.lower() == 'yes':
            success = random.randint(1, 6)
            if success <= 5:
                success = add_pokemon(guild_id, user_id, region, pokemon, pokemon_level)
                if success == 0:
                    await interaction.followup.send(f'You currently have too many pokemon from this region!', ephemeral=True)
                else:
                    await interaction.followup.send(f'Congratulations! {pokemon.capitalize()} has been added to storage.', ephemeral=True)
                    level_up = trainerxp_add(guild_id, user_id, amount=8)
                    if level_up == 1:
                        channel_name = get_channel(guild_id)
                        channel = discord.utils.get(interaction.guild.channels, name=channel_name)
                        
                        if not channel:
                            channel = interaction.channel

                        await channel.send(f'{interaction.user.mention} has leveled up to level **{trainer_data[3]}**!')
            else:
                await interaction.followup.send('Oh no! The pokemon fled.', ephemeral=True)
        if msg.content.lower() == 'no':
            await interaction.followup.send('You got away safely', ephemeral=True)

    @app_commands.command(name='pokemon_list', description='List out your pokemon.')
    async def pokelist(self, interaction: discord.Interaction, user: str=None, region: str=None, level: int=None, pokemon: str=None):
        guild_id = interaction.guild.id
        if region:
            region = region.lower()
        
        if pokemon:
            pokemon = pokemon.lower()

        if user is None:
            user_id = interaction.user.id

        else:
            member = discord.utils.get(interaction.guild.members, name=user)
            if member is None:
                member = discord.utils.find(lambda memb: str(memb) == user, interaction.guild.members)

            if member is None:
                await interaction.response.send_message(f'User {user} not found!', ephemeral=True)
                return
            
            user_id = member.id

        pokemon_list = poke_fetch(guild_id, user_id, region, level, pokemon)
        
        if pokemon_list == []:
            await interaction.response.send_message('No pokemon found!', ephemeral=True)
            return
        else:
            await interaction.response.send_message(f'{len(pokemon_list)} pokemon found!', ephemeral=True)

        message = ''
        for item in pokemon_list:
            message += f'**{item[3].capitalize()}** - [Region: {item[2].capitalize()}   ID: {item[7]}]\n'

        await interaction.followup.send(f'{message}\n***For more information on a given pokemon use /pokemon_info***',  ephemeral=True)

    @app_commands.command(name='pokemon_release', description='Release a pokemon back into the wild!')
    async def poke_del(self, interaction: discord.Interaction, pokemon_id: int):
        guild_id = interaction.guild.id
        user_id = interaction.user.id

        poke_data = poke_fetch(guild_id, user_id, id=pokemon_id)

        if poke_data == []:
            await interaction.response.send_message(f'No pokemon found with this id.', ephemeral=True)
        else:
            await interaction.response.send_message(f'Are you sure you want to release your Level {poke_data[0][6]} {poke_data[0][3].capitalize()}? (yes or no)\n***This action CANNOT be undone***', ephemeral=True)

        def check(message):
            return message.author == interaction.user and message.channel == interaction.channel

        try:
            msg = await self.bot.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await interaction.channel.send('You took too long to respond!')
        
        if msg.content.lower() == 'yes':
            await interaction.followup.send(f'{poke_data[0][3].capitalize()} was released!', ephemeral=True)
            release_pokemon(guild_id, user_id, pokemon_id)
            level_up = trainerxp_add(guild_id, user_id, amount=8)
            if level_up == 1:
                channel_name = get_channel(guild_id)
                channel = discord.utils.get(interaction.guild.channels, name=channel_name)
                        
                if not channel:
                    channel = interaction.channel

                trainer_data = fetch_trainer(guild_id, user_id)
                await channel.send(f'{interaction.user.mention} has leveled up to level **{trainer_data[3]}**!')

        elif msg.content.lower() == 'no':
            await interaction.followup.send(f'{poke_data[0][3].capitalize()} was *not* released!', ephemeral=True)

    @app_commands.command(name='pokemon_info', description='Get more info on a specific pokemon!')
    async def poke_info(self, interaction: discord.Interaction, pokemon_id: int):
        guild_id = interaction.guild.id
        user_id = interaction.user.id

        poke_data = poke_fetch(guild_id, user_id, id=pokemon_id)

        if poke_data == []:
            await interaction.response.send_message('No pokemon found with this id.', ephemeral=True)
            return
        
        poke_types = get_type(poke_data[0][3])

        message = (
            f"**{poke_data[0][3].capitalize()}**   Type(s): **{', '.join(type.capitalize() for type in poke_types)}**\n"
            f"*Region Caught:*   {poke_data[0][2].capitalize()}\n"
            f"*Current XP:*   {poke_data[0][4]}\n"
            f"*XP Needed for Next Level:*   {poke_data[0][5]}\n"
            f"*Current Level:*   {poke_data[0][6]}\n"
            f"*ID:*   {poke_data[0][7]}"
        )
        
        await interaction.response.send_message(message, ephemeral=True)
        
async def setup(bot):
    await bot.add_cog(PokemonCog(bot))