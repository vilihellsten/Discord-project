import random
import discord
from discord.ext import commands
from dotenv import load_dotenv 
import logging
import os
import asyncio
from bot_text_file import help_text, responses, steamupdates_instructions
from google import genai

load_dotenv()

token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
logging.basicConfig(filename='discord.log', encoding='utf-8', level=logging.DEBUG)
client = genai.Client()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user.name}')

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
@bot.command()
async def ask(ctx, *, question):
    response = client.models.generate_content(
    model="gemini-2.5-flash-lite", contents=question, #max_output_tokens=100 and version needs some thought 
    )
    await ctx.send(response.text)
    
# When a new member joins the server
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name='general')
    if channel:
        await channel.send(f'Welcome to the server, {member.mention}!')

# Message control
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if 'hello' in message.content.lower():
        await message.channel.send(f'Hello, {message.author.mention}!')

    # Keeps steam-updates message channel clear after user input
    if message.channel.name == "steam-updates": 
        await message.delete(delay=30) 

    await bot.process_commands(message)


@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello, {ctx.author.mention}!')

# Steamupdates help commands gets posted
@bot.command()
async def steamupdates(ctx):
    print("steamupdates command")
    embed = discord.Embed(title="Steam Update Instructions", description=steamupdates_instructions, color=0x00ff00)
    await ctx.send(embed=embed)

# Simple way to make polls in server
@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="Poll", description=question, color=0x00ff00)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction('👍')
    await poll_message.add_reaction('👎')

# General help commands for the bot
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Available commands:", description=help_text, color=0x00ff00)
    await ctx.send(embed=embed)

# 8ball 
@bot.command(name='8ball')
async def ball(ctx, *, question):
    answer = random.choice(responses)
    await ctx.send(f'Question: {question}\nAnswer: {answer}')

# Loads extensions
asyncio.run(bot.load_extension("music"))
asyncio.run(bot.load_extension("steam-updates"))

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
