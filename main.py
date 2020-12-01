# PoliKupon
#
# Made with Python 3.8, PostgreSQL & ❤love❤ by Michał Kiedrzyński (michkied#6677)
# 10.2020

import discord
from discord.ext import commands
from configparser import ConfigParser
from datetime import datetime
import sys
import asyncio
import asyncpg

from coupons import Coupons
from servers import Servers
from master_server import Masterserver
import pathlib

config = ConfigParser()
config.read(str(pathlib.Path(__file__).parent.absolute())+'/config.ini')
info = config['INFO']
db_info = config['DATABASE']

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=info['prefix'], intents=intents)
bot.remove_command('help')


@bot.event
async def on_ready():
    date = datetime.now()
    print('Zalogowano jako:')
    print(bot.user.name)
    print(bot.user.id)
    print(date.strftime('%d.%m.%Y  %H:%M'))
    print('by Michał Kiedrzyński')
    print('------')
    await bot.get_channel(id=int(info['log_channel'])).send(content=date.strftime("`%H:%M:%S` Połączono"))
    await (await bot.get_channel(int(info['shop_channel'])).fetch_message(int(info['shop_message']))).add_reaction(info['shop_emoji'])


@bot.command()
async def killapp(ctx):
    if int(ctx.author.id) == int(info['owner']):
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


@bot.command()
async def pomoc(ctx):
    text = "**__Jak skorzystać z kuponu?__**\n`1.` Na lekcyjnym kanale tekstowym użyj komendy `{0}kupon`\n" \
           "`2.` Potwierdź chęć wykorzystania kuponu reagując :white_check_mark: na odpowiedź bota\n" \
           "`3.` Zaczekaj aż nauczyciel zatwierdzi wykorzystanie kuponu\n" \
           "`4.` Ciesz się ze swojego nieprzygotowania!\n\n" \
           "**__Jak sprawdzić ile mam kuponów?__**\n" \
           "Aby sprawdzić ilość posiadanych kuponów, użyj komendy `{0}moje_kupony`"

    await ctx.send(text.format(info['prefix']))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    bot.db = loop.run_until_complete(asyncpg.create_pool(user=db_info['user'], database=db_info['database_name'], password=db_info['password'], max_size=15))

    bot.info = info

    if info['shop_active'] == 'y':
        bot.shop_is_on = True
    else:
        bot.shop_is_on = False

    bot.add_cog(Coupons(bot))
    bot.add_cog(Servers(bot))
    bot.add_cog(Masterserver(bot))

    bot.run(info['token'], reconnect=True)

