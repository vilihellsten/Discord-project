import discord
from discord.ext import commands, tasks
import requests
import json
import re
#from google import genai
#from google.genai import types

#gemini-2.5-flash-lite parempi mutta enemmän tokeneita vievä

""" voisi käyttää AI:tä formatoimaan päivitykset nätimmin koska hieman arvaamatonta tuo steamin api välillä
response = client.models.generate_content(
model="gemini-2.0-flash-lite",config = types.GenerateContentConfig(system_instruction="Format this text so it can be posted in discord,just give one text because after you are done it will be immeaditelly posted in discord, Keep URL clickable, NO EMOJIS"), contents=raw_text, #max_output_tokens=100 säätöä
)

print(response.text)
"""
#client = genai.Client()

json_data =  {
    "appid": 730,
    "newsitems": [
    {
        "gid": "1811772772523858",
        "title": "Counter-Strike 2 Update",
        "url": "https://steamstore-a.akamaihd.net/news/externalpost/steam_community_announcements/1811772772523858",
        "author": "Vitaliy",
        "contents": "[p]Let's get right into it. Today's update features new Wingman and Competitive community maps, along with brand new charms (including community designs), stickers, and more.[/p][p][/p][h3]Community Maps[/h3][p][video webm=\"{STEAM_CLAN_IMAGE}/3381077/1328ecdd3aff19f14078872e0b8eea7e24e615f8.webm\" mp4=\"{STEAM_CLAN_IMAGE}/3381077/c5ab133e75f3b6b2c822652b91d16dfffad9bdd1.mp4\" poster=\"https://clan.akamai.steamstatic.com/images/3381077/61b420dee3aff1796ba385d7405396b5047deb15.png\" autoplay=\"true\" controls=\"false\"][/video]From the mines of Golden to the moving train in Transit, we've got four new Community maps for you to check out. Golden and Palacio have been added to Competitive, Casual, and Deathmatch modes, and Rooftop and Transit have been added to Wingman.[/p][p][/p][h3]New Armory Content[/h3][p][video webm=\"{STEAM_CLAN_IMAGE}/3381077/76714b20b536928194ade6f5237890cf2a25239d.webm\" mp4=\"{STEAM_CLAN_IMAGE}/3381077/0316226665da792bf99752da24c6869c5bb26496.mp4\" poster=\"https://clan.akamai.steamstatic.com/images/3381077/1b2f71d055a5b73ec263d88ebf1cd5c7108aa1da.png\" autoplay=\"true\" controls=\"false\"][/video]It's a lil' HE grenade... for your gun. It doesn't explode, but it sure is [i]charming[/i]. Introducing the all new Dr. Boom Charms, now available in the Armory.[/p][p][/p][p][video webm=\"{STEAM_CLAN_IMAGE}/3381077/9b6ecf851f93202f7c7e3a1a6c1e80fd29e71239.webm\" mp4=\"{STEAM_CLAN_IMAGE}/3381077/c2e64c689b7e6aa8ea134de7c06b6e0cea790a4d.mp4\" poster=\"https://clan.akamai.steamstatic.com/images/3381077/7490b11599e34e5b309e1680892689cde14a69eb.png\" autoplay=\"true\" controls=\"false\"][/video]A few months ago we added charms to the workshop, and you responded. For some insight into the creative and occasionally twisted minds of the CS2 community, check out the Missing Link Community Charms in the Armory.[/p][p][/p][p][img]{STEAM_CLAN_IMAGE}/3381077/9a588a3121139f437497d4a279e279f29f10998f.png[/img][/p][p]Speaking of community designs, the Armory now features two brand new sticker collections, including the return of Sugarface![/p]",
        "feedlabel": "Community Announcements",
        "date": 1759533512,
        "feedname": "steam_community_announcements",
        "feed_type": 1,
        "appid": 730,
        "tags": [
        "patchnotes"
        ]
    }
    ],
    "count": 1675
}



class Steam_updates(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tracked_games = {}
     
    # Check for all tracked game updates every 60 minutes
    @tasks.loop(minutes=60)
    async def check_for_updates(self):
        for appname, data in self.tracked_games.items():
            appid = data["appid"]
            news = await self.fetch_game_update(appid)
            if news and news["gid"] != data["latest_update_id"]:
                channel = discord.utils.get(self.bot.get_all_channels(), name='steam-updates')
                self.tracked_games[appname]["latest_update_id"] = news["gid"]
                if channel is not None: # is not None !!!!!!!!!!!!!!!!!
                    picture = "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/730/header.jpg?t=1749053861"
                    embed = discord.Embed(title=news["title"], url=news["url"], description=news["contents"], color=0x00ff00)
                    embed.set_thumbnail(url=picture)
                    await channel.send(embed=embed)
                    with open('tracked_games.json', 'w') as f:
                        json.dump(self.tracked_games, f,)
                        print(f"{appname}, updated latest_update_id variable to 'tracked_games.json'.")
                else:
                    print("Channel 'steam-updates' not found.")

        # Fetch latest update for any app by appid
    async def fetch_game_update(self, appid:int):
        url = f"https://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/?appid={appid}&count=1&maxlength=100&format=json"
        response = requests.get(url)
        if response.status_code == 200:
            news = response.json()["appnews"]["newsitems"][0]
            return{
                "title": news["title"],
                "url": news["url"],
                "contents": news["contents"],
                "gid": news["gid"],
                "date": news["date"]
            }
        return None

    # Search app id by name from local json file and then fetch latest update
    async def search_game_id(self,ctx, appname:str):
        print("checking")
        try:
            with open('Apps.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            apps = data["applist"]["apps"]
        except FileNotFoundError:
            print("Error: 'Apps.json' file not found.")
            return None
        print("searching " + appname)

        appid = None
        for app in apps:
            if app["name"] == appname:
                appid = app["appid"]
                print("Found appid:", appid)
                
                news = await self.fetch_any_update(appid)
                embed = discord.Embed(title=news["title"], url=news["url"], description=news["contents"], color=0x00ff00)
                await ctx.send(embed=embed)
        else:
            if appid is None:
                await ctx.send(f"App '{appname}' not found.")

    @commands.command()
    async def list(self, ctx):
        print("listing")
        if not self.tracked_games:
            await ctx.send("No games are currently being tracked.")
            return
        i = 1
        message = ""
        for appname, data in self.tracked_games.items():
            message += f"{i:>2} : {appname}\n"
            i += 1
        #message= f"```{message}```"
        embed = discord.Embed(title="Currently tracked Games:", description=message, color=0x00ff00)
        await ctx.send(embed=embed)

    @commands.command()
    async def remove(self, ctx, list_number:int):
        print("removing")
        if not self.tracked_games:
            await ctx.send("No games are currently being tracked.")
            return
        if list_number < 1 or list_number > len(self.tracked_games):
            await ctx.send("Invalid list number.")
            return
        appname = list(self.tracked_games.keys())[list_number - 1]
        del self.tracked_games[appname]
        with open('tracked_games.json', 'w') as f:
            json.dump(self.tracked_games, f,)
            print(f"Removed {appname} from 'tracked_games.json'.")
        await ctx.send(f"Stopped tracking updates for '{appname}'.")

    @commands.command()  #TODO voisi hakea nimelläkin, oikeat checkit tilalle
    async def add(self, ctx, appid): ## voisi etsiä nimellä tai IDllä? ID tarkin

        try:
            appid = int(appid)
        except ValueError:
            await ctx.send("ID must be a number.")
            return
        
        print("adding")
        try:
            with open('Apps.json', 'r', encoding='utf-8') as f: ## voisi ladata netistäkin tai miksi edes tarkistaa
                data = json.load(f) ## voisi luottaa käyttäjään että tietää mitä tekee ja antaa oikean id, jos ei ilmoittaa epäkelvosta id:stä
            apps = data["applist"]["apps"]  
        except FileNotFoundError:
            print("Error: 'Apps.json' file not found.")
            return None
        print("searching " + str(appid))

        appname = None
        for app in apps:
            if app["appid"] == appid:
                appname = app["name"]
                print("Found name:", appname)
                self.tracked_games[appname] = {"appid": appid, "latest_update_id": None}
                print(self.tracked_games)

                with open('tracked_games.json', 'w') as f:
                    json.dump(self.tracked_games, f,)
                    print("Tracked games saved to 'tracked_games.json'.")
                    # pitäisi lisäyksen jälkeen tarkistaa onko päivityksiä ja lähettää viesti kanavalle???

                await ctx.send(f"Now tracking updates for '{appname}'.")
                return
        else:
            if appname is None:
                await ctx.send(f"App '{appname}' not found.")


    # Loads tracked games from a JSON file 
    async def load_tracked_games(self):
        try:
            with open('tracked_games.json', 'r') as f:
                self.tracked_games = json.load(f)
                print(self.tracked_games)
                print("Tracked games loaded from 'tracked_games.json'.")
        except FileNotFoundError:
            print("No tracked games found, starting with an empty list.")
            self.tracked_games = {}

    # Command to check for updates of a specific app by name
    @commands.command()
    async def check(self, ctx, appname:str):
        await self.search_game_id(ctx, appname)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.load_tracked_games()
        await self.check_for_updates.start() 
       

async def setup(bot):
    await bot.add_cog(Steam_updates(bot))
