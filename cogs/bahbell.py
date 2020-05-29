from discord.ext import commands
from .core import converter as conv
from typing import Optional
from math import log10

import discord
import colors

def male_bfp(height, neck, waist):
    denom = 1.0324 - 0.19077 * log10(waist-neck) + 0.15456 * log10(height)
    return 495 / denom - 450

def female_bfp(height, neck, waist, hip):
    denom = 1.29579 - 0.35004 * log10(waist+hip-neck) + 0.22100 * log10(height)
    return 495 / denom - 450

class Bahbell(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=['bfp'])
    async def bodyfat(self, context, gender:conv.Gender, height:float, neck:float, waist:float, hip:Optional[float]):
        if gender == conv.MALE:
            bfp = male_bfp(height, neck, waist)
        elif gender == conv.FEMALE:
            if not hip:
                raise commands.BadArgument('Missing `hip` measurement for girls!')
            bfp = female_bfp(height, neck, waist, hip)
        
        embed = colors.embed(description=f'Your body fat percentage is `{bfp:.2f}%`') \
                .add_field(name='Height', value=f'{height:0.0f}cm') \
                .add_field(name='Neck', value=f'{neck:0.0f}cm') \
                .add_field(name='Waist', value=f'{waist:0.0f}cm')
        if hip:
            embed.add_field(name='Hip', value=f'{hip:0.0f}cm')

        await context.send(embed=embed)

def setup(bot):
    bot.add_cog(Bahbell(bot))