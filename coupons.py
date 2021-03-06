from discord.ext import commands
from datetime import datetime
import discord
import asyncio
import random


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
        self.running = []

    async def log(self, message):
        await self.bot.get_channel(int(self.bot.info['log_channel'])).send(f'`{datetime.now().strftime("%d.%m.%Y  %H:%M:%S")}` {message}')

    @commands.command()
    async def nowy_kupon(self, ctx, user=None, first_name=None, last_name=None, klasa=None):
        if isinstance(ctx.channel, discord.abc.GuildChannel):
            sellers = self.bot.get_guild(int(self.bot.info['master_server'])).get_role(int(self.bot.info['seller_role'])).members
            if ctx.author in sellers and ctx.guild.id == int(self.bot.info['master_server']):
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
                        await ctx.send(f':white_check_mark: Dodano nowy kupon, którego właścicielem jest **{name} {klasa}** (przypisany do użytkownika {student.mention})')
                        await self.log(f':inbox_tray: Zarejestrowano nowy kupon, którego właścicielem jest {name + " " + klasa} ({student} `{student.id}`)')
                    else:
                        await ctx.send(':x: **Taki użytkownik nie istnieje!**')
                else:
                    await ctx.send(f':x: **Użyto niepoprawnej liczby argumentów**\nPoprawne użycie komendy: `{self.bot.info["prefix"]}nowy_kupon <@użytkownik> <imię> <nazwisko> <klasa>`')

    @commands.command()
    async def kupony(self, ctx):
        if isinstance(ctx.channel, discord.abc.GuildChannel):
            sellers = self.bot.get_guild(int(self.bot.info['master_server'])).get_role(int(self.bot.info['seller_role'])).members
            if ctx.author in sellers and ctx.guild.id == int(self.bot.info['master_server']):
                coupons = sorted((await self.db.fetch('SELECT * FROM polikupon_kupony')), key=lambda i: (i['class']))
                text, payload = '>>> ', []
                for p, coupon in enumerate(coupons):
                    fragment = f'`{p+1}.` **{coupon["class"]} {coupon["name"]}**  - `{coupon["user_id"]}`\n'
                    if len(text + fragment) < 2000:
                        text += fragment
                    else:
                        payload.append(text)
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
            seller = self.bot.get_guild(int(self.bot.info['master_server'])).get_role(int(self.bot.info['seller_role'])).members
            if ctx.author in seller and ctx.guild.id == int(self.bot.info['master_server']):
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

            def check(m):
                return 'dzieki' in m.content.lower().replace('ę', 'e') and m.author == ctx.author and m.channel == ctx.channel
            try:
                await self.bot.wait_for('message', timeout=15, check=check)
                await ctx.send(random.choice(['luz', 'spoko', 'nie ma sprawy', 'do usług', 'łatwo', 'glhf', 'chill', ':sunglasses:', ':pleading_face:', ':+1:']))
            except asyncio.TimeoutError:
                pass
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
                coupon = await self.db.fetchrow('SELECT * FROM polikupon_kupony WHERE user_id = $1', str(student.id))

                if student.id in self.running:
                    await ctx.send(':x: **Proces został już rozpoczęty w innym miejscu**')
                    return

                if coupon:
                    self.running.append(student.id)
                    waiting, ready = ':arrows_counterclockwise: Oczekiwanie na zatwierdzenie', ':white_check_mark: Zatwierdzono'
                    text = '**__KUPON__**\n' \
                           f'Właścicielem/ką tego kuponu jest **{coupon["name"]}** z klasy **{coupon["class"]}**.\n' \
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
                            self.running.remove(student.id)
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

                        if not (std_agree and tch_agree):
                            embed = discord.Embed(description=text.format(tch_state, std_state), color=0xfffffe)
                            embed.set_thumbnail(url='https://i.imgur.com/pFY5I2P.jpg')
                            await message.edit(embed=embed)

                    await self.db.execute('DELETE FROM polikupon_kupony WHERE coupon_id = $1', coupon['coupon_id'])
                    self.running.remove(student.id)
                    embed = discord.Embed(description=f'**__:receipt: KUPON WYKORZYSTANY__**\n\nWłaściciel: {student.mention}\nNauczyciel: {teacher.mention}', color=0xfffffe)
                    embed.set_thumbnail(url='https://i.imgur.com/pFY5I2P.jpg')
                    await message.edit(embed=embed)

                    await self.log(f':outbox_tray: Wykorzystano kupon należący do {coupon["name"] + " " + coupon["class"]} (`{student.id}`). Nauczycielem podpisującym był {teacher}')
                else:
                    await ctx.send(f':x: **Uczeń {student.mention} nie posiada żadnego kuponu**')

            else:
                if user is None:
                    await ctx.send(f':x: **Nie podano ucznia, którego kupony mają zostać sprawdzone**\nPoprawne użycie: `{self.bot.info["prefix"]}kupon <@użytkownik>`\nnp. `{self.bot.info["prefix"]}kupon @Jan Kowalski`')
                else:
                    await ctx.send(':x: **Nie ma takiego ucznia**')
        else:
            await ctx.send(':x: **Bot nie jest aktywowany na tym serwerze!**')

