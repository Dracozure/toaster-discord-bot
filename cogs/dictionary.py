import sqlite3
from discord.ext import commands
import requests
from dotenv import load_dotenv
import os

class Dictionary(commands.Cog):
    conn = sqlite3.connect("words.db") 
    c = conn.cursor()
    THESAURUS_API = os.getenv("THESAURUS_API")
    DICTIONARY_API = os.getenv("DICTIONARY_API")

    def __init__(self, bot):
        self.bot = bot
        load_dotenv()
        self.c.execute("""CREATE TABLE words (
                word text,
                author_id integer,
                timestamp text
        )""")
        self.conn.commit()
        self.conn.close()
    
    @commands.command(name = "getword")
    async def get_word(self, ctx, *, word: str):
        try:
            response = requests.get(f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={self.DICTIONARY_API}")
            word = response.json()[0]["meta"]["id"]

            if (":" in word):
                index = word.index(":")

                word = word[0:index]

            await ctx.channel.send(word)
        except:
            await ctx.channel.send(f"**{word}** is invalid")

async def setup(bot):
    print("Inside dictionary setup function")
    await bot.add_cog(Dictionary(bot))

    