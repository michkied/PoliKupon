from discord.ext import commands
from datetime import datetime
import discord


class Coupons(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @commands.command()
    async def nowy_kupon(self, ctx, user=None, first_name=None, last_name=None, klasa=None):
        masters = self.bot.get_guild(int(self.bot.info['master_server'])).get_role(int(self.bot.info['master_role'])).members
        if ctx.author in masters:
            if None not in (user, first_name, last_name, klasa):
                student = discord.utils.get(ctx.guild.members, mention=user.replace('!', ''))
                if student is None:
                    student = discord.utils.get(ctx.guild.members, name=user)
                if student is None:
                    try:
                        student = discord.utils.get(ctx.guild.members, id=int(user))
                    except (ValueError, TypeError):
                        pass

                if student is not None:
                    name = first_name+' '+last_name
                    log = self.bot.get_channel(int(self.bot.info['log_channel']))
                    await self.db.execute('INSERT INTO polikupon_kupony(user_id, name, class) VALUES($1, $2, $3)', str(student.id), name, klasa)
                    await ctx.send(f':white_check_mark: Dodano nowy kupon, którego właścicielem jest **{name}** (przypisany do użytkownika {student.mention})')
                    await log.send(f'`{datetime.now().strftime("%d.%m.%Y  %H:%M:%S")}` :inbox_tray: Zarejestrowano nowy kupon, którego właścicielem jest {name+" "+klasa} ({student} `{student.id}`)')
                else:
                    await ctx.send(':x: **Taki użytkownik nie istnieje!**')
            else:
                await ctx.send(f':x: **Użyłeś niepoprawnej liczby argumentów**\nPoprawne użycie komendy: `{self.bot.info["prefix"]}nowy_kupon <@użytkownik> <imię> <nazwisko> <klasa>`')

