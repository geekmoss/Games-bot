from discord.ext.commands import Bot, Cog, command, Context, check
from misc import is_debug_mode
from Cogs.BaseCog import BaseCog
from db import Lobby, LobbyList
from typing import Union
import peewee
import discord


class Lobbies(BaseCog):
    @command(name="list", aliases=("l",))
    @check(is_debug_mode)
    async def lst(self, ctx: Context):
        """Vypíše seznam lobby.

        $list"""

        lobbies = Lobby.select().where(Lobby.server == ctx.guild.id).execute()

        buffer = ""

        for lobby in lobbies:
            buffer += f"**`{lobby.name}`**: {lobby.subject}\n"
            pass

        await ctx.send(embed=discord.Embed(
            title="List of lobbies",
            color=discord.Colour.from_rgb(50, 50, 200),
            description=buffer if len(buffer) else "Aktuálně nejsou žádná lobby vytvořená."
        ))
        pass

    @command(name="join", aliases=("j",))
    @check(is_debug_mode)
    async def join(self, ctx: Context, lobby: str):
        """Připojíte se k vybranému lobby.

        $join NAME

        $join NašeSuperLobby"""
        l = Lobby.get_or_none((Lobby.name == lobby) & (Lobby.server == ctx.guild.id))

        if not l:
            await self.generic_error(ctx, "Lobby nebylo nalezeno, zkontrolujte příkaz a jeho argumenty.")
            return

        p = LobbyList.get_or_none((LobbyList.user_mention == ctx.author.mention) & (LobbyList.lobby == l.id))
        if p:
            await ctx.send(embed=discord.Embed(
                title="Info",
                color=discord.Colour.from_rgb(100, 200, 100),
                description="Již jste v tomto lobby připojeni."
            ))
            return

        LobbyList.create(lobby=l.id, user=ctx.author.display_name, user_mention=ctx.author.mention)
        await ctx.send(embed=discord.Embed(
            title="Info",
            color=discord.Colour.green(),
            description=f"Vítejte v {l.name}!"
        ))
        pass

    @command()
    @check(is_debug_mode)
    async def leave(self, ctx: Context, lobby: str):
        """Příkaz pro opuštění lobby.

        $leave NAME

        $leave NašeSuperLobby"""
        l: Lobby = Lobby.get_or_none((Lobby.name == lobby) & (Lobby.server == ctx.guild.id))

        if not l:
            await self.generic_error(ctx, "Lobby nebylo nalezeno.")
            return

        if l.author_mention == ctx.author.mention:
            await self.generic_error(ctx, f"Jelikož jste lobby založili, nemůžete ho opustit. "
                                          f"Použijte příkaz pro smazání.\n`$delete \"{l.name}\"`")
            return

        ll: LobbyList = LobbyList.get_or_none((LobbyList.lobby == l.id) & (LobbyList.user_mention == ctx.author.mention))
        if ll:
            ll.delete_instance()
            await ctx.send(embed=discord.Embed(
                title="Info",
                colour=discord.Colour.green(),
                description="Opustili jste lobby."
            ))
            return
        else:
            await self.generic_error(ctx, "Daného lobby jste nebyli členy, zkontrolujte příkaz.")
            return
        pass

    @command()
    @check(is_debug_mode)
    async def create(self, ctx: Context, name: str, subject: str):
        """Vytváří nové lobby.

        $create NAME SUBJECT

        $create NašeSuperLobby \"Naše skupina se věnuje hraní XYZ\""""

        name = name.replace(" ", "_")

        try:
            l: Lobby = Lobby.create(name=name, subject=subject, author=ctx.author.display_name,
                                    author_mention=ctx.author.mention, server=ctx.guild.id)
        except peewee.IntegrityError as e:
            if e.args[0] == "UNIQUE constraint failed: lobby.name, lobby.server":
                await self.generic_error(ctx, "Vybraný název již existuje, zvolte prosím jiný.")
                return

            raise

        LobbyList.create(lobby=l.id, user=ctx.author.display_name, user_mention=ctx.author.mention)
        await ctx.send(embed=discord.Embed(
            title="Info",
            color=discord.Colour.green(),
            description=f"Lobby {l.name} bylo úspěšně založeno. GL&HF!"
        ))
        pass

    @command()
    @check(is_debug_mode)
    async def delete(self, ctx: Context, lobby: str):
        """Maže vybrané lobby.

        $delete NAME

        $delete NašeSuperLobby"""
        l: Lobby = Lobby.get_or_none((Lobby.name == lobby) & (Lobby.server == ctx.guild.id))
        if not l:
            await self.generic_error(ctx, "Lobby nebylo nalezeno.")
            return

        if l.author_mention != ctx.author.mention and ctx.author.id != self.owner:
            await self.generic_error(ctx, "Lobby může smazat pouze vlastník.")
            return

        l.delete_instance(recursive=True)
        await ctx.send(embed=discord.Embed(
            title="Info",
            color=discord.Colour.green(),
            description="Lobby bylo úspěšně smazáno."
        ))
        pass

    @command(aliases=("m",))
    @check(is_debug_mode)
    async def mention(self, ctx: Context, lobby: str, msg: str = None):
        """Označí a svolá všechny, kteří jsou členy vybraného lobby.

        $mention NAME
        $mention NAME MESSAGE

        $mention NašeSuperLobby
        $mention NašeSuperLobby \"Dnes hra od 20:00.\""""
        l: Lobby = Lobby.get_or_none((Lobby.name == lobby) & (Lobby.server == ctx.guild.id))
        if not l:
            await self.generic_error(ctx, "Lobby nebylo nalezeno.")
            return

        content_msg = "Hey, wake up! \n" if not msg else msg + "\n"
        mentions = []

        for row in LobbyList.select().where(LobbyList.lobby == l.id).execute():
            mentions.append(row.user_mention)
            pass

        content = content_msg + " • ".join(mentions)
        if len(content) > 2000:
            content = content_msg
            for item in mentions:
                if content == "":
                    content = item
                    continue

                if len(content + " • " + item) < 2000:
                    content += " • " + item
                    pass
                else:
                    await ctx.send(content)
                    content = ""
                    pass
                pass
            pass
        else:
            await ctx.send(content)
            pass
        pass

    @command()
    @check(is_debug_mode)
    async def lobby(self, ctx: Context, lobby: str):
        """Zobrazí detail vybraného lobby.

        $lobby NAME

        $lobby NašeSuperLobby"""

        l: Lobby = Lobby.get_or_none((Lobby.name == lobby) & (Lobby.server == ctx.guild.id))

        if not l:
            await self.generic_error(ctx, "Lobby nebylo nalezeno.")
            return

        users = list(LobbyList.select().where(LobbyList.lobby == l.id).execute())
        users_desc = "\n".join(map(lambda x: f"- {x.user}, připojil se {x.joined:%Y-%m-%d %H:%M}", users))

        await ctx.send(embed=discord.Embed(
            title=l.name,
            color=discord.Colour.green(),
            description=f"**Popis**: {l.subject}\n\n"
                        f"**Vlasntík**: {l.author}\n"
                        f"**Založeno**: {l.created:%Y-%m-%d %H:%M}\n\n\n"
                        f"**Členové** ({len(users)}): \n{users_desc}"
        ))
        return

    @command()
    @check(is_debug_mode)
    async def update(self, ctx: Context, lobby: str, key: str, value: str):
        """Provede úpravu existujícího lobby. Umožňuje změnit jméno (name) či její předmět (subject).

        $update NAME KEY VALUE

        $update NašeSuperLobby name JeštěSuprovějšíLobby
        $update NašeSuperLobby subject \"Nový popis našeho suprového lobby.\""""

        l: Lobby = Lobby.get_or_none((Lobby.name == lobby) & (Lobby.server == ctx.guild.id))

        if not l:
            await self.generic_error(ctx, "Lobby nebylo nalezeno.")
            return

        if l.author_mention != ctx.author.mention and ctx.author.id != self.owner:
            await self.generic_error(ctx, "Lobby může upravit pouze vlastník.")
            return

        if key.lower() == "name":
            l.name = value

            try:
                l.save()
            except peewee.IntegrityError as e:
                if e.args[0] == "UNIQUE constraint failed: lobby.name, lobby.server":
                    await self.generic_error(ctx, "Vybraný název již existuje, zvolte prosím jiný.")
                    return
                raise

            pass
        elif key.lower() == "subject":
            l.subject = value
            l.save()
            pass

        pass

    @command()
    @check(is_debug_mode)
    async def ownership(self, ctx: Context, lobby: str, user: discord.User):
        """Předá vlastnictví zadanému uživateli.

        $ownership NAME @USER

        $ownership NašeSuperLobby @Franta"""

        l: Lobby = Lobby.get_or_none((Lobby.name == lobby) & (Lobby.server == ctx.guild.id))

        if not l:
            await self.generic_error(ctx, "Lobby nebylo nalezeno.")
            return

        if l.author_mention != ctx.author.mention and ctx.author.id != self.owner:
            await self.generic_error(ctx, "Lobby může předat pouze vlastník.")
            return

        l.author = user.display_name
        l.author_mention = user.mention
        l.save()

        await ctx.send(embed=discord.Embed(
            title="Info",
            color=discord.Colour.green(),
            description="Vlastnictví lobby předáno."
        ))
        pass
    pass
