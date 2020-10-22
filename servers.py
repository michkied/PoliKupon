from discord.ext import commands
from datetime import datetime
import discord
import asyncio
import random
import string


class Servers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @commands.Cog.listener()
    async def on_server_join(self, guild):
        log = self.bot.get_channel(int(self.bot.info['log_channel']))
        await log.send(f'`{datetime.now().strftime("%d.%m.%Y  %H:%M:%S")}` :new: Bot dołączył do nowego serwera {guild.name} (`{guild.id}`)')
        if guild.me.guild_permissions.administrator:
            channel = await guild.create_text_channel('PoliKupon-setup', overwrites={guild.default_role: discord.PermissionOverwrite(read_messages=False)})
            await channel.send(f'**Hej! :wave:**\nPierwszy krok za tobą - bot został poprawnie dodany na serwer!\n\nAby przejść dalej, podaj klucz aktywacyjny serwera (musi to zrobić {guild.owner.mention} lub inna osoba z uprawnieniami administratora). Wyślij go jako wiadomość na tym kanale.\n:warning: Jeżeli nie zrobisz tego w ciągu 10 minut, bot opuści serwer.')

            def check(msg):
                return msg.author == guild.owner or msg.author.guild_permissions.administrator

            while True:
                try:
                    message = (await self.bot.wait_for('message', timeout=600, check=check)).content
                except asyncio.TimeoutError:
                    await guild.leave()
                    return

                key = (await self.db.fetchrow('SELECT * FROM polikupon_klasy WHERE key = $1', message))
                if key is not None:
                    if not key['server']:
                        await self.db.execute('UPDATE polikupon_klasy SET server = $1 WHERE key = $2', str(guild.id), key['key'])
                        await channel.send(f':white_check_mark: **Serwer został poprawnie aktywowany :tada:**\nWszystko gotowe, miłego korzystania!')
                        await log.send(f'`{datetime.now().strftime("%d.%m.%Y  %H:%M:%S")}` :closed_lock_with_key: Serwer {guild.name} (`{guild.id}`) został aktywowany kluczem `{message}` ({key["klasa"]})')
                        return

                await channel.send(f':x: **Klucz {message} jest niepoprawny!**\nPodaj poprawny klucz aktywacyjny')
                await log.send(f'`{datetime.now().strftime("%d.%m.%Y  %H:%M:%S")}` :x: Podano niepoprawny klucz {message} na serwerze {guild.name} (`{guild.id}`)')
        else:
            await log.send(f'`{datetime.now().strftime("%d.%m.%Y  %H:%M:%S")}` :lock: Bot nie ma admina na serwerze {guild.name} (`{guild.id}`)')
            await guild.text_channels[0].send(':x: **Do poprawnego działania bot wymaga uprawnień administratora. Dodaj bota jeszcze raz, zwracając uwagę na zaznaczenie odpowiedniego uprawnienia na karcie dodawania**')
            await guild.leave()

    @commands.command()
    async def keys(self, ctx, arg1=None, arg2=None):
        if int(ctx.author.id) == int(self.bot.info['owner_id']):
            if arg1 == 'list':
                keys = await self.db.fetch('SELECT * FROM polikupon_klasy')
                text = '>>> '
                for key in keys:
                    text += f'`{key["key"]}` - {key["klasa"]} - {key["server"]}\n'
                await ctx.send(text)

            elif arg1 == 'add':
                if arg2 is not None:
                    b = 0
                    key = ''
                    while b < 5:
                        key += ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5)) + '-'
                        b += 1
                    key = key.upper()[:-1]
                    await self.db.execute('INSERT INTO polikupon_klasy(klasa, key) VALUES($1, $2)', arg2, key)
                    await ctx.send(f'Wygenerowano klucz {key} i przypisano go do klasy {arg2}')

            elif arg1 == 'remove':
                if arg2 is not None:
                    rsp = await self.db.execute('DELETE FROM polikupon_klasy WHERE key = $1', arg2)
                    await ctx.send(rsp)

            else:
                await ctx.send('```{0}keys list\n{0}keys add <klasa>\n{0}keys remove <key>```'.format(self.bot.info['prefix']))
