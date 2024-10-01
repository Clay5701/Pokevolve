import discord
from discord import app_commands
from discord.ext import commands
from util.pokedb import fetch_companion, fetch_trainer, push_region

class Trainer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Trainer is online.')

    @app_commands.command(name='trainer_info', description='Get your trainer info or someone else\'s info!')
    async def trainer_info(self, interaction: discord.Interaction, user: str = None):
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

        trainer_data = fetch_trainer(guild_id, user_id)
        poke_data = fetch_companion(guild_id, user_id)

        if trainer_data is None:
            await interaction.response.send_message(f'No trainer info found!', ephemeral=True)
            return
        
        if poke_data == [] or poke_data is None:
            comp_message = 'No companion'
        else:
            comp_message = f'Current Companion: **{poke_data[0][3].capitalize()}** (lvl {poke_data[0][6]})'

        region_data = region_list(trainer_data[3])
        
        message = (
            f"{response} trainer info:\n"
            f"{comp_message}\n"
            f"*Current XP:*   {trainer_data[4]}\n"
            f"*XP Needed for Next Level:*   {trainer_data[5]}\n"
            f"*Current Level:*   {trainer_data[3]}\n"
            f"*Unlocked Regions:*   {', '.join(region.capitalize() for region in region_data)}"
        )

        await interaction.response.send_message(message, ephemeral=True)
    
    @app_commands.command(name='travel', description='Go to a different region!')
    async def travel(self, interaction: discord.Interaction, region: str):
        region = region.lower()
        all_regions = ['kantos','johto','hoenn','sinnoh','unova']
        guild_id = interaction.guild.id
        user_id = interaction.user.id
        trainer_data = fetch_trainer(guild_id, user_id)

        region_data = region_list(trainer_data[3])

        if region not in all_regions:
            await interaction.response.send_message('Invalid region!', ephemeral=True)
            return

        if region not in region_data:
            await interaction.response.send_message('You haven\'t unlocked this region yet!', ephemeral=True)
            return
        
        if region == trainer_data[6]:
            await interaction.response.send_message('You are currently in this region!', ephemeral=True)
        
        push_region(guild_id, user_id, region)
        await interaction.response.send_message(f'You traveled to {region.capitalize()}!', ephemeral=True)

def region_list(level):
    region_data = []
    if level > 9:
        region_data.insert(0, 'unova')
        region_data.insert(0, 'sinnoh')
    if level > 4:
        region_data.insert(0, 'hoenn')
        region_data.insert(0, 'johto')

    region_data.insert(0, 'kantos')

    return region_data

async def setup(bot):
    await bot.add_cog(Trainer(bot))