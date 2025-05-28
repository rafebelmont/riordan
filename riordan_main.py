import discord
from discord.ext import commands
from discord import app_commands

from dotenv import load_dotenv
import os

import bot_functions



load_dotenv(".env")
GUILD_ID = os.getenv("GUILD_ID")
GUILD = discord.Object(id=GUILD_ID)
TOKEN: str = os.getenv("TOKEN")

class Client(commands.Bot):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

        try:
            synced = await self.tree.sync(guild=GUILD)
            print(f'Synced {len(synced)} commands.')
        except Exception as e:
            print(f'Error syncing commands: {e}')

    #async def on_message(self, message):
    #    print(f'Message from {message.author}: {message.content}')

intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="!", intents=intents)

@client.tree.command(name="card", description="Busca a carta associada ao nome dado como argumento.", guild=GUILD)
async def getCard(interaction: discord.Interaction, search_name: str, regenerate: bool = False):
    await interaction.response.defer()
    file_name_str = bot_functions.give_card(search_name, regenerate)
    await interaction.followup.send(file=discord.File(file_name_str))

@client.tree.command(name="build_warband", description="Cria um warband. Use ';' como separador", guild=GUILD)
async def buildWarband(interaction: discord.Interaction, *, warband: str):
    await interaction.response.defer()
    args_list = warband.split(";")
    warband_str, total_points, total_hp, warband_jpg = bot_functions.give_warband(*args_list)
    await interaction.followup.send(warband_str+f', Total de pontos: {total_points}, Total de HP: {total_hp}.')
    await interaction.followup.send(file=discord.File(warband_jpg))

@client.tree.command(name="add_alias", description="Adiciona um alias (apelido) a uma criatura.", guild=GUILD)
async def addAlias(interaction: discord.Interaction, alias: str, search_name: str):
    the_card_name = bot_functions.add_alias(alias, search_name)
    await interaction.response.send_message(f'O apelido {alias} foi adicionado a criatura {the_card_name}.')

client.run(TOKEN)