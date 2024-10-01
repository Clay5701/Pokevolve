import discord
from discord import app_commands
from discord.ext import commands
from util.pokedb import poke_fetch, set_companion, fetch_companion
from util.pokeapi import get_type

class Companion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Companion is online.')

    @app_commands.command(name='set_companion', description='Set your companion pokemon!')
    async def set_bud(self, interaction: discord.Interaction, pokemon_id: int):
        guild_id = interaction.guild.id
        user_id = interaction.user.id

        poke_data = poke_fetch(guild_id, user_id, id=pokemon_id)
        og_comp_data = fetch_companion(guild_id, user_id)

        if poke_data == []:
            await interaction.response.send_message('No pokemon found with this id.', ephemeral=True)
            return
        
        if og_comp_data != []:
            if pokemon_id == og_comp_data[0][7]:
                await interaction.response.send_message(f'{poke_data[0][3].capitalize()} is already your companion!', ephemeral=True)

        set_companion(guild_id, user_id, pokemon_id)

        comp_data = fetch_companion(guild_id, user_id)

        if comp_data != poke_data:
            await interaction.response.send_message('Something went wrong setting your companion. Check your pokemon id!', ephemeral=True)
        
        await interaction.response.send_message(f'{poke_data[0][3].capitalize()} is now your companion!', ephemeral=True)

    @app_commands.command(name='companion_info', description='Get info on your or someone else\'s companion pokemon!.')
    async def comp_info(self, interaction: discord.Interaction, user: str = None):
        guild_id = interaction.guild.id

        if user is None:
            user_id = interaction.user.id
            response = 'Your'

        else:
            member = discord.utils.get(interaction.guild.members, name=user)
            if member is None:
                member = discord.utils.find(lambda memb: str(memb) == user, interaction.guild.members)

            if member is None:
                await interaction.response.send_message(f'User {user} not found!', ephemeral=True)
                return
            
            user_id = member.id
            response = f"{user}'s"

        poke_data = fetch_companion(guild_id, user_id)
        
        if poke_data == [] or poke_data is None:
            await interaction.response.send_message(f'No companion info found!', ephemeral=True)
            return

        poke_types = get_type(poke_data[0][3]) 

        message = (
            f"{response} companion info:\n"
            f"**{poke_data[0][3].capitalize()}**   Type(s): **{', '.join(type.capitalize() for type in poke_types)}**\n"
            f"*Region Caught:*   {poke_data[0][2].capitalize()}\n"
            f"*Current XP:*   {poke_data[0][4]}\n"
            f"*XP Needed for Next Level:*   {poke_data[0][5]}\n"
            f"*Current Level:*   {poke_data[0][6]}\n"
            f"*ID:*   {poke_data[0][7]}"
        )
        
        await interaction.response.send_message(message, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Companion(bot))