import os
import discord
from discord.ext import commands
from openai import OpenAI

# ---- YOUR IDS ----
GUILD_ID = 848119845144100924
WELCOME_CHANNEL_ID = 907003823866929162
MEMBER_ROLE_ID = 1081346773349584926
TOTAL_MEMBERS_CHANNEL_ID = 907013404546433054

# ---- BOT SETUP ----
intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # REQUIRED for "!nibbs ..."

bot = commands.Bot(command_prefix="!", intents=intents)

# ---- OPENAI ----
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

NIBBS_INSTRUCTIONS = """
You are Nibbs, the friendly helper for the iBite Discord server.

Your job:
- Help users understand what iBite is and how it works.
- Answer questions about the iBite website: https://ibite.app/home
- Explain the server basics: welcome, roles, where to ask questions, how to get updates.
- Keep answers short, friendly, and practical.

About iBite:
iBite is an app where users walk around their city and collect digital resources like wood, stone, leaves, fruits, etc.
They can craft gear, tools, and other items to upgrade their character and home.

Rules:
- If you don’t know something specific about this Discord server, say so and suggest where to ask (e.g., an announcements or help channel).
- Don’t make up fake iBite features or policies.
"""

async def update_member_count(guild: discord.Guild):
    channel = guild.get_channel(TOTAL_MEMBERS_CHANNEL_ID)
    if channel is None:
        try:
            channel = await bot.fetch_channel(TOTAL_MEMBERS_CHANNEL_ID)
        except Exception as e:
            print(f"❌ Member count channel fetch failed: {e}")
            return

    try:
        await channel.edit(name=f"Total Members: {guild.member_count}")
    except Exception as e:
        print(f"❌ Failed to update member count: {e}")

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    guild = bot.get_guild(GUILD_ID)
    if guild:
        await update_member_count(guild)

@bot.event
async def on_member_remove(member: discord.Member):
    if member.guild.id == GUILD_ID:
        await update_member_count(member.guild)

@bot.event
async def on_member_join(member: discord.Member):
    if member.guild.id != GUILD_ID:
        return

    # Assign Member role
    role = member.guild.get_role(MEMBER_ROLE_ID)
    if role:
        try:
            await member.add_roles(role, reason="Auto-assign Member role on join")
        except Exception as e:
            print(f"❌ Failed to add role: {e}")

    # Welcome message
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel is None:
        try:
            channel = await bot.fetch_channel(WELCOME_CHANNEL_ID)
        except Exception:
            channel = None

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
        await channel.send(embed=embed)

    await update_member_count(member.guild)

# ---- NIBBS AI COMMAND ----
@bot.command(name="nibbs")
async def nibbs(ctx: commands.Context, *, question: str):
    # Optional: prevent spam by limiting to certain channels/roles later
    await ctx.typing()

    try:
        response = client.responses.create(
            model="gpt-5",
            instructions=NIBBS_INSTRUCTIONS,
            input=question
        )
        text = response.output_text.strip()  # Responses API returns output_text :contentReference[oaicite:2]{index=2}
        if not text:
            text = "I didn’t catch that—could you rephrase your question?"
        # Discord message limit safety
        await ctx.send(text[:1900])
    except Exception as e:
        await ctx.send("Nibbs is having trouble right now. Try again in a minute.")
        print(f"❌ Nibbs error: {e}")

# ---- RUN BOT ----
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing.")
if not os.getenv("OPENAI_API_KEY"):
    print("⚠️ OPENAI_API_KEY missing. !nibbs will not work until set.")

bot.run(TOKEN)