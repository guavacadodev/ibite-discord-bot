import os
import discord
from discord.ext import commands

# ---- YOUR IDS ----
GUILD_ID = 848119845144100924
WELCOME_CHANNEL_ID = 907003823866929162
MEMBER_ROLE_ID = 1081346773349584926
TOTAL_MEMBERS_CHANNEL_ID = 907013404546433054

# ---- BOT SETUP ----
intents = discord.Intents.default()
intents.members = True  # REQUIRED
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

    guild = bot.get_guild(GUILD_ID)
    if guild:
        await update_member_count(guild)

@bot.event
async def on_member_remove(member):
    if member.guild.id != GUILD_ID:
        return

    await update_member_count(member.guild)

async def update_member_count(guild: discord.Guild):
    channel = guild.get_channel(TOTAL_MEMBERS_CHANNEL_ID)

    if channel is None:
        print("❌ Member count channel not found.")
        return

    try:
        count = guild.member_count
        await channel.edit(name=f"Total Members: {count}")
        print(f"✅ Updated member count to {count}")
    except Exception as e:
        print(f"❌ Failed to update member count: {e}")

@bot.event
async def on_member_join(member: discord.Member):
    if member.guild.id != GUILD_ID:
        return

    # ---- Assign Role ----
    role = member.guild.get_role(MEMBER_ROLE_ID)

    if role:
        try:
            await member.add_roles(role, reason="Auto-assign Member role on join")
            print(f"Added Member role to {member.name}")
        except Exception as e:
            print(f"Failed to add role: {e}")
    else:
        print("Member role not found!")

    # ---- Send Welcome Message ----
    channel = bot.get_channel(WELCOME_CHANNEL_ID)

    if channel:
        embed = discord.Embed(
            title="🍽️ Welcome to iBite!",
            description=f"Hey {member.mention} 👋\n\nWelcome to the official iBite server!",
            color=discord.Color.green()
        )
        embed.add_field(
            name="🔥 What You Can Do Here",
            value="• Get updates on iBite\n• Join food discussions\n• Test new features\n• Become a beta foodie 🍔",
            inline=False
        )
        embed.set_footer(text="Let’s build the future of food together.")

        await channel.send(embed=embed)
        await update_member_count(member.guild)

# ---- RUN BOT ----
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)