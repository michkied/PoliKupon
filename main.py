
# PoliKupon by Michał Kiedrzyński (michkied#6677)
# 10.2020


# Importowanie niezbędnych bibliotek & reszty plików
import discord
from discord.ext import commands
from configparser import ConfigParser
from datetime import datetime
import sys
import asyncio
import asyncpg

# Wczytanie ustawień
config = ConfigParser()
config.read('startup.ini')
info = config['STARTUP']
db_info = config['DATABASE']

# Zdefiniowanie obiektu Bota
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=info['prefix'], intents=intents)
bot.remove_command('help')


# Potwierdzenie połączenia
@bot.event
async def on_ready():
    date = datetime.now()
    print('Zalogowano jako:')
    print(bot.user.name)
    print(bot.user.id)
    print(date.strftime('%d.%m.%Y  %H:%M'))
    print('by Michał Kiedrzyński')
    print('------')
    await bot.get_channel(id=int(info['ready_confirmation_channel'])).send(content=date.strftime("`%H:%M:%S` Połączono"))


# Komenda wyłączająca bota
@bot.command()
async def killapp(ctx):
    if int(ctx.author.id) == int(info['owner_id']):
        await ctx.send("**__Użycie tej komendy spowoduje wyłączenie bota. Aby potwierdzić decyzję odpisz 'TAK'__**")

        def check(msg):
            return msg.content.startswith('TAK') and msg.author == ctx.author

        message = await bot.wait_for('message', timeout=5, check=check)
        kod = message.content.strip()
        if kod == "TAK":
            await ctx.send("Wyłączanie...")
            await bot.close()
            await bot.db.close()
            sys.exit()


if __name__ == '__main__':

    # Połączenie z bazą danych
    loop = asyncio.get_event_loop()
    bot.db = loop.run_until_complete(asyncpg.create_pool(user=db_info['user'], database=db_info['database_name'], password=db_info['password'], max_size=15))

    # Uruchomienie bota
    bot.run(info['token'], reconnect=True)
