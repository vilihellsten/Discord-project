import random
import discord
from discord.ext import commands
from dotenv import load_dotenv 
import logging
import os
import asyncio
from bot_text_file import help_text, responses


load_dotenv()

token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
logging.basicConfig(filename='discord.log', encoding='utf-8', level=logging.DEBUG)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)
latest_update_id = None

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

    # if "bad word" in message.content.lower(): example
    #     await message.delete()
    await bot.process_commands(message)


@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello, {ctx.author.mention}!')

@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="Poll", description=question, color=0x00ff00)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction('👍')
    await poll_message.add_reaction('👎')

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Available commands:", description=help_text, color=0x00ff00)
    await ctx.send(embed=embed)

@bot.command(name='8ball')
async def ball(ctx, *, question):
    answer = random.choice(responses)
    await ctx.send(f'Question: {question}\nAnswer: {answer}')

asyncio.run(bot.load_extension("music"))
asyncio.run(bot.load_extension("steam-updates"))
bot.run(token, log_handler=handler, log_level=logging.DEBUG)
