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

        if (guild_id != 520337076659421192):
            return
        
        # USE THE MESSAGE CONTENT INSTEAD, JUST CHECK FOR RESPONSE, MERRIAM WEBSTER RETURNING SOME WEIRD STUFF
        
        try:
            response = requests.get(f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{message.content}?key={self.DICTIONARY_API}")

            word = response.json()[0]["meta"]["id"].lower().strip()
            starting_letter = await self.get_last_letter()
            word_already_typed = await self.check_word_exist(word)

            if (":" in word): #Sometimes there are multiple definitions and API returns word with colon. Ex: hey:1
                index = word.index(":")

                word = word[0:index]

            if (word != message.content.lower().strip()): #Sometimes dictionary will "autocorrect" which returns wrong word
                raise Exception()

            if (word[0] != starting_letter and starting_letter != ""): 
                await message.add_reaction(wrong_reaction)
                
                await message.channel.send(f"Your word must start with the letter **{starting_letter}**")

                return

            if (not word_already_typed):
                await message.add_reaction(correct_reaction)

                await self.insert_word(word, author_id, timestamp, message_link)
                
                await self.save_last_word(word)
            else:
                await message.add_reaction(wrong_reaction)
                
                await message.channel.send(f"**{message.content}** has already been typed")
        except:
            await message.add_reaction(wrong_reaction)

            await message.channel.send(f"**{message.content}** is invalid")

    async def insert_word(self, word, author_id, timestamp, message_link):
        word = self.trim_word_alpha(word)
        
        self.c.execute(f"INSERT INTO words VALUES ('{word}', '{author_id}', '{timestamp}','{message_link}')")

        self.conn.commit()

    async def check_word_exist(self, word):
        try:
            self.c.execute(f"SELECT * FROM words WHERE word = '{word}'")

            fetched_word = self.c.fetchone()

            self.conn.commit()

            return len(fetched_word) > 0
        except:
            return False
        
    async def get_last_letter(self):
        last_word = open("./current_word.txt", "r").read().strip()

        if (os.stat("./current_word.txt").st_size == 0):
            return ""

        return last_word[-1]
    
    async def save_last_word(self, word):
        file='./current_word.txt' 

        with open(file, 'w') as filetowrite:
            filetowrite.write(word)

    async def trim_word_alpha(self, word):
        for char in word:
            if (not word.isalpha()):
                word = word.replace(char, "")

        return word

async def setup(bot):
    print("Inside dictionary setup function")
    await bot.add_cog(Dictionary(bot))

    