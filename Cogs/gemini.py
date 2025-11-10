from google import genai
from discord.ext import commands


client = genai.Client()

#Todo: Move the ask command here from main.py and steamupdates
class Gemini(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tracked_games = {}

    @commands.command()
    async def ask(ctx, *, question):
        response = client.models.generate_content(
        model="gemini-2.5-flash-lite", contents=question, #max_output_tokens=150
        )
        await ctx.send(response.text)

async def setup(bot):
    await bot.add_cog(Gemini(bot))