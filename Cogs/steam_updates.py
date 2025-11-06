import discord
from discord.ext import commands, tasks
import json
import aiohttp
from google import genai
from google.genai import types


gemini_instructions = "Format this text so it can be posted in discord, you can not edit the text at all, only the formating,just give one text because after you are done it will be immeaditelly posted in discord, Keep URL clickable,no HTML-code, NO EMOJIS"
client = genai.Client()


class Steam_updates(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tracked_games = {}


    # Fetch latest update for Steamapp by appid
    async def fetch_game_update(self, appid:int):

        update_url = f"https://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/?appid={appid}&count=10&maxlength=0&format=json"
        picture_url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
        header_image = None

        
        async with aiohttp.ClientSession() as session:

            # Fetch latest header image of the game
            async with session.get(picture_url) as resp:
                if resp.status == 200:
                    picture_json = await resp.json()
                    app_data = picture_json.get(str(appid), {}).get("data", {})
                    header_image = app_data.get("header_image")

            # Fetch laste news updates from Steam News API
            async with session.get(update_url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    newsitems = data.get("appnews", {}).get("newsitems", [])

                    # Loop through news and find the newest one with official community announcements
                    # Returns information needed about the update
                    for news in newsitems:
                        print("news:", news)
                        if news.get("feedname") == "steam_community_announcements":
                            return {
                                "title": news.get("title"),
                                "url": news.get("url"),
                                "contents": news.get("contents"),
                                "gid": news.get("gid"),
                                "date": news.get("date"),
                                "picture": header_image
                            }
        return None


    #TODO Currently the game name is from a local steamapps.json file, 
    # We already have the appid, could just use Steam API to find
    # the app name instead of going through the local file

    # Adds a game to tracked_games_list
    @commands.command()  
    async def add(self, ctx, appid): 

        # Makes sure appid is a number
        try:
            appid = int(appid)
        except ValueError:
            await ctx.send("ID must be a number.")
            return
        
        # Loads local steamapps.json list containing appid and name, "{"appid": 440, "name": "Team Fortress 2"}"
        try:
            with open('data/steamapps.json', 'r', encoding='utf-8') as f: 
                data = json.load(f) 
            apps = data["applist"]["apps"]  
        except FileNotFoundError:
            print("Error: 'steamapps.json' file not found.")
            return None
        print("searching " + str(appid))

        # Look for a game that matches users input appid in the steamapps.json list
        appname = None 
        for app in apps:
            if app["appid"] == appid:
                appname = app["name"]
                print("Found name:", appname)
                break

        # Appid not found
        if appname is None:
            await ctx.send(f"App with ID '{appid}' not found.")
            return
        
        # If Appid is already tracked
        if appname in self.tracked_games:
            await ctx.send(f"Already tracking updates for ID: {appid} , {appname}.", delete_after=15)
            return
        
        # Fetch game update with appid
        news = await self.fetch_game_update(appid)
        print(news['contents'])

        # Formats the applications update information
        response = client.models.generate_content(
        model="gemini-2.5-flash-lite",config = types.GenerateContentConfig(system_instruction=gemini_instructions), contents=news['contents'] #max_output_tokens=100 säätöä
        )

        embed = discord.Embed(title=news["title"], url=news["url"], description=response.text[:800] + ("..." if len(response.text) > 800 else ""), color=0x00ff00)
        embed.set_image(url=news["picture"])
        await ctx.send(embed=embed)
        
        # Update tracked_games list
        self.tracked_games[appname] = {"appid": appid, "latest_update_id": news["gid"]}
        print(self.tracked_games)

        # Save changes to the Json file
        with open('data/tracked_games.json', 'w') as f:
            json.dump(self.tracked_games, f,)
            print("Tracked games saved to 'tracked_games.json'.")

        await ctx.send(f"Now tracking updates for '{appname}'.")
    
    
    # Might be needed
    async def channel_check(self):
        channel = discord.utils.get(self.bot.get_all_channels(), name='steam-updates')
        if channel is None:
            print("Channel 'steam-updates' not found.")
            return None
        return channel
    
    # Get a list from all tracked games
    @commands.command()
    async def list(self, ctx):

        if not self.tracked_games:
            await ctx.send("No applications are currently being tracked.")
            return
        i = 1
        message = ""

        # Gives a number : name for each game in tracked_games
        for appname in self.tracked_games.keys(): 
            message += f"{i} : {appname}\n" 
            i = i + 1

        embed = discord.Embed(title="Currently tracked applications:", description=message, color=0x00ff00)
        await ctx.send(embed=embed)

    # Remove a tracked game from a list using number
    @commands.command()
    async def remove(self, ctx, list_number:int):

        if not self.tracked_games:
            await ctx.send("No games are currently being tracked.")
            return
        
        if list_number < 1 or list_number > len(self.tracked_games):
            await ctx.send("Invalid list number.")
            return
        
        # Update tracked_games list
        appname = list(self.tracked_games.keys())[list_number - 1]
        del self.tracked_games[appname]

        # Save changes to the Json file
        with open('data/tracked_games.json', 'w') as f:
            json.dump(self.tracked_games, f,)
            print(f"Removed {appname} from 'tracked_games.json'.")
        await ctx.send(f"Stopped tracking updates for '{appname}'.")
    
    # Check all games in tracked_games for new Steam updates every 60 minutes
    @tasks.loop(minutes=60)
    async def check_for_updates(self):
        print("Checking for updates...")

        # Looks for a channel named 'steam-updates'
        channel = discord.utils.get(self.bot.get_all_channels(), name='steam-updates')
        if channel is None:
            print("Channel 'steam-updates' not found.")
            return
        
        # Go through every tracked game to check if there is new updates
        updated = False
        for appname, data in self.tracked_games.items():
            appid = data["appid"]
            news = await self.fetch_game_update(appid)

            # If a new update (gid) does not match with latest_update_id, post new update in Discord and replace id in tracked_games
            if news and news["gid"] != data["latest_update_id"]:
                self.tracked_games[appname]["latest_update_id"] = news["gid"]
                embed = discord.Embed(title=news["title"], url=news["url"], description=news["contents"], color=0x00ff00)
                embed.set_image(url=news["picture"])
                await channel.send(embed=embed)
                updated = True

        # If new updates are found, update the latest_update_id and save the changes
        if updated:
            with open('data/tracked_games.json', 'w') as f:
                json.dump(self.tracked_games, f,)
                print(f"{appname}, updated latest_update_id variable to 'tracked_games.json'.")
                


    # Load all tracked games from a JSON file on startup
    async def load_tracked_games(self):
        try:
            with open('data/tracked_games.json', 'r') as f:
                self.tracked_games = json.load(f)
                print("Tracked games loaded from 'tracked_games.json'.")
        except FileNotFoundError:
            print("No tracked games found, starting with an empty list.")
    

    # Command to check for updates of a specific app by name
    @commands.command()
    async def check(self, ctx, appname:str):
        await self.search_game_id(ctx, appname)


    # Loads on startup
    @commands.Cog.listener()
    async def on_ready(self):
        await self.load_tracked_games()
        await self.check_for_updates.start() 
       

async def setup(bot):
    await bot.add_cog(Steam_updates(bot))
