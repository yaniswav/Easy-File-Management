import discord
from discord.ext import commands

class Confirm(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):

        v = Ah()
        await interaction.response.send_message('alors', ephemeral=True, view=v)

        self.value = True
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Cancelling', ephemeral=True)
        self.value = False
        self.stop()


class Ah(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label='CC', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('c', ephemeral=True)
        self.value = True
        self.stop()

    @discord.ui.button(label='CaCncel', style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('cc', ephemeral=True)
        self.value = False
        self.stop()


class Meta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="hello")
    async def hello(self, ctx, *, member: discord.Member = None):
        """Says hello"""
        await ctx.send("hey")
        view = Confirm()
        await ctx.send(f'<@>, veux-tu envoyer ce CER ?', view=view)

    @commands.command()
    async def ask(self, ctx: commands.Context):
        """Asks the user a question to confirm something."""
        # We create the view and assign it to a variable so we can wait for it later.
        view = Confirm()
        await ctx.send('Do you want to continue?', view=view)
        # Wait for the View to stop listening for input...
        await view.wait()
        if view.value is None:
            print('Timed out...')
        elif view.value:
            print('Confirmed...')
        else:
            print('Cancelled...')
    
    @commands.command()
    @commands.is_owner()
    async def insert_value(self, ctx):

        query = '''
            INSERT INTO depot
            (user_id, file_path)
            VALUES
            ($1, $2)
            ON CONFLICT (user_id) DO UPDATE SET file_path = $3;
            '''
            
        async with self.bot.db_pool.cursor() as cursor:

            # Insert a row of data
            await cursor.execute(query, ctx.author.id, "CER/test.pdf", "CER/test.pdf")

            # Save (commit) the changes
            await self.bot.db_pool.commit()


        await ctx.send('Updated code.')
        
async def setup(bot):
    await bot.add_cog(Meta(bot))
