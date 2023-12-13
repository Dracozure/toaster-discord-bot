import sqlite3
from discord.ext import commands
import requests
from dotenv import load_dotenv
import os
from pytz import timezone

class Dictionary(commands.Cog):
    conn = sqlite3.connect("words.db") 
    c = conn.cursor()
    THESAURUS_API = os.getenv("THESAURUS_API")
    DICTIONARY_API = os.getenv("DICTIONARY_API")

    def __init__(self, bot):
        self.bot = bot
        load_dotenv()
        self.c.execute("""CREATE TABLE IF NOT EXISTS words (
                word text,
                author_id integer,
                timestamp text,
                messge_link text
        )""")
        self.conn.commit()
    
    @commands.Cog.listener()
    async def on_message(self, message):
        channel_id = message.channel.id
        guild_id = message.guild.id
        date_format = "%Y-%m-%d %H:%M:%S"

        author_id = message.author.id
        message_link = message.jump_url
        timestamp = message.created_at.astimezone(timezone("US/Pacific")).strftime(date_format)

        correct_reaction = "✅"
        wrong_reaction = "❌"

        if (message.author.bot):
            return

        if (guild_id != 774455931442298901 or channel_id != 1144334325765120143):
            return
        
        try:
            response = requests.get(f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{message.content}?key={self.DICTIONARY_API}")
            word = response.json()[0]["meta"]["id"]

            if (":" in word):
                index = word.index(":")

                word = word[0:index]

            word_exist = await self.get_word(word)
            starting_letter = await self.get_last_letter()

            if (word.strip()[0] != starting_letter and starting_letter != ""):
                await message.add_reaction(wrong_reaction)
                
                await message.channel.send(f"Your word must start with the letter **{starting_letter}**")

                return

            if (not word_exist):
                await message.add_reaction(correct_reaction)

                await self.insert_word(word, author_id, timestamp, message_link)
                
                await self.save_last_word(word)
            else:
                await message.add_reaction(wrong_reaction)
                
                await message.channel.send(f"**{word}** has already been typed")
        except:
            await message.add_reaction(wrong_reaction)

            await message.channel.send(f"**{message.content}** is invalid")

    async def insert_word(self, word, author_id, timestamp, message_link):
        self.c.execute(f"INSERT INTO words VALUES ('{word}', '{author_id}', '{timestamp}','{message_link}')")

        self.conn.commit()

    async def get_word(self, word):
        try:
            self.c.execute(f"SELECT * FROM words WHERE word = '{word}'")

            fetched_word = self.c.fetchone()

            self.conn.commit()

            return len(fetched_word) > 0
        except:
            return False
        
    async def get_last_letter(self):
        last_word = open("./current_word.txt", "r").read().strip()

        if (last_word == ""):
            return ""

        return last_word[-1]
    
    async def save_last_word(self, word):
        file='./current_word.txt' 

        with open(file, 'w') as filetowrite:
            filetowrite.write(word)

async def setup(bot):
    print("Inside dictionary setup function")
    await bot.add_cog(Dictionary(bot))

    