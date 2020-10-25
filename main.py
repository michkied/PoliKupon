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

config = ConfigParser()
config.read('config.ini')
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


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    bot.db = loop.run_until_complete(asyncpg.create_pool(user=db_info['user'], database=db_info['database_name'], password=db_info['password'], max_size=15))

    bot.info = info

    bot.add_cog(Coupons(bot))
    bot.add_cog(Servers(bot))
    bot.add_cog(Masterserver(bot))

    bot.run(info['token'], reconnect=True)

