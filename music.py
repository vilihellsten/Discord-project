import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
import asyncio

#TODO: Song queue, pause, resume, skip, error handling, maybe add reactions for controls

YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': False
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = YoutubeDL(YTDL_OPTIONS)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        print("join command")
        if ctx.author.voice is not None:
            await ctx.author.voice.channel.connect()
            await ctx.send("Joined the voice channel!")
        else:
            await ctx.send("You're not in a voice channel!")

   
    @commands.command()
    async def play(self, ctx, *, input: str):
        vc = ctx.voice_client

        #testaa
        #if not vc: # If the bot is not connected to a voice channel, try to join the author's channel
        #   await ctx.send("I'm not connected to a voice channel.")
        #  return
        
        #if ctx.voice_client and ctx.author.voice:
        #    if ctx.author.voice.channel != ctx.voice_client.channel:
         #       await ctx.send("Bot is busy in a another channel. You need to be in the same voice channel as the bot to play music.")
         #       return
            
        #await self.join(ctx) #kokeilussa
        #await asyncio.sleep(1)  # Varmistaa, että bot on liittynyt kan
        #testaa loppuu
        
        if vc.is_playing():
            vc.stop()
            await asyncio.sleep(0.25)

        if input.startswith("http") or input.startswith("www"):
            await ctx.send(f"Processing URL: {input}")

            try:
                info = ytdl.extract_info(input, download=False)
            except Exception as e:
                await ctx.send(f"Invalid URL or error occurred: {str(e)}")
                await ctx.voice_client.disconnect()
                return
            audio_url = info['url']
            title = info.get('title', 'Unknown')

        else:
            try:
                info = ytdl.extract_info(f"ytsearch:{input}", download=False)['entries'][0]
                webpage_url = info.get('webpage_url')
            except Exception as e:
                await ctx.send(f"Invalid URL or error occurred: {str(e)}")
                await ctx.voice_client.disconnect()
            await ctx.send(f"Processing URL: {webpage_url}")
            audio_url = info['url']
            title = info.get('title', 'Unknown')
            

        vc.play(discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS))
        window = await ctx.send(f"Now playing: **{title}**")
        await window.add_reaction("⏭️")

    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("Disconnected.")
        else:
            await ctx.send("I'm not in a voice channel.")

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Stopped playback.")
        else:
            await ctx.send("Nothing is playing.")

async def setup(bot):
    await bot.add_cog(Music(bot))