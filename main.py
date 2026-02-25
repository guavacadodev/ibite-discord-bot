import os
import discord
from discord.ext import commands

# ---- YOUR IDS ----
GUILD_ID = 848119845144100924
WELCOME_CHANNEL_ID = 907003823866929162

# ---- BOT SETUP ----
intents = discord.Intents.default()
intents.members = True  # REQUIRED for member join events

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    # Make sure it’s your server
    if member.guild.id != GUILD_ID:
        return

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

# ---- RUN BOT ----
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)