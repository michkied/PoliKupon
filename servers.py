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

    async def log(self, message):
        log = self.bot.get_channel(int(self.bot.info['log_channel']))
        await log.send(f'`{datetime.now().strftime("%d.%m.%Y  %H:%M:%S")}` {message}')

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.log(f':new: Bot dołączył do nowego serwera {guild.name} (`{guild.id}`)')
        if guild.me.guild_permissions.administrator:
            if str(guild.id) != self.bot.info['tchr_server']:
                channel = await guild.create_text_channel('PoliKupon-setup', overwrites={guild.default_role: discord.PermissionOverwrite(read_messages=False)})
                await channel.send(f'**Hej! :wave:**\nPierwszy krok za tobą - bot został poprawnie dodany na serwer!\n\n**Aby przejść dalej, podaj klucz aktywacyjny serwera** (musi to zrobić osoba z uprawnieniami administratora). Wyślij go jako wiadomość na tym kanale.\n:warning: Jeżeli nie zrobisz tego w ciągu 10 minut, bot opuści serwer.')

                await asyncio.sleep(2)

                def check(msg):
                    return (msg.author == guild.owner or msg.author.guild_permissions.administrator) and msg.author != guild.me and msg.channel == channel

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
                            await self.log(f':closed_lock_with_key: Serwer **{guild.name}** (`{guild.id}`) został aktywowany kluczem `{message}` ({key["klasa"]})')
                            return

                    await channel.send(f':x: **Klucz `{message}` jest niepoprawny!**\nPodaj poprawny klucz aktywacyjny')
                    await self.log(f':x: Podano niepoprawny klucz `{message}` na serwerze {guild.name} (`{guild.id}`)')
            else:
                await self.log(f':teacher: Bot dołączył do serwera nauczycieli **{guild.name}** (`{guild.id}`)')
        else:
            await self.log(f':lock: Bot nie ma admina na serwerze {guild.name} (`{guild.id}`)')
            await guild.text_channels[0].send(':x: **Do poprawnego działania bot wymaga uprawnień administratora. Dodaj bota jeszcze raz, zwracając uwagę na zaznaczenie odpowiedniego uprawnienia na karcie dodawania**')
            await guild.leave()

    @commands.command()
    async def keys(self, ctx, arg1=None, *, arg2=None):
        if int(ctx.author.id) == int(self.bot.info['owner']):
            if arg1 == 'list':
                keys = sorted(await self.db.fetch('SELECT * FROM polikupon_klasy'), key=lambda i: (i['klasa']))
                text = '>>> '
                for key in keys:
                    text += f'**{key["klasa"]}** - `{key["key"]}` - `{key["server"]}`\n'
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
                    await ctx.send(f'**Wygenerowano klucz `{key}` i przypisano go do klasy `{arg2}`**')

            elif arg1 == 'remove':
                if arg2 is not None:
                    rsp = await self.db.execute('DELETE FROM polikupon_klasy WHERE key = $1', arg2)
                    if rsp == 'DELETE 1':
                        await ctx.send(f':white_check_mark: **Usunięto klucz `{arg2}`**')
                    else:
                        await ctx.send(':x: **Nie ma takiego klucza**')

            else:
                await ctx.send('```{0}keys list\n{0}keys add <klasa>\n{0}keys remove <klucz>```'.format(self.bot.info['prefix']))

