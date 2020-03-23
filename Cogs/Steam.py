from discord.ext.commands import command, check, Context
from discord import Colour, Embed
from Cogs.BaseCog import BaseCog
from Misc.SteamMatch import SteamMatch, SteamMatchException


class Steam(BaseCog):
    @command(aliases=('sm',))
    async def steamMatch(self, ctx: Context, *users):
        """Hledá shody ve knihovnách zmíněných hráčů."""
        try:
            await ctx.trigger_typing()
            sm = SteamMatch(*users)
            data = sm.compare()

            libs = ', '.join(map(lambda x: f'**{x}** *({data["users"][x]} games)*', data['users']))

            def build_item(game):
                pt = sum(game["info"]["u"].values())
                is_mins = pt < 60
                t = pt if is_mins else pt / 60
                return f'- **[{game["info"]["name"]}]({game["url"]})**, *playtime of everyone ' \
                       f'`{t:.1f} {"min" if is_mins else "hour"}{"" if t < 2.0 else "s"}`*;'
                pass

            body = "" + \
                   f"There are {len(data['games'])} matches from {libs} players libraries.\n\n" + \
                   '\n'.join(map(build_item, data['games']))

            if len(body) > 2048:
                buff = ""
                msgs = []
                for l in body.splitlines():
                    if len(buff + l + "\n") <= 2048:
                        buff += l + "\n"
                        pass
                    else:
                        msgs.append(buff)
                        buff = l + "\n"
                        pass
                    pass

                if buff:
                    msgs.append(buff)

                for i, n in enumerate(msgs):
                    await ctx.send(embed=Embed(
                        title=f"Steam Matcher Result - Part {i + 1}",
                        color=Colour.from_rgb(66, 244, 125),
                        description=n
                    ))
                pass
            else:
                await ctx.send(embed=Embed(
                    title="Steam Matcher Result",
                    color=Colour.from_rgb(66, 244, 125),
                    description=body
                ))
                pass
            pass
        except SteamMatchException as e:
            await self.generic_error(ctx, e.args[0])
        pass
    pass
