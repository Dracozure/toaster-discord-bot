from discord.ext import commands
from datetime import datetime
from pytz import timezone
from discord import app_commands
import discord

class Msg_Logging(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.channel = None
        self.guild = None

    async def cog_load(self):
        pass

    async def cog_unload(self):
        pass

    # Affects multiple servers, only one instance running on multiple servers

    @app_commands.command(name="setchannellogging")
    @app_commands.describe(channelid="id of logging channel")
    async def hello(self, interaction: discord.Interaction, channelid: str):
        try:
            self.guild = interaction.guild
            if not self.guild.get_channel(int(channelid)):
                raise Exception
            self.channel = self.guild.get_channel(int(channelid))
            await interaction.response.send_message(f"Set #{self.channel} as logging channel")
        except Exception:
            await interaction.response.send_message("Invalid channel id")

    @commands.Cog.listener()
    async def on_message_delete(self, message):        
        author = message.author
        date_format = "%Y-%m-%d %H:%M:%S"
        my_timezone = "PST"
        direct_attachments = await self.processAttachments(message)
        timestamp = message.created_at.astimezone(timezone("US/Pacific")).strftime(date_format)

        if (message.author.bot):
            return

        author_info_str = f"""
        Author: <@{author.id}>
        User ID: {author.id}
        User Name: {author.name}"""

        timestamp_info_str = f"""
        Timezone: {my_timezone}
        Deleted At: {timestamp}"""

        message_info_str = f"""
        --__Message Link__--
        {message.jump_url}
        --__Message Deleted__--
        {message.content}"""

        attachments_info_str = f"""
        --__Original Attachments__--
        {direct_attachments}"""

        embed = discord.Embed(title = "MESSAGE DELETION ❌", color = 0xff0000)
        
        embed.add_field(name = "Author Info", value = author_info_str, inline = False)
        embed.add_field(name = "Timestamp Info", value = timestamp_info_str, inline = False)
        embed.add_field(name = "Message Info", value = message_info_str, inline = False)
        embed.add_field(name = "Direct Attachments Info", value = attachments_info_str, inline = False)

        await self.channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):        
        author = after.author
        date_format = "%Y-%m-%d %H:%M:%S"
        my_timezone = "PST"
        direct_attachments = await self.processAttachments(before)
        after_attachments = await self.processAttachments(after)

        if (before.author.bot):
            return

        if (before == after and direct_attachments == after_attachments):
            return

        timestamp_original = after.created_at.astimezone(timezone("US/Pacific")).strftime(date_format)
        timestamp_edit = datetime.now().astimezone(timezone("US/Pacific")).strftime(date_format)

        author_info_str = f"""
        Author: <@{author.id}>
        User ID: {author.id}
        User Name: {author.name}"""

        timestamp_info_str = f"""
        Timezone: {my_timezone}
        Created At: {timestamp_original}
        Edited At: {timestamp_edit}"""

        message_info_str = f"""
        --__Message Link__--
        {after.jump_url}
        --__Message Before__--
        {before.content}
        --__Message After__--
        {after.content}"""

        attachments_info_str = f"""
        --__Original Attachments__--
        {direct_attachments}"""

        embed = discord.Embed(title = "MESSAGE EDIT ⚠️", color = 0xfff700)
        
        embed.add_field(name = "Author Info", value = author_info_str, inline = False)
        embed.add_field(name = "Timestamp Info", value = timestamp_info_str, inline = False)
        embed.add_field(name = "Message Info", value = message_info_str, inline = False)
        embed.add_field(name = "Direct Attachments Info", value = attachments_info_str, inline = False)

        await self.channel.send(embed = embed)

    async def processAttachments(self, message):
        attachments = ""

        if message.attachments:
            for attachment in message.attachments:
                attachments += attachment.content_type + "\n"
                attachments += attachment.url + "\n"

        return attachments

async def setup(bot):
    print("Inside logging setup function")
    await bot.add_cog(Msg_Logging(bot))

    