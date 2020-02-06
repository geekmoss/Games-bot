import os


def is_debug_mode(ctx):
    owner = int(os.getenv("DISCORD_OWNER_USERID", False))
    debug = os.getenv("DEBUG", False)
    if debug:
        return ctx.author.id == owner
    else:
        return True
    pass
