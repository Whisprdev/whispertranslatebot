import discord
from googletrans import Translator
from discord.ext import commands
from discord import app_commands
from discord import Interaction
from config import token
from translation import LANGUAGES, smallLang
from typing import Literal, Optional

# ♡⊹˚₊made with love by whisprdev ₊˚⊹♡
# ------------------------------------- #

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

translator = Translator()


@bot.event
async def on_ready():
    print("Translator bot ready")


# ----------- Events -----------------

@bot.command()
async def reply(ctx, lang):
    message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
    userMessage = message.content
    translatedMessage = translator.translate(userMessage, dest=lang)
    await ctx.send(f'This message translated to {LANGUAGES[lang]} is: {translatedMessage.text}')


@bot.command()
async def translate(ctx, arg):
    translator = Translator()
    translator.translate(arg)

    await ctx.send(f"Sent by {ctx.author}")
    await ctx.send(translator.translate(arg))


@bot.tree.command()
@app_commands.describe(
    target_language='The language you want your message translated to',
    message='The message you want translated',
)
async def translate(interaction: discord.Interaction, target_language: str, message: str):
    """Translates a message to a specific language."""
    translatedMessage = translator.translate(message, dest=target_language)
    await interaction.response.send_message(f'{interaction.user.mention}: {translatedMessage.text}')


@translate.autocomplete('target_language')
async def translate_autocomplete(
        interaction: discord.Interaction,
        current: str,
) -> list[app_commands.Choice[str]]:
    languages = smallLang
    return [
        app_commands.Choice(name=fruit, value=fruit)
        for fruit in languages if current.lower() in fruit.lower()
    ]


# sync command for slash commands!
@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object],
               spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


bot.run(token)
