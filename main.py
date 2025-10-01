import discord
from discord.ext import commands
from dotenv import load_dotenv 
import logging
import os




load_dotenv()

token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)


async def on_ready():
    assert bot.user is not None
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user.name}')

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name='general')
    if channel:
        await channel.send(f'Welcome to the server, {member.mention}!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if 'hello' in message.content.lower():
        await message.channel.send(f'Hello, {message.author.mention}!')

    # if "kirosana" in message.content.lower():
    #     await message.delete()

    await bot.process_commands(message)

@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello, {ctx.author.mention}!')


bot.run(token, log_handler=handler, log_level=logging.DEBUG)