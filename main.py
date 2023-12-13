import discord
from discord import Intents
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
from bot import Bot
from dotenv import load_dotenv
import os

intents = Intents.all()
intents.message_content = True
bot = Bot(command_prefix = ">", intents = intents)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

@bot.command(name="koreanTad")
async def korean_tad(ctx):
    file = discord.File("./assets/videos/korean_tad.mov")
    await ctx.send("Tad moment", file = file)

@bot.command(name="koreanTad2")
async def korean_tad(ctx):
    file = discord.File("./assets/videos/korean_tad_2.mp4")
    await ctx.send("Another Tad moment", file = file)

@bot.event
async def on_member_update(before, after):
    if before.id == 1081523614475624498 and after.display_name != "khỉ yêu dầu":
        await after.edit(nick = "khỉ yêu dầu")

@bot.command(name="changenick")
async def change_nick(ctx, member: discord.Member, *, nick):
    if ctx.message.author.id == 313393208744869892:
        await member.edit(nick = nick)

@bot.event
async def on_message(message):
    if message.author.id == 509287976208039958:
        messages = ["Hello hello! <:SipDuck:1136192477498449930>", 
                    "Hello hello! <:DuckSip:1108503068993142884>",
                    "Hello hello! <:birdsip:800498740279902240>"]
        if message.content in messages:
            author = message.author
            await message.delete()
            await message.channel.send(f"Nice try {author.mention}")
    await bot.process_commands(message)

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000, 1)}ms")

@bot.command(name="createpassport")
async def create_passport(ctx, user: discord.User):
    img = Image.open("./assets/img/pass_page_1.png")
    font = ImageFont.truetype("./assets/fonts/Literaturnaya_Regular.ttf", 100)
    
    data = BytesIO(await user.avatar.read())  
    pfp = Image.open(data)
    pfp = pfp.resize((177, 177))
    img.paste(pfp, (70, 650))

    draw = ImageDraw.Draw(img)

    name_box = draw.textbbox((0,0), "Hello", font = font)
    draw.rectangle(name_box, fill = "Red", width = 0)
    draw.text((0, 0), "Hello", font = font, fill = "black")

    placed_of_birth = draw.textbbox((0,0), "Hello", font = font)
    draw.rectangle(name_box, fill = "Red", width = 0)
    draw.text((0, 0), "Hello", font = font, fill = "black")

    name_box = draw.textbbox((0,0), "Hello", font = font)
    draw.rectangle(name_box, fill = "Red", width = 0)
    draw.text((0, 0), "Hello", font = font, fill = "black")

    img.save("profile.png")

    await ctx.send(file=discord.File("./profile.png"))

@bot.command(name="getdisplaypfp")
async def get_display_pfp(ctx, user: discord.User):
    pfp = user.display_avatar
    embed = discord.Embed(title=f"Member Display Avatar", description="", color=0xffff00)

    embed.set_thumbnail(url=(pfp.url))

    await ctx.send(embed = embed)

@bot.command(name="purgechannel")
async def purge_channel(ctx, limit):
    if ctx.message.author.id != 313393208744869892:
        await ctx.send("No perms!")
        return
    
    await ctx.channel.purge(limit = int(limit))

bot.run(f"{BOT_TOKEN}")


 