from discord.ext import commands
from datetime import datetime
from pytz import timezone
import discord

class Logging(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.content != after.content:
            author = after.author
            date_format = "%Y-%m-%d %H:%M:%S"
            my_timezone = "PST"
            before_attachments = []
            after_attachments = []

            timestamp_original = after.created_at.astimezone(timezone("US/Pacific")).strftime(date_format)
            timestamp_edit = datetime.now().astimezone(timezone("US/Pacific")).strftime(date_format)

            if (before.attachments):
                before_attachments = before.attachments

            if (after.attachments):
                after_attachments = after.attachments

            author_info_str = f"""
            Author: <@{author.id}>
            User ID: {author.id}
            User Name: {author.name}"""

            timestamp_info_str = f"""
            Timezone: {my_timezone}
            Created At: {timestamp_original}
            Edited At: {timestamp_edit}"""

            message_info_str = f"""
            Message Before: {before.content}
            Message After: {after.content}"""

            embed = discord.Embed(title = "Author Info", description = author_info_str, color = author.color)
            
            embed.add_field(name = "Timestamp Info", value = timestamp_info_str, inline = False)
            embed.add_field(name = "Message Info", value = message_info_str, inline = False)

            await after.channel.send(embed = embed)

            if after.attachments:
                await after.channel.send(content = after.attachments[0].url)

async def setup(bot):
    print("Inside logging setup function")
    await bot.add_cog(Logging(bot))

    