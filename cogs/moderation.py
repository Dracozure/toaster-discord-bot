import datetime
from discord.ext import commands
import discord

class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="smokebreak")
    @commands.has_permissions(ban_members = True)
    async def smoke_break(self, ctx, member: discord.Member, duration, *, reason: str):
        time = datetime.timedelta(seconds = int(duration))

        await member.edit(timed_out_until=discord.utils.utcnow() + time)

        if (reason):
            await ctx.send(f'{member.mention} has been hauled off to jail for **{reason}**')

async def setup(bot):
    print("Inside moderation setup function")
    await bot.add_cog(Moderation(bot))
