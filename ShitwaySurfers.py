import discord
import random
from discord.ext import tasks, commands

intents = discord.Intents.default()
intents.members = True
bot = discord.Bot(intents=intents)

squares = ["⬛" for _ in range(100)]
squares[44] = "🟩"
pos = 44
score = 0
enemies = []
message = None


@bot.event
async def on_ready():
    print(f'Bot online {bot.user}!')
    game_loop.start()
    await respawn_enemies()


class MyView(discord.ui.View):
    @discord.ui.button(label="LEFT", style=discord.ButtonStyle.primary, emoji="⬅️")
    async def left_button_callback(self, button, interaction):
        global pos
        squares[pos] = "⬛"
        pos -= 1
        if pos < 0:
            pos = 0
        squares[pos] = "🟩"
        await update_message(interaction)

    @discord.ui.button(label="RIGHT", style=discord.ButtonStyle.primary, emoji="➡️")
    async def right_button_callback(self, button, interaction):
        global pos
        squares[pos] = "⬛"
        pos += 1
        if pos >= len(squares):
            pos = len(squares) - 1
        squares[pos] = "🟩"
        await update_message(interaction)

    @discord.ui.button(label="UP", style=discord.ButtonStyle.primary, emoji="⬆️")
    async def up_button_callback(self, button, interaction):
        global pos
        squares[pos] = "⬛"
        pos -= 10
        if pos < 0:
            pos += 100
        squares[pos] = "🟩"
        await update_message(interaction)

    @discord.ui.button(label="DOWN", style=discord.ButtonStyle.primary, emoji="⬇️")
    async def down_button_callback(self, button, interaction):
        global pos
        squares[pos] = "⬛"
        pos += 10
        if pos >= len(squares):
            pos -= 100
        squares[pos] = "🟩"
        await update_message(interaction)

    @discord.ui.button(label="STOP", style=discord.ButtonStyle.danger, emoji="❌")
    async def stop_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await stop_embed(interaction)


async def stop_embed(interaction: discord.Interaction = None):
    global message
    embed = discord.Embed(
        title="Shitway Surfers - Game Over",
        description=game(),
        color=discord.Color.blurple()
    )
    embed.add_field(
        name=f"Final Score: {score}",
        value=" ",
        inline=False
    )
    if interaction:
        await interaction.response.send_message(embed=embed)
    else:
        if message:
            await message.channel.send(embed=embed)

    if message:
        await message.delete()
        message = None

    game_loop.stop()


async def update_message(interaction=None):
    global score, pos, message

    if pos in enemies:
        await stop_embed(interaction)
        return

    embed = discord.Embed(
        title="Shitway Surfers",
        description=game(),
        color=discord.Color.blurple()
    )
    embed.add_field(
        name=f"Score: {score}",
        value="",
        inline=False
    )

    if interaction:
        await interaction.response.edit_message(embed=embed, view=MyView())
    else:
        if message:
            await message.edit(embed=embed, view=MyView())


@tasks.loop(seconds=2)
async def game_loop():
    global pos
    global score
    score += 1

    squares[pos] = "⬛"
    pos -= 10
    if pos < 0:
        await respawn_enemies()
        pos += 100
    squares[pos] = "🟩"
    await update_message()


async def respawn_enemies():
    global enemies

    for enemy in enemies:
        squares[enemy] = "⬛"
    enemies = []

    while len(enemies) < 24:
        new_enemy = random.randrange(0, 100)
        if new_enemy != pos and new_enemy not in enemies:
            squares[new_enemy] = "🟥"
            enemies.append(new_enemy)

    await update_message()


def game():
    border = "🟦"
    size = 10
    lines = []

    for i in range(size):
        line = border + ''.join(squares[i*size:(i+1)*size]) + border
        lines.append(line)

    return '\n'.join(lines)


@bot.slash_command()
async def shitwaysurfers(ctx):
    global message
    squares[pos] = "🟩"

    embed = discord.Embed(
        title="Shitway Surfers",
        description=game(),
        color=discord.Color.blurple()
    )
    message = await ctx.send(embed=embed, view=MyView())
    await respawn_enemies()


bot.run("BOT-TOKEN")
