from discord.ext import commands
import os

class Bot(commands.Bot):
    async def setup_hook(self) -> None:
        for f in os.listdir("ToasterBot/cogs"):
	        if f.endswith(".py"):
		        await self.load_extension("cogs." + f[:-3])