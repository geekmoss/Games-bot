from discord.ext.commands import command, Context
from discord import Guild, Member, Role
from discord.utils import get
from typing import List
from Cogs.BaseCog import BaseCog
import os


class Config(BaseCog):
    @command(hidden=True)
    async def stop(self, ctx):
        if not self.bot.is_closed():
            await self.bot.close()
            if not self.bot.loop.is_closed():
                self.bot.loop.close()
                pass
            pass

        await self.bot.logout()
        pass
