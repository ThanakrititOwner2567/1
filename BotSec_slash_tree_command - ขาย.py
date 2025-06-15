from datetime import timedelta
import discord
from discord.ext import commands
import time # noqa: F401

# ===== CONFIG =====
TOKEN = "TechChill-TOKEN"  # แก้เป็น Token ของคุณ
VC_CHANNEL_ID = "1376595739248951297"  #แก้เป็น IDห้องเสียง ของคุณ ที่จะให้บอทเข้า
LOG_CHANNEL_ID = "1376595980325228564"  #แก้เป็น ID ห้องLog ของคุณ
AUTO_ROLE_ID = "1332149369415143454"  # ID บทบาทที่ให้สมาชิกใหม่
WHITELIST = ["1259054643015848041"]  # user IDs ที่ยกเว้นการตรวจสอบ
BLACKLIST = [""]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"บอทออนไลน์: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"ซิงค์ Slash Commands แล้ว {len(synced)} คำสั่ง")
    except Exception as e:
        print(f"Sync error: {e}")
    try:
        for guild in bot.guilds:
            vc = guild.get_channel(int(VC_CHANNEL_ID))
            if vc and isinstance(vc, discord.VoiceChannel):
                await vc.connect()
                print(f'เข้าห้องเสียง: {vc.name}')
    except Exception as e:
        print(f'VC Error: {e}')

def log_action(title, description, color=discord.Color.blurple()):
    async def inner():
        channel = bot.get_channel(LOG_CHANNEL_ID)
        if channel:
            embed = discord.Embed(title=title, description=description, color=color)
            await channel.send(embed=embed)
    return inner

@bot.tree.command(name="kick", description="เตะสมาชิกออกจากเซิร์ฟเวอร์")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "ไม่ระบุ"):
    if interaction.user.id in BLACKLIST:
        embed = discord.Embed(title="คำสั่งถูกปฏิเสธ", description="คุณไม่มีสิทธิใช้คำสั่งนี้", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    await member.kick(reason=reason)
    embed = discord.Embed(title="KICK", description=f"{member.mention} ถูกเตะ", color=discord.Color.orange())
    await interaction.response.send_message(embed=embed)
    await log_action("KICK", f"{member} ถูกเตะโดย {interaction.user} ด้วยเหตุผล: {reason}")()

@bot.tree.command(name="ban", description="แบนสมาชิกออกจากเซิร์ฟเวอร์")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "ไม่ระบุ"):
    if interaction.user.id in BLACKLIST:
        embed = discord.Embed(title="คำสั่งถูกปฏิเสธ", description="คุณไม่มีสิทธิใช้คำสั่งนี้", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    await member.ban(reason=reason)
    embed = discord.Embed(title="BAN", description=f"{member.mention} ถูกแบน", color=discord.Color.red())
    await interaction.response.send_message(embed=embed)
    await log_action("BAN", f"{member} ถูกแบนโดย {interaction.user} ด้วยเหตุผล: {reason}")()

@bot.tree.command(name="mute", description="Mute สมาชิกชั่วคราว")
async def mute(interaction: discord.Interaction, member: discord.Member, duration: int = 60, reason: str = "ไม่ระบุ"):
    if interaction.user.id in BLACKLIST:
        embed = discord.Embed(title="คำสั่งถูกปฏิเสธ", description="คุณไม่มีสิทธิใช้คำสั่งนี้", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    try:
        await member.edit(timed_out_until=discord.utils.utcnow() + timedelta(seconds=duration))
        embed = discord.Embed(title="MUTE", description=f"{member.mention} ถูก mute {duration} วินาที", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)
        await log_action("MUTE", f"{member} ถูก mute โดย {interaction.user} เป็นเวลา {duration} วิ ด้วยเหตุผล: {reason}")()
    except Exception as e:
        embed = discord.Embed(title="เกิดข้อผิดพลาด", description=str(e), color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)

bot.run(TOKEN)
