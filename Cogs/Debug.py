from discord.ext.commands import command, check
from Cogs.BaseCog import BaseCog
import os


def is_owner(ctx):
    owner = os.getenv("DISCORD_OWNER_USERID", 0)
    return ctx.author.id == owner


class Debug(BaseCog):
    @command(hidden=True)
    @check(is_owner)
    async def stop(self, ctx):
        if not self.bot.is_closed():
            await self.bot.close()
            if not self.bot.loop.is_closed():
                self.bot.loop.close()
                pass
            pass

        await self.bot.logout()
        pass
    pass
