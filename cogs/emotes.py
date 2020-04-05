import discord
import typing
import re
import aiohttp
import colors
import math
import random
import cogs
import env

from .core import converter as conv
from discord.ext import commands

EMOTES_PER_PAGE = 25
EMOJI_PATTERN = '(:[^:\s]+:)(?!\d)'
INTERROBANG = '⁉️'
HOME_GUILD = 596171359747440657

EMBED_BACKCOLOR = 0x2f3136

TWEMOJI_CDN = 'https://twemoji.maxcdn.com/v/latest/72x72/%x.png'

class Emotes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['big'])
    async def enlarge(self, context, emoji:conv.NitroEmoji):
        embed = discord.Embed(color=EMBED_BACKCOLOR)
        url = None
        if type(emoji) in [discord.Emoji, discord.PartialEmoji]:
            url = emoji.url
        elif len(emoji) == 1:
            url = TWEMOJI_CDN % ord(emoji)
        
        if url:
            embed.set_image(url=url)
            await context.send(embed=embed)
        else:
            React = self.bot.get_cog(cogs.REACT)
            await React.add_reaction(context.message, ':interrobang:')

    @commands.command(aliases=['emojis'])
    async def emotes(self, context, page:int=1):
        home_guild = self.bot.get_guild(HOME_GUILD)
        embed = colors.embed()
        embed.set_author(name='Available Emotes')
        total_page = math.ceil(len(home_guild.emojis) / EMOTES_PER_PAGE)
        embed.set_footer(text=f'Page {page}/{total_page}')
        
        all_emojis = sorted(home_guild.emojis, key=lambda e: e.name)
        emojis = []
        start = EMOTES_PER_PAGE * (page - 1)
        end = EMOTES_PER_PAGE * page
        page_emojis = all_emojis[start:end]
        for e in page_emojis:
            emojis += [f'{e} `:{e.name}:`']
        embed.description = '\n'.join(emojis)
        await context.send(embed=embed)
    
    @commands.command()
    @commands.guild_only()
    async def drop(self, context, emoji:conv.NitroEmoji, author:typing.Optional[conv.Member], i:int=1):
        counter = 1
        async for message in context.history(limit=None, before=context.message):
            if author and message.author != author:
                continue
                
            if counter < i:
                counter += 1
                continue
            break
        
        await message.add_reaction(emoji)
        
    @commands.Cog.listener()
    async def on_message(self, msg):
        if env.TESTING or msg.author == self.bot.user: return
        context = await self.bot.get_context(msg)
        if context.command:
            return
        await self.reply_emotes(msg)
    
    def get_emoji(self, name):
        return discord.utils.get(self.bot.emojis, name=name)

    async def reply_emotes(self, msg):
        match = re.findall(EMOJI_PATTERN, msg.content)
        emojis = []

        for emoji in match:
            emoji = self.get_emoji(emoji.replace(':', ''))
            if emoji:
                emojis += [str(emoji)]
        
        if emojis:
            emojis = ' '.join(emojis)
            await msg.channel.send(emojis)
    
    @commands.command(hidden=True)
    @commands.is_owner()
    async def addemote(self, context, url, name=None):
        response = INTERROBANG
        
        async with context.typing():
            image = await download_image(url)
            if image:
                if not name:
                    name = 'emote%04d' % random.randint(0, 9999)
                await context.guild.create_custom_emoji(name=name, image=image)
                response = self.get_emoji(name)
            await context.message.add_reaction(response)
    
    @commands.command(hidden=True)
    @commands.is_owner()
    async def stealemote(self, context, channel:typing.Optional[discord.TextChannel], msg_id:int, name=None):
        channel = channel or context.channel
        response = INTERROBANG
        try:
            await context.trigger_typing()
            msg = await channel.fetch_message(msg_id)
            emote = await get_emote_from_msg(context, msg)
            name = name or emote.name
            image = await emote.url.read()
            await self.bot.get_guild(HOME_GUILD).create_custom_emoji(name=name, image=image)
            response = self.get_emoji(name)
        except:
            import traceback; traceback.print_exc()
        await context.message.add_reaction(response)
    
    @commands.command(hidden=True)
    async def emourl(self, context, channel:typing.Optional[discord.TextChannel], msg_id:int):
        msg = (channel or context.channel).fetch_message(msg_id)
        e = await get_emote_from_msg(context, msg)
        await context.send(e.url)
    
async def get_emote_from_msg(context, msg):
    return await commands.PartialEmojiConverter().convert(context, msg.content)

async def download_image(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            if r.status == 200:
                return await r.read()

def setup(bot):
    bot.add_cog(Emotes(bot))