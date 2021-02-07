from discord.ext import commands
import discord


class Masterserver(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if str(payload.message_id) == self.bot.info['shop_message'] and payload.emoji.name == self.bot.info['shop_emoji'] and payload.user_id != self.bot.user.id and self.bot.shop_is_on:
            guild = self.bot.get_guild(int(self.bot.info['master_server']))
            if str(payload.user_id) not in (chan.name for chan in guild.text_channels):
                false, true = discord.PermissionOverwrite(read_messages=False), discord.PermissionOverwrite(read_messages=True)
                seller_role = guild.get_role(int(self.bot.info['seller_role']))

                channel = await guild.create_text_channel(name=str(payload.user_id), category=guild.get_channel(int(self.bot.info['shop_category'])), overwrites={
                    guild.default_role: false,
                    guild.get_member(payload.user_id): true,
                    seller_role: true
                })

                text = '**Hej!** :wave:\nDzięki za chęć kupienia gazetki!\n' \
                       'Aby dokonać zakupu, **wyślij na tym kanale swoje imię, nazwisko oraz klasę** i zaczekaj aż moderatorzy go zatwierdzą.\n\n' \
                       ':warning: **__Pamiętaj, że decyzja o zakupie jest równoznaczna z akceptacją regulaminu oraz obowiązkiem zapłaty po powrocie do szkoły__**'

                await channel.send(f'{seller_role.mention} {guild.get_member(payload.user_id).mention}', delete_after=1)
                await channel.send(text)
                await channel.send(f'`{payload.user_id}`')

            message = await guild.get_channel(payload.channel_id).fetch_message(self.bot.info['shop_message'])
            await message.remove_reaction(self.bot.info['shop_emoji'], payload.member)

    @commands.command()
    async def archiwizuj(self, ctx, *, name=None):
        if isinstance(ctx.channel, discord.abc.GuildChannel) and isinstance(ctx.channel, discord.TextChannel):
            sellers = self.bot.get_guild(int(self.bot.info['master_server'])).get_role(int(self.bot.info['seller_role'])).members
            if str(ctx.guild.id) == self.bot.info['master_server'] and len(ctx.channel.name) == 18 and ctx.author in sellers:
                await ctx.channel.set_permissions(target=ctx.guild.get_member(int(ctx.channel.name)), overwrite=discord.PermissionOverwrite(read_messages=False))
                await ctx.channel.set_permissions(target=ctx.guild.get_role(int(self.bot.info['seller_role'])), overwrite=discord.PermissionOverwrite(read_messages=False))
                if name is not None:
                    await ctx.channel.edit(name=name, category=ctx.guild.get_channel(int(self.bot.info['shop_archive_category'])))
                else:
                    await ctx.channel.edit(name=ctx.channel.name+'_archived', category=ctx.guild.get_channel(int(self.bot.info['shop_archive_category'])))
                await ctx.message.delete()
                await ctx.send('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n**Transakcja zakończona**')

    @commands.command()
    async def wlacz_sklep(self, ctx):
        if isinstance(ctx.channel, discord.abc.GuildChannel) and isinstance(ctx.channel, discord.TextChannel):
            if str(ctx.guild.id) == self.bot.info['master_server'] and str(ctx.author.id) in self.bot.info['owners']:
                self.bot.shop_is_on = True
                await ctx.send(':white_check_mark: **Sklep włączony**')
                await (await self.bot.get_channel(int(self.bot.info['shop_channel'])).fetch_message(int(self.bot.info['shop_message']))).add_reaction(self.bot.info['shop_emoji'])

    @commands.command()
    async def wylacz_sklep(self, ctx):
        if isinstance(ctx.channel, discord.abc.GuildChannel) and isinstance(ctx.channel, discord.TextChannel):
            if str(ctx.guild.id) == self.bot.info['master_server'] and str(ctx.author.id) in self.bot.info['owners']:
                self.bot.shop_is_on = False
                await ctx.send('**Sklep wyłączony**')
