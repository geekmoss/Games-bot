from discord.ext.commands import command, check, Context
from discord import Guild, Member, Role
from discord.utils import get
from typing import List
from Cogs.BaseCog import BaseCog
import os


def is_owner(ctx):
    owner = int(os.getenv("DISCORD_OWNER_USERID", 0))
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

    @command(hidden=True)
    @check(is_owner)
    async def test(self, ctx):
        print(type(ctx.author.mention), ctx.author.mention)
        pass

    @command(hidden=True)
    @check(is_owner)
    async def fix_illegal_volk(self, ctx: Context):
        """Odebírá Volk roli těm co jí nemají mít."""
        g: Guild = ctx.guild
        VOLK_ROLE = get(g.roles, name="Volkssturm")
        members: List[Member] = g.members
        for i, member in enumerate(members):
            if (i + 1) % 100 == 0:
                print(f"{i + 1} / {len(members)}")
                pass

            roles = [role.name for role in member.roles]
            if set(roles) != {"@everyone", "Volkssturm"} and "Volkssturm" in roles:
                await member.remove_roles(VOLK_ROLE, reason="Fixování stavu")
                print(member.display_name, roles)
                pass
            pass

    @command(hidden=True)
    @check(is_owner)
    async def count_volks(self, ctx: Context):
        """"""
        g: Guild = ctx.guild
        VOLK_ROLE = get(g.roles, name="Volkssturm")
        Hovado_ROLE = get(g.roles, name="Hovado")
        members: List[Member] = g.members

        count = 0
        for i, member in enumerate(members):
            if (i + 1) % 100 == 0:
                print(f"{i + 1} / {len(members)}")
                pass

            roles = [role.name for role in member.roles]
            if "Volkssturm" in set(roles) and "Hovado" in set(roles):
                await member.remove_roles(Hovado_ROLE, reason="Fixování stavu")
                count += 1
                pass
            pass
        await ctx.send(f"Count: {count}")
    pass
