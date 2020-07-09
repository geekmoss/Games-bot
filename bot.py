from discord.ext import commands
from discord import Embed, Colour
from dotenv import load_dotenv
from Cogs import *
from db import check_db
import signal
import os

load_dotenv()

is_debug = os.getenv("DEBUG", False)
token = os.getenv("DISCORD_TOKEN") if not is_debug else is_debug

owner = int(os.getenv("DISCORD_OWNER_USERID"))

bot = commands.Bot(command_prefix="$" if not is_debug else "d$")


def stop():
    bot.loop.close()
    bot.logout()
    pass


async def command_error(self, ctx: commands.Context, error):
    if self.error_log:
        print(error)

    if isinstance(error, commands.MissingRequiredArgument):
        await self.send_cmd_help(ctx)
    pass


@bot.event
async def on_ready():
    print("I'm ready!")
    pass


@bot.event
async def on_command_error(context: commands.Context, exception):
    print(f"{context.command}:", exception)

    if isinstance(exception, commands.MissingRequiredArgument):
        await context.send(embed=Embed(
            title="Error",
            color=Colour.red(),
            description=f"Příkaz není napsaný správně, prosím zkontrolujte ho.\n\n"
                        f"```\n{context.command.help}\n```"
        ))
        pass
    pass


bot.loop.add_signal_handler(signal.SIGINT, stop)
bot.loop.add_signal_handler(signal.SIGTERM, stop)

bot.add_cog(Debug(bot, owner))
bot.add_cog(Lobbies(bot, owner))
bot.add_cog(Steam(bot, owner))

check_db()
bot.run(token)


