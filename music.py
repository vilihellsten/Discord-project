import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
import asyncio

#TODO:

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
        self.song_queue = []

    @commands.command()
    async def join(self, ctx):
        print("join command")
        if ctx.author.voice is not None:
            await ctx.author.voice.channel.connect()
            await ctx.send("Joined the voice channel!")
        else:
            await ctx.send(f"You're not in a voice channel!")

    @commands.command()
    async def play(self, ctx, *, input):
        if ctx.voice_client and ctx.author.voice:
            if ctx.author.voice.channel != ctx.voice_client.channel:
                await ctx.send("Bot is busy in another channel. You need to be in the same voice channel as the bot to play music.")
                return

        if not ctx.voice_client:
            await self.join(ctx)
            await asyncio.sleep(0.2)

        vc = ctx.voice_client

        if vc.is_playing():
            song = await self.search_youtube(ctx, input)
            self.song_queue.append(song)
            await ctx.send(f"Added **{song['title']}** to the queue")
            print("Added to queue:", song['title'])
            return

        song = await self.search_youtube(ctx, input)
        await self.start_playback(ctx, song)

    async def start_playback(self, ctx, song):
        vc = ctx.voice_client
        print("Playing:", song['title'])
        vc.play(discord.FFmpegPCMAudio(song['url'], **FFMPEG_OPTIONS), after=lambda e: self.bot.loop.create_task(self.queue(ctx)))
        window = await ctx.send(f"Now playing: **{song['title']}**")
        await window.add_reaction("⏹️")
        await window.add_reaction("⏭️")

        if window is not None:
            def check(reaction, user):
                return user != self.bot.user and str(reaction.emoji) in ["⏹️", "⏭️"] and reaction.message.id == window.id
            while vc.is_playing():
                reaction, user = await self.bot.wait_for('reaction_add', check=check)
                print(f"Reaction: {reaction}, User: {user}")
                if str(reaction.emoji) == "⏹️":
                    await self.stop(ctx)
                    break
                    #await window.clear_reactions()NEED MANAGE MESSAGES PERMISSION
                    #await window.remove_reaction(reaction.emoji, user)NEED MANAGE MESSAGES PERMISSION
                elif str(reaction.emoji) == "⏭️":
                    await self.skip(ctx, window)
                    break
                    #await window.clear_reactions()
                    
                    #await window.remove_reaction(reaction.emoji, user)NEED MANAGE MESSAGES PERMISSION
                    
        
        #await window.clear_reaction("⏹️") NEED MANAGE MESSAGES PERMISSION
        #await window.clear_reaction("⏭️") NEED MANAGE MESSAGES PERMISSION
            

    async def skip(self, ctx, window): #window NEED MANAGE MESSAGES PERMISSION
        print("skip function")
        await asyncio.sleep(1)  # <-- This causes a delay before playing the next song
        #await window.clear_reactions() NEED MANAGE MESSAGES PERMISSION
        print(self.song_queue)
        if not self.song_queue:
            await ctx.send("No songs in the queue to skip.") #probably not needed as queue takes care of this
            return
        ctx.voice_client.stop()
        await ctx.send("Skipped to next track.")

    async def queue(self, ctx):
        print("queue function")
        print(self.song_queue)
        if len(self.song_queue) > 0:
            next_song = self.song_queue.pop(0)
            print("Playing next song from queue:", next_song['title'])
            await self.start_playback(ctx, next_song)
        else:
            await ctx.send("Reached end of queue.")

    async def search_youtube(self,ctx,input):
        try:
            info = ytdl.extract_info(input if input.startswith("http") 
            else f"ytsearch:{input}", download=False)

            if 'entries' in info:  # jos ytsearch
                info = info['entries'][0]
            song = {
                'title': info.get('title', 'Unknown'),
                'url': info['url'],
                'webpage_url': info.get('webpage_url')
            }
            print("Found song:", song['title'])
            return song
        except Exception as e:
            print("Error in search_youtube:", e)
        
    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            #await ctx.send("Disconnected.")
        else:
            await ctx.send("I'm not in a voice channel.")

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            self.song_queue.clear()
            #await ctx.send("Stopped playback and cleared song queue.")
        else:
            await ctx.send("Nothing is playing.")

async def setup(bot):
    await bot.add_cog(Music(bot))