import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
import asyncio

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

    # Bot joins users voice channel
    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice is not None:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send(f"You're not in a voice channel!")

    # Bot plays a song or adds it to song_queue
    @commands.command()
    async def play(self, ctx, *, input):

        # Bot cant join the user if it is playing music in a another voice channel
        if ctx.voice_client and ctx.author.voice:
            if ctx.author.voice.channel != ctx.voice_client.channel:
                await ctx.send("Bot is busy in another channel. You need to be in the same voice channel as the bot to play music.")
                return

        # If the bot is not connected, join the voice channel
        if not ctx.voice_client:
            await self.join(ctx)
            await asyncio.sleep(0.2)

        vc = ctx.voice_client

        # If bot is already playing, add the song to the queue
        if vc.is_playing():
            song = await self.search_youtube(ctx, input)
            self.song_queue.append(song)
            await ctx.send(f"Added **{song['title']}** to the queue")
            print("Added to queue:", song['title'])
            return

        # Search the song and start playback
        song = await self.search_youtube(ctx, input)
        await self.start_playback(ctx, song)

    # Plays the songs
    async def start_playback(self, ctx, song):
        vc = ctx.voice_client
   
        # After song ends
        def after_playback(error):
            async def inner():
                await self.remove_buttons(vc) # Removes buttons from player
                await self.queue(ctx)         # Checks the queue for a new song
            self.bot.loop.create_task(inner())

        print("Playing:", song['title'])
        vc.play(discord.FFmpegOpusAudio(song['url'], **FFMPEG_OPTIONS), after=after_playback)
        
        # Embeds the player, all the info needed
        embed = discord.Embed(
            title="🎵 Now Playing",
            description=f"[{song['title']}]({song['webpage_url']})",
            color=discord.Color.blurple()
            )
        if 'thumbnail' in song and song['thumbnail']:
            embed.set_image(url=song['thumbnail'])

        # View holds buttons
        view = MusicControls(ctx, self)
        # View attached to message that is sent to Discord channel
        message = await ctx.send(embed=embed, view=view)
        # Update the current message, helps with deleteing buttons from "player"
        vc.current_message = message

    # Song queue
    async def queue(self, ctx):
        print("queue function")

        # If there are songs in queue, play next song and delete it from queue
        if len(self.song_queue) > 0:
            next_song = self.song_queue.pop(0)
            print("Playing next song from queue:", next_song['title'])
            await self.start_playback(ctx, next_song)
        else:
            return
        
    # Skips the current song
    async def skip(self, ctx): 
        print("skip function")
        await asyncio.sleep(1)

        # If queue is empty, stop playing and remove buttons
        if not self.song_queue:
            await self.remove_buttons(ctx.voice_client)
            await self.stop(ctx)
        
        # If queue is not empty, stopping trigger after_playback
        ctx.voice_client.stop()

    # Searches youtube for media, users can give URL or search term
    async def search_youtube(self,ctx,input):
        try:
            # Checks if input is http or search term
            info = await asyncio.to_thread(ytdl.extract_info,
                input if input.startswith("http") else f"ytsearch:{input}",download=False)
            
            # Search term produces a list, chooses first one
            if 'entries' in info:  
                info = info['entries'][0]
            
            # All that is needed from info
            song = {
                'title': info.get('title', 'Unknown'),
                'url': info['url'],
                'webpage_url': info.get('webpage_url'),
                'thumbnail': info.get('thumbnail')
            }
            print("Found song:", song['title'])
            print("Webpage URL:", song['webpage_url'])
            return song
        except Exception as e:
            print("Error in search_youtube:", e)
    
    # Disconnect users channel
    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        else:
            await ctx.send("I'm not in a voice channel.")

    # Stops playback, clears song_queue and removes buttons, remove command portion?
    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            await self.remove_buttons(ctx.voice_client)
            ctx.voice_client.stop()
            self.song_queue.clear()
        else:
            await ctx.send("Nothing is playing.")

    # Removes buttons from message or "player"
    async def remove_buttons(self, vc):
        if vc and vc.current_message:
            try:
                await vc.current_message.edit(view=None)
            except Exception as e:
                print("Error removing buttons:", e)
            vc.current_message = None

async def setup(bot):
    await bot.add_cog(Music(bot))


# Buttons for message or "player"
class MusicControls(discord.ui.View):
    def __init__(self, ctx, music_cog):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.music_cog = music_cog  

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger)
    async def stop_button(self, interaction: discord.Interaction, _):
        # Permission check for buttons
        if self.users_in_voice_channel(interaction.user):
            await interaction.response.defer()
            await self.music_cog.stop(self.ctx)
        else:
            await interaction.response.send_message(
                "You must be in the same voice channel as the bot to use this.", ephemeral=True
            )

    @discord.ui.button(label="Skip", style=discord.ButtonStyle.primary)
    async def skip_button(self, interaction: discord.Interaction, _):
        # Permission check for buttons
        if self.users_in_voice_channel(interaction.user):
            await interaction.response.defer()
            await self.music_cog.skip(self.ctx)
        else:
            await interaction.response.send_message(
                "You must be in the same voice channel as the bot to use this.", ephemeral=True
            )
        
    # Determines who can use the buttons
    def users_in_voice_channel(self, user):
        vc = self.ctx.voice_client

        # Check if the bot has a voice client
        if vc is None:
            return False 

        # Check if the bot is actually in a channel
        if vc.channel is None:
            return False  

        # Check if the user is connected to a voice channel
        if user.voice is None:
            return False 
        
        # Check if the user's voice channel matches the bot's channel
        if user.voice.channel != vc.channel:
            return False  
        return True
