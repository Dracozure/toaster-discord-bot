import sqlite3
from discord.ext import commands
import requests
from dotenv import load_dotenv
import os
from pytz import timezone

class Dictionary(commands.Cog):
    connection = sqlite3.connect("words.db") 
    cursor = connection.cursor()
    THESAURUS_API = os.getenv("THESAURUS_API")
    DICTIONARY_API = os.getenv("DICTIONARY_API")

    def __init__(self, bot):
        self.bot = bot
        load_dotenv()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS words (
                word text,
                author_id integer,
                timestamp text,
                messge_link text
        )""")
        self.connection.commit()

    @commands.command(name = "getwordinfo")
    async def get_word_info(self, ctx, word):
        response = requests.get(f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={self.DICTIONARY_API}")

        word = response.json()[0]["meta"]["id"].lower().strip()
        print(word)
        stem_set = set(map(lambda stem: stem.split(" ")[0], response.json()[0]["meta"]["stems"]))
        for word in stem_set:
            print(word)
        short_def = response.json()[0]["shortdef"] #List
        part_of_speech = response.json()[0]["fl"]
    
    @commands.Cog.listener()
    async def on_message(self, message):
        channel_id = message.channel.id
        guild_id = message.guild.id
        date_format = "%Y-%m-%d %H:%M:%S"

        author_id = message.author.id
        last_author_id = await self.get_last_author()
        message_link = message.jump_url
        timestamp = message.created_at.astimezone(timezone("US/Pacific")).strftime(date_format)

        correct_reaction = "✅"
        wrong_reaction = "❌"

        if (message.author.bot):
            return

        if (guild_id != 520337076659421192 or channel_id != 1144334325765120143):
            return
        
        if (last_author_id != "" and int(author_id) == int(last_author_id)):
            await message.channel.send("Wait for someone else to input word")

            return
        
        try:
            response = requests.get(f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{message.content}?key={self.DICTIONARY_API}")

            dict_word = response.json()[0]["meta"]["id"].lower().strip()
            user_word = message.content.lower().strip()
            word_set = set(map(lambda stem: stem.split(" ")[0], response.json()[0]["meta"]["stems"]))
            starting_letter = await self.get_last_letter()

            if (":" in dict_word): #Sometimes there are multiple definitions and API returns word with colon. Ex: hey:1
                index = dict_word.index(":")

                dict_word = dict_word[0:index]

            word_set.add(dict_word)

            if (user_word not in word_set): #Sometimes dictionary will "autocorrect" which returns wrong word
                raise Exception()

            if (user_word[0] != starting_letter and starting_letter != ""): 
                await message.add_reaction(wrong_reaction)
                await message.channel.send(f"Your word must start with the letter **{starting_letter}**")

                return
            
            word_already_typed = await self.check_word_exist(word_set, user_word)

            if (not word_already_typed):
                await message.add_reaction(correct_reaction)
                await self.insert_word(user_word, author_id, timestamp, message_link)
                await self.save_last_word(user_word)
                await self.save_last_author(author_id)
            else:
                await message.add_reaction(wrong_reaction)
                await message.channel.send(f"**{message.content}** has already been typed")
        except:
            await message.add_reaction(wrong_reaction)
            await message.channel.send(f"**{message.content}** is invalid")

    async def insert_word(self, word, author_id, timestamp, message_link):
        word = word.replace("'", "''")
        self.cursor.execute(f"INSERT INTO words VALUES ('{word}', '{author_id}', '{timestamp}','{message_link}')")

        self.connection.commit()

    async def check_word_exist(self, word_set, user_word):
        for word in word_set:
            try:
                word = word.replace("'", "''")

                self.cursor.execute(f"SELECT * FROM words WHERE word = '{word}'")

                fetched_word = self.cursor.fetchone()

                self.connection.commit()

                if len(fetched_word) > 0 and fetched_word[0] == user_word:
                    return True
            except:
                continue

        return False
        
    async def get_last_letter(self):
        last_word = open("./current_word.txt", "r").read().strip()

        if (last_word.strip() == ""):
            return ""
        
        trimmed_last_word = await self.trim_word_alpha(last_word)

        return trimmed_last_word[-1]
    
    async def get_last_author(self):
        last_author_id = open("./last_author.txt", "r").read().strip()

        if (last_author_id.strip() == ""):
            return ""

        return last_author_id
    
    async def save_last_word(self, word):
        file = "./current_word.txt" 

        with open(file, "w") as filetowrite:
            filetowrite.write(word)

    async def save_last_author(self, author_id):
        file = "./last_author.txt"

        with open(file, "w") as filetowrite:
            filetowrite.write(str(author_id))

    async def trim_word_alpha(self, word):
        for char in word:
            if (not char.isalpha()):
                word = word.replace(char, "")

        return word

async def setup(bot):
    print("Inside dictionary setup function")
    await bot.add_cog(Dictionary(bot))

    