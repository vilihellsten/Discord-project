import random
import discord
from discord.ext import commands
from dotenv import load_dotenv 
import logging
import os
import asyncio


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
    help_text = """ 
    !hello - Greet the bot
    !poll <question> - Create a poll with the given question
    !help - Show this help message
    !join - Bot joins your voice channel
    !play <url or search term> - Play audio from a youtube URL or search term
    !stop - Stop the current audio
    !leave - Bot leaves the voice channel
    """
    embed = discord.Embed(title="Available commands:", description=help_text, color=0x00ff00)
    await ctx.send(embed=embed)

@bot.command(name='8ball')
async def ball(ctx, *, question):
    print("ball")
    responses = [
        "It is certain.",
        "It is decidedly so.",
        "Without a doubt.",
        "Yes - definitely.",
        "You may rely on it.",
        "As I see it, yes.",
        "Most likely.",
        "Outlook good.",
        "Yes.",
        "Signs point to yes.",
        "Better not tell you now.",
        "Don't count on it.",
        "My reply is no.",
        "My sources say no.",
        "Outlook not so good.",
        "Very doubtful."
    ]
    answer = random.choice(responses)
    print(answer)
    
    await ctx.send(f'Question: {question}\nAnswer: {answer}')

asyncio.run(bot.load_extension("music"))
asyncio.run(bot.load_extension("steam-updates"))
bot.run(token, log_handler=handler, log_level=logging.DEBUG)
