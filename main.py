import discord
from discord.ext import commands
import json
import os
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

ARQUIVO = "farm.json"
CANAL_LIDERES_ID = 1486499265562935498

# =========================
# BANCO JSON
# =========================
if not os.path.exists(ARQUIVO):
    with open(ARQUIVO, "w") as f:
        json.dump({}, f)


def carregar():
    with open(ARQUIVO, "r") as f:
        return json.load(f)


def salvar(dados):
    with open(ARQUIVO, "w") as f:
        json.dump(dados, f, indent=4)


# =========================
# BOT ONLINE
# =========================
@bot.event
async def on_ready():
    print(f"✅ Bot online como {bot.user}")


# =========================
# FARM
# =========================
@bot.command()
async def farm(ctx, *args):

    # apagar comando
    if ctx.guild:
        perms = ctx.channel.permissions_for(ctx.guild.me)
        if perms.manage_messages:
            try:
                await ctx.message.delete()
            except:
                pass

    dados = carregar()
    uid = str(ctx.author.id)

    if uid not in dados:
        dados[uid] = {
            "nome": ctx.author.name,
            "aço": 0,
            "chip": 0,
            "tecido": 0
        }

    itens_validos = ["aço", "chip", "tecido"]
    registro = {"aço": 0, "chip": 0, "tecido": 0}

    if len(args) % 2 != 0:
        await ctx.send("❌ Use: !farm aço 2 chip 2 tecido 2", delete_after=20)
        return

    for i in range(0, len(args), 2):
        item = args[i].lower()

        if item not in itens_validos:
            await ctx.send(f"❌ Item inválido: {item}", delete_after=20)
            return

        try:
            quantidade = int(args[i + 1])
        except:
            await ctx.send("❌ Quantidade inválida.", delete_after=20)
            return

        registro[item] += quantidade
        dados[uid][item] += quantidade

    salvar(dados)

    embed = discord.Embed(
        title="📦 Farm registrado",
        color=discord.Color.green()
    )

    for item, qtd in registro.items():
        if qtd > 0:
            embed.add_field(name=item.capitalize(), value=qtd)

    await ctx.send(embed=embed, delete_after=20)


# =========================
# RANKING
# =========================
@bot.command()
async def ranking(ctx, item: str = None):

    # apagar comando
    if ctx.guild:
        perms = ctx.channel.permissions_for(ctx.guild.me)
        if perms.manage_messages:
            try:
                await ctx.message.delete()
            except:
                pass

    dados = carregar()
    ranking = []

    for user in dados.values():
        if item:
            item = item.lower()
            if item not in ["aço", "chip", "tecido"]:
                await ctx.send("❌ Use aço, chip ou tecido", delete_after=20)
                return
            total = user[item]
            ranking.append((user["nome"], total))
        else:
            total = user["aço"] + user["chip"] + user["tecido"]
            ranking.append((user, total))

    ranking.sort(key=lambda x: x[1], reverse=True)

    embed = discord.Embed(
        title="🏆 Ranking" if not item else f"🏆 Ranking de {item}",
        color=discord.Color.gold()
    )

    if item:
        for i, (nome, total) in enumerate(ranking[:10], start=1):
            embed.add_field(name=f"{i}. {nome}", value=str(total), inline=False)
    else:
        for i, (user, total) in enumerate(ranking[:10], start=1):
            embed.add_field(
                name=f"{i}. {user['nome']} ({total})",
                value=(
                    f"🔩 Aço: {user['aço']}\n"
                    f"💻 Chip: {user['chip']}\n"
                    f"🧵 Tecido: {user['tecido']}"
                ),
                inline=False
            )

    await ctx.send(embed=embed, delete_after=20)


# =========================
# RELATÓRIO
# =========================
@bot.command()
async def relatorio(ctx):

    # apagar comando
    if ctx.guild:
        perms = ctx.channel.permissions_for(ctx.guild.me)
        if perms.manage_messages:
            try:
                await ctx.message.delete()
            except:
                pass

    dados = carregar()
    canal = bot.get_channel(CANAL_LIDERES_ID)

    if canal is None:
        await ctx.send("❌ Canal não encontrado.", delete_after=20)
        return

    embed = discord.Embed(
        title="📊 Relatório de Farm",
        description=f"Data: {datetime.now().strftime('%d/%m/%Y')}",
        color=discord.Color.purple()
    )

    for user in dados.values():
        embed.add_field(
            name=user["nome"],
            value=f"Aço: {user['aço']} | Chip: {user['chip']} | Tecido: {user['tecido']}",
            inline=False
        )

    await canal.send(embed=embed)
    await ctx.send("✅ Relatório enviado!", delete_after=20)


# =========================
# RESET GERAL
# =========================
@bot.command()
async def resetar(ctx):

    # apagar comando
    if ctx.guild:
        perms = ctx.channel.permissions_for(ctx.guild.me)
        if perms.manage_messages:
            try:
                await ctx.message.delete()
            except:
                pass

    if not any(role.name == "Líder" for role in ctx.author.roles):
        await ctx.send("❌ Apenas líderes podem usar.", delete_after=20)
        return

    dados = carregar()

    for uid in dados:
        dados[uid]["aço"] = 0
        dados[uid]["chip"] = 0
        dados[uid]["tecido"] = 0

    salvar(dados)

    await ctx.send("🧹 Todos os farms foram zerados!", delete_after=20)


# =========================
# RESET INDIVIDUAL
# =========================
@bot.command()
async def resetaruser(ctx, membro: discord.Member):

    # apagar comando
    if ctx.guild:
        perms = ctx.channel.permissions_for(ctx.guild.me)
        if perms.manage_messages:
            try:
                await ctx.message.delete()
            except:
                pass

    if not any(role.name == "Líder" for role in ctx.author.roles):
        await ctx.send("❌ Apenas líderes podem usar.", delete_after=20)
        return

    dados = carregar()
    uid = str(membro.id)

    if uid not in dados:
        await ctx.send("❌ Usuário sem registro.", delete_after=20)
        return

    dados[uid]["aço"] = 0
    dados[uid]["chip"] = 0
    dados[uid]["tecido"] = 0

    salvar(dados)

    await ctx.send(f"🧹 Farm de {membro.mention} zerado!", delete_after=20)


# =========================
# INICIAR BOT
# =========================
bot.run(os.getenv("TOKEN"))
