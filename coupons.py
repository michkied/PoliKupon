from discord.ext import commands
from datetime import datetime
import discord
import asyncio


async def activated(db, arg):
    if isinstance(arg, discord.abc.GuildChannel) or isinstance(arg, discord.Guild):
        if isinstance(arg, discord.Guild):
            obj_id = arg.id
        else:
            obj_id = arg.guild.id
        klasa = (await db.fetchrow('SELECT * FROM polikupon_klasy WHERE server = $1', str(obj_id)))
        if klasa:
            return True
    return False


class Coupons(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    async def log(self, message):
        log = self.bot.get_channel(int(self.bot.info['log_channel']))
        await log.send(f'`{datetime.now().strftime("%d.%m.%Y  %H:%M:%S")}` {message}')

    @commands.command()
    async def nowy_kupon(self, ctx, user=None, first_name=None, last_name=None, klasa=None):
        if isinstance(ctx.channel, discord.abc.GuildChannel):
            masters = self.bot.get_guild(int(self.bot.info['master_server'])).get_role(int(self.bot.info['master_role'])).members
            if ctx.author in masters and ctx.guild.id == int(self.bot.info['master_server']):
                if None not in (user, first_name, last_name, klasa):
                    student = discord.utils.get(ctx.guild.members, mention=user)
                    if student is None:
                        student = discord.utils.get(ctx.guild.members, mention=user.replace('!', ''))
                    if student is None:
                        student = discord.utils.get(ctx.guild.members, name=user)
                    if student is None:
                        try:
                            student = discord.utils.get(ctx.guild.members, id=int(user))
                        except (ValueError, TypeError):
                            pass

                    if student is not None:
                        name = first_name + ' ' + last_name

                        max_id = await self.db.fetchrow('SELECT MAX(coupon_id) FROM polikupon_kupony')
                        if max_id['max'] is None:
                            max_id = 0
                        else:
                            max_id = max_id['max']

                        await self.db.execute('INSERT INTO polikupon_kupony(user_id, name, class, coupon_id) VALUES($1, $2, $3, $4)', str(student.id), name, klasa, max_id + 1)
                        await ctx.send(f':white_check_mark: Dodano nowy kupon, którego właścicielem jest **{name}** (przypisany do użytkownika {student.mention})')
                        await self.log(f':inbox_tray: Zarejestrowano nowy kupon, którego właścicielem jest {name + " " + klasa} ({student} `{student.id}`)')
                    else:
                        await ctx.send(':x: **Taki użytkownik nie istnieje!**')
                else:
                    await ctx.send(f':x: **Użyłeś niepoprawnej liczby argumentów**\nPoprawne użycie komendy: `{self.bot.info["prefix"]}nowy_kupon <@użytkownik> <imię> <nazwisko> <klasa>`')

    @commands.command()
    async def kupony(self, ctx):
        if isinstance(ctx.channel, discord.abc.GuildChannel):
            masters = self.bot.get_guild(int(self.bot.info['master_server'])).get_role(int(self.bot.info['master_role'])).members
            if ctx.author in masters and ctx.guild.id == int(self.bot.info['master_server']):
                coupons = sorted((await self.db.fetch('SELECT * FROM polikupon_kupony')), key=lambda i: (i['name'].split(' ')[1]))
                text, payload = '>>> ', []
                for p, coupon in enumerate(coupons):
                    fragment = f'`{p+1}.` **{coupon["name"]} {coupon["class"]}**  - `{coupon["user_id"]}`\n'
                    if len(text + fragment) < 2000:
                        text += fragment
                    else:
                        payload.append(text + fragment)
                        text = '>>> ' + fragment

                if text == '>>> ':
                    await ctx.send(':x: **Nie ma żadnych zarejestrowanych kuponów**')
                    return

                payload.append(text)

                if payload:
                    for chunk in payload:
                        await ctx.send(chunk)

    @commands.command()
    async def usun_kupon(self, ctx, user_id=None):
        if isinstance(ctx.channel, discord.abc.GuildChannel):
            masters = self.bot.get_guild(int(self.bot.info['master_server'])).get_role(int(self.bot.info['master_role'])).members
            if ctx.author in masters and ctx.guild.id == int(self.bot.info['master_server']):
                if user_id is not None:
                    coupon = await self.db.fetchrow('SELECT * FROM polikupon_kupony WHERE user_id = $1', user_id)
                    if coupon:
                        await self.db.execute('DELETE FROM polikupon_kupony WHERE coupon_id = $1', coupon['coupon_id'])
                        await ctx.send(f':white_check_mark: **Pomyślnie usunięto jeden kupon należący do {coupon["name"]} (`{user_id}`)**')
                        await self.log(f':wastebasket: Usunięto kupon należący do **{coupon["name"]}** z klasy **{coupon["class"]}** (`{user_id}`)')
                    else:
                        await ctx.send(f':x: **Użytkownik o ID `{user_id}` nie istnieje lub nie posiada żadnych kuponów**')
                else:
                    await ctx.send(f':x: **Użyłeś niepoprawnej liczby argumentów**\nPoprawne użycie komendy: `{self.bot.info["prefix"]}usun_kupon <ID użytkownika>`')

    @commands.command()
    async def moje_kupony(self, ctx):
        if await activated(self.db, ctx.channel) or isinstance(ctx.channel, discord.abc.PrivateChannel):
            coupons = await self.db.fetch('SELECT * FROM polikupon_kupony WHERE user_id = $1', str(ctx.author.id))
            await ctx.send(f':receipt: **Posiadasz `{len(coupons)}` kupon(y)**')
        else:
            await ctx.send(':x: **Bot nie jest aktywowany na tym serwerze!**')

    @commands.command()
    async def kupon(self, ctx, *, user=None):
        if await activated(self.db, ctx.channel):
            tchrs = self.bot.get_guild(int(self.bot.info['tchr_server'])).members
            student = None
            if ctx.author not in tchrs:
                student = ctx.author

            if student is None and user is not None:
                student = discord.utils.get(ctx.guild.members, mention=user)
                if student is None:
                    student = discord.utils.get(ctx.guild.members, mention=user.replace('!', ''))
                if student is None:
                    student = discord.utils.get(ctx.guild.members, name=user)
                if student is None:
                    try:
                        student = discord.utils.get(ctx.guild.members, id=int(user))
                    except (ValueError, TypeError):
                        pass

            if student in tchrs:
                student = None

            if student is not None:
                kupon = await self.db.fetchrow('SELECT * FROM polikupon_kupony WHERE user_id = $1', str(student.id))
                if kupon:
                    waiting, ready = ':arrows_counterclockwise: Oczekiwanie na zatwierdzenie', ':white_check_mark: Zatwierdzono'
                    text = '**__KUPON__**\n' \
                           f'Właścicielem/ką tego kuponu jest **{kupon["name"]}** z klasy **{kupon["class"]}**.\n' \
                           'Wykorzystanie kuponu wymaga zatwierdzenia przez nauczyciela i ucznia, poprzez wciśnięcie reakcji :white_check_mark: pod tą wiadomością.\n\n' \
                           'Nauczyciel: **{}**\nUczeń: **{}**'

                    embed = discord.Embed(description=text.format(waiting, waiting), color=0xfffffe)
                    embed.set_thumbnail(url='https://i.imgur.com/pFY5I2P.jpg')
                    message = await ctx.send(embed=embed)
                    await message.add_reaction('✅')
                    std_agree, tch_agree = False, False

                    def check(reaction, user):
                        return user in [student] + tchrs and str(reaction.emoji) == '✅' and reaction.message == message and user != ctx.guild.me

                    while not (std_agree and tch_agree):
                        try:
                            reaction, user = await self.bot.wait_for('reaction_add', timeout=90, check=check)
                        except asyncio.TimeoutError:
                            embed = discord.Embed(description=':alarm_clock: **Czas na zatwierdzenie kuponu minął**')
                            await message.edit(embed=embed)
                            await message.remove_reaction('✅', ctx.guild.me)
                            return

                        rct_users = await reaction.users().flatten()
                        rct_users.remove(ctx.guild.me)

                        if student in rct_users:
                            std_agree = True
                        else:
                            std_agree = False

                        for usr in rct_users:
                            if usr in tchrs:
                                tch_agree = True
                                teacher = usr
                                break
                            tch_agree = False

                        if std_agree:
                            std_state = ready
                        else:
                            std_state = waiting

                        if tch_agree:
                            tch_state = ready
                        else:
                            tch_state = waiting

                        embed = discord.Embed(description=text.format(tch_state, std_state), color=0xfffffe)
                        embed.set_thumbnail(url='https://i.imgur.com/pFY5I2P.jpg')
                        await message.edit(embed=embed)

                    await self.db.execute('DELETE FROM polikupon_kupony WHERE coupon_id = $1', kupon['coupon_id'])
                    embed = discord.Embed(description=f'**__:receipt: KUPON WYKORZYSTANY__**\n\nWłaściciel: {student.mention}\nNauczyciel: {teacher.mention}', color=0xfffffe)
                    embed.set_thumbnail(url='https://i.imgur.com/pFY5I2P.jpg')
                    await message.edit(embed=embed)

                    await self.log(f':outbox_tray: Wykorzystano kupon należący do {kupon["name"] + " " + kupon["class"]} (`{student.id}`). Nauczycielem podpisującym był {teacher}')
                else:
                    await ctx.send(f':x: **Uczeń {student.mention} nie posiada żadnego kuponu**')

            else:
                if user is None:
                    await ctx.send(f':x: **Nie podano ucznia, którego kupony mają zostać sprawdzone**\nPoprawne użycie: `{self.bot.info["prefix"]}kupon <@użytkownik>`\nnp. `{self.bot.info["prefix"]}kupon @Jan Kowalski`')
                else:
                    await ctx.send(':x: **Nie ma takiego ucznia**')
        else:
            await ctx.send(':x: **Bot nie jest aktywowany na tym serwerze!**')

