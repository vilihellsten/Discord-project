import discord
from discord.ext import commands
import requests
import json

class Steam_updates(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        #self.latest_update_id = None # Ei käytössä vielä testivaiheessa

    async def fetch_cs2_updates(self):
        url = f"https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=730&count=1&maxlength=3000&format=json"
        response = requests.get(url)
        if response.status_code == 200:
            news = response.json()["appnews"]["newsitems"][0]
            formated_content = news["contents"].replace('.', '.\n - ').replace('\\', '')

            if formated_content.endswith('\n - '):
                formated_content = formated_content[:-3].strip()
            if not formated_content.startswith('-'):
                formated_content = '- ' + formated_content
            return{
                "title": news["title"],
                "url": news["url"],
                "contents": formated_content,
                "gid": news["gid"],
                "date": news["date"]
            }
        return None
    
    
    async def check_for_updates(self):
        cs_id = 730
        news = await self.fetch_cs2_updates()
        #if news and news["gid"] != self.latest_update_id:
        channel = discord.utils.get(self.bot.get_all_channels(), name='steam-updates')
        self.latest_update_id = news["gid"]
        if channel:
            picture = "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/730/header.jpg?t=1749053861"
            embed = discord.Embed(title=news["title"], url=news["url"], description=news["contents"], color=0x00ff00)
            embed.set_thumbnail(url=picture)
            await channel.send("New CS2 Update!", embed=embed)
    

    async def searchs_id(self,ctx, appname:str):
        print("checking")
        try:
            with open('Apps.json', 'r', encoding='utf-8') as f:
                data = json.load(f)  # data is a dict now

            apps = data["applist"]["apps"]  # this is the list of apps

        except FileNotFoundError:
            print("Error: 'Apps.json' file not found.")
            return None
        except json.JSONDecodeError:
            print("Error: 'Apps.json' is not valid JSON.")
            return None
        except KeyError:
            print("Error: JSON structure is not as expected.")
            return None

        print(appname)

        appid = None
        for app in apps:
            if app["name"] == appname:
                appid = app["appid"]
                print("Found appid:", appid)
                news = await self.fetch_any_update(appid)
                embed = discord.Embed(title=news["title"], url=news["url"], description=news["contents"], color=0x00ff00)
                await ctx.send(embed=embed)
                
  
        return appid

    async def fetch_any_update(self, appid:int):
        url = f"https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid={appid}&count=1&maxlength=3000&format=json"
        response = requests.get(url)
        if response.status_code == 200:
            news = response.json()["appnews"]["newsitems"][0]
            formated_content = news["contents"].replace('.', '.\n - ').replace('\\', '')

            if formated_content.endswith('\n - '):
                formated_content = formated_content[:-3].strip()
            if not formated_content.startswith('-'):
                formated_content = '- ' + formated_content
            return{
                "title": news["title"],
                "url": news["url"],
                "contents": formated_content,
                "gid": news["gid"],
                "date": news["date"]
            }
        return None



    @commands.command()
    async def check(self, ctx, appname:str):
        print("command")
        await self.searchs_id(ctx, appname)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.check_for_updates()

async def setup(bot):
    await bot.add_cog(Steam_updates(bot))
