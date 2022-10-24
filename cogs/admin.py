import discord
from discord.ext import commands
from discord.ext.commands import Greedy
import typing
import config

from typing import Optional, Literal

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`

    @commands.hybrid_command()
    @commands.is_owner()
    async def sync(
    self, ctx, guilds = None, spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        if not guilds:
            if spec == "~":
                synced = await self.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                self.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await self.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                self.bot.tree.clear_commands(guild=ctx.guild)
                await self.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await self.bot.tree.sync()

            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await self.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

    @commands.hybrid_command(pass_context=True, hidden=True, name='eval')
    @commands.is_owner()
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if not (ret):
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')


    @commands.hybrid_command(pass_context=True, hidden=True, name='reload')
    @commands.is_owner()
    async def reload(self, ctx, extension = None):
    
        if extension is None:
            v,e = 0, 0
            for ext in config.initial_extensions:
                try:
                    await self.bot.reload_extension(f"{ext}")
                    print(f"Reloaded extension: {ext}")            
                    v+=1
                except commands.ExtensionError:
                    print(f"Couldn't reload extension: {ext}")
                    e+=1

            if ctx.interaction:
                await ctx.interaction.response.send_message(f"Reloaded {v} extensions, {e} fail.", ephemeral=True)
                return
            
            await ctx.message.add_reaction('\u2705')
            await ctx.send(f"Reloaded {v} extensions, {e} fail.")
            return
        
        try:
            await self.bot.reload_extension(f"cogs.{extension}")
        
        except commands.ExtensionError as e:
            print(f"Couldn't reload extension: {extension}\nError: {e}")

        else:
            print(f"Reloaded extension: {extension}")
            
            if ctx.interaction:
                await ctx.interaction.response.send_message(f"Reloaded `{extension}`", ephemeral=True)
                return

            await ctx.message.add_reaction('\u2705')


async def setup(bot):
    await bot.add_cog(Admin(bot))
