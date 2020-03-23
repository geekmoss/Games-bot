from discord.ext.commands import Bot, Cog, command, Context
from discord import Embed, Colour, File
from Cogs.BaseCog import BaseCog
from Misc import Covid
from requests import get
from datetime import datetime


class Covid19(BaseCog):
    @staticmethod
    def __api_call() -> dict:
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
            description=f"**Nakažených:** `{d.get('infected', '???')}`\n"
                        f"**Testovaných:** `{d.get('totalTested', '???')}`\n"
                        f"**Uzdravených:** `{d.get('recovered', '???')}`\n"
                        f"**Zemřelých:** `{d.get('deceased', '???')}`\n"
                        f"*Aktualizováno {d.get('lastUpdatedAtSource', '???')}*"
        ))
        pass

    @command()
    async def corona_timeline(self, ctx: Context):
        """Vývoj počtu infikovaných v ČR. Včetně vyjádření přírůstku a logaritmické škály."""

        await ctx.trigger_typing()
        d = self.__api_call()

        if not d:
            await self.generic_error(ctx, "Něco se nepovedlo. Nejsou dostupná data.")
            return

        await ctx.send(file=File(Covid.infected(d), "corona_cze_timeline.png"))
        pass

    @command()
    async def corona_regions(self, ctx: Context):
        """Počet nakažených dle krajů"""

        await ctx.trigger_typing()
        d = self.__api_call()

        if not d:
            await self.generic_error(ctx, "Něco se nepovedlo. Nejsou dostupná data.")
            return

        await ctx.send(file=File(Covid.by_region(d), "corona_cze_by_region.png"))
        pass

    @command()
    async def corona_quarantine_by_regions(self, ctx: Context):
        """Počet karantén dle krajů"""

        await ctx.trigger_typing()
        d = self.__api_call()

        if not d or len(d['regionQuarantine']) == 0:
            await self.generic_error(ctx, "Něco se nepovedlo. Nejsou dostupná data.")
            return

        await ctx.send(file=File(Covid.quarantine_by_regions(d), "corona_cze_quarantine_by_region.png"),
                       content=f"Údaj k {d['regionQuarantine'][-1]['reportDate']}")
        pass

    @command()
    async def corona_demography(self, ctx: Context):
        """Nakažení podle demografie"""

        await ctx.trigger_typing()
        d = self.__api_call()

        if not d:
            await self.generic_error(ctx, "Něco se nepovedlo. Nejsou dostupná data.")
            return

        await ctx.send(file=File(Covid.demography(d), "corona_cze_demography.png"))
        pass

    @command()
    async def corona_models(self, ctx: Context, peak_day: int = 0, detailed: bool = False):
        """ Predikce na základě logistické, možnost specifickovat den kdy bude nejvyšší peak. (Kolikátý den od 1. 1. 2020)

         Vytvořeno na základě: https://github.com/creative-connections/Bodylight-notebooks/blob/master/Covid-19/Covid-19InItalyAndCzechia.ipynb"""

        await ctx.trigger_typing()
        d = self.__api_call()
        if not d:
            await self.generic_error(ctx, "Něco se nepovedlo. Nejsou dostupná data.")
            return

        if detailed:
            f, d = Covid.prediction(d, peak_day)
            days = (d['last_date'] - datetime(2020, 1, 1)).days
            await ctx.send(file=File(f, "corona_cze_predictions_model.png)"), embed=Embed(
                title="Details",
                description=f"**Predicted last day:** __{d['last_date'].strftime('%d. %m. %Y')}__ *({days}. day)*\n\n"
                            f"**Optimistic model:** {d['log_model_a']}\n" +
                            (f"**Realistic model:** {d['log_model_b']}\n" if peak_day else '\n') +
                            f"\n\n"
                            f"Logistic Regression: `f(x, a, b, c) = c / 1+e ^ (-(x - b) / a)`\n"
                            f"- *x*: time\n"
                            f"- *a*: speed of infection\n"
                            f"- *b*: critical point, day when most infected people was recorded\n"
                            f"- *c*: total number of infected people",
                color=Colour.dark_green()
            ))
        else:
            await ctx.send(file=File(Covid.prediction(d, peak_day)[0], "corona_cze_predictions_model.png)"))
            pass
        pass
    pass
