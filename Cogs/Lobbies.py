from discord.ext.commands import Bot, Cog, command, Context
from Cogs.BaseCog import BaseCog
from db import Lobby, LobbyList
from typing import Union
import discord


class Lobbies(BaseCog):
    @command(name="list", aliases=("l",))
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
    async def join(self, ctx: Context, lobby: str):
        """Připojíte se k vybranému lobby.

        $join NAME

        $join NašeSuperLobby"""
        l = Lobby.get_or_none((Lobby.name == lobby) & (Lobby.server == ctx.guild.id))

        if not l:
            await self.generic_error(ctx, "Lobby nebylo nalezeno, zkontrolujte příkaz a jeho argumenty.")
            return

        p = LobbyList.get_or_none(LobbyList.user == ctx.author.mention)
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
    async def create(self, ctx: Context, name: str, subject: str):
        """Vytváří nové lobby.

        $create NAME SUBJECT

        $create NašeSuperLobby \"Naše skupina se věnuje hraní XYZ\""""

        name = name.replace(" ", "_")

        l: Lobby = Lobby.create(name=name, subject=subject, author=ctx.author.display_name,
                                author_mention=ctx.author.mention, server=ctx.guild.id)

        LobbyList.create(lobby=l.id, user=ctx.author.display_name, user_mention=ctx.author.mention)
        await ctx.send(embed=discord.Embed(
            title="Info",
            color=discord.Colour.green(),
            description=f"Lobby {l.name} bylo úspěšně založeno. GL&HF!"
        ))
        pass

    @command()
    async def delete(self, ctx: Context, lobby: str):
        """Maže vybrané lobby.

        $delete NAME

        $delete NašeSuperLobby"""
        l: Lobby = Lobby.get_or_none((Lobby.name == lobby) & (Lobby.server == ctx.guild.id))
        if not l:
            await self.generic_error(ctx, "Lobby nebylo nalezeno.")
            return

        if l.author_mention != ctx.author.mention:
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
    async def lobby(self, ctx: Context, lobby: str):
        """Zobrazí detail vybraného lobby.

        $lobby NAME

        $lobby NašeSuperLobby"""

        l: Lobby = Lobby.get_or_none((Lobby.name == lobby) & (Lobby.server == ctx.guild.id))

        if not l:
            await self.generic_error(ctx, "Lobby nebylo nalezeno.")
            return

        users = list(LobbyList.select().where(LobbyList.lobby == l.id).execute())
        users_desc = "\n".join(map(lambda x: f"- {x.user}, připojil se{x.joined:%Y-%m-%d %H:%M}", users))

        await ctx.send(embed=discord.Embed(
            title=l.name,
            color=discord.Colour.green(),
            description=f"**Popis**: {l.subject}\n\n"
                        f"**Vlasntík**: {l.author}\n"
                        f"**Založeno**: {l.created:%Y-%m-%d %H:%M}\n\n\n"
                        f"**Členové** ({len(users)}): \n{users_desc}"
        ))
        return
    pass
