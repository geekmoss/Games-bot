from discord.ext.commands import Bot, Cog, command, Context
from discord import Embed, Colour, File
from Cogs.BaseCog import BaseCog
from Misc import Covid
from requests import get


class Covid19(BaseCog):
    def __api_call(self) -> dict:
        r = get("https://api.apify.com/v2/key-value-stores/K373S4uCFR9W1K8ei/records/LATEST?disableRedirect=true")
        if r.status_code != 200:
            return None

        return r.json()

    @command()
    async def corona(self, ctx: Context):
        """Aktuální situace v ČR."""

        await ctx.trigger_typing()

        d = self.__api_call()
        if not d:
            await self.generic_error(ctx, "Něco se nepovedlo. Nejsou dostupná data.")
            return

        await ctx.send(embed=Embed(
            title="COVID-19: Aktuální situace v ČR",
            color=Colour.dark_green(),
            description=f"**Počet nakažených:** `{d.get('infected', '???')}`\n"
                        f"**Počet testovaných:** `{d.get('totalTested', '???')}`\n"
                        f"*Aktualizováno {d.get('lastUpdatedAtSource', '???')}*"
        ))
        pass

    @command()
    async def corona_timeline(self, ctx: Context):
        """Vývoj počtu infikovaných v ČR."""

        await ctx.trigger_typing()
        d = self.__api_call()

        if not d:
            await self.generic_error(ctx, "Něco se nepovedlo. Nejsou dostupná data.")
            return

        await ctx.send(file=File(Covid.infected(d), "corona_cr_timeline.png"))
        pass

    @command()
    async def corona_timeline_log(self, ctx: Context):
        """Vývoj počtu infikovaných v ČR na logaritmické škále."""

        await ctx.trigger_typing()
        d = self.__api_call()

        if not d:
            await self.generic_error(ctx, "Něco se nepovedlo. Nejsou dostupná data.")
            return

        await ctx.send(file=File(Covid.infected_log(d), "corona_cr_timeline_yaxis_log.png"))
        pass
    pass
