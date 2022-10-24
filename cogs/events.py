import asyncio
import discord
import random
import datetime
import asqlite
import os
from discord.ext import commands, tasks
from discord.ext.commands.cooldowns import BucketType
        
# class Confirm(discord.ui.View):
#     def __init__(self):
#         super().__init__()
#         self.value = None

#     @discord.ui.button(label='Confirmer', style=discord.ButtonStyle.green)
#     async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
#         await interaction.message.delete()
#         # await interaction.response.send_message('Confirmé!', ephemeral=True)
#         self.value = True
#         self.stop()

#     @discord.ui.button(label='Annuler', style=discord.ButtonStyle.grey)
#     async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
#         await interaction.message.delete()
#         await interaction.response.send_message('Annulé :(', ephemeral=True)
#         self.value = False
#         self.stop()

class ConfirmSQL(discord.ui.View):
    def __init__(self, path):
        super().__init__()
        self.value = None
        self.path = path

    @discord.ui.button(label='Confirmer', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        os.remove(f"{self.path}")
        
        await interaction.message.delete()
        await interaction.response.send_message('Confirmé, le remplacement a été effectué!', ephemeral=True)

        self.value = True
        self.stop()

    @discord.ui.button(label='Annuler', style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        await interaction.response.send_message("Rien n'a changé la putain de **** t'as cru quoi ?", ephemeral=True)
        self.value = False
        self.stop()

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        channel = None
        
    @commands.Cog.listener()
    async def on_message(self, message):
        
        if message.author.bot:
            return

        if message.channel.id == 1025396505873485905:

            channel = self.bot.get_channel(message.channel.id)

            if message.attachments:
            
                split_v1 = str(message.attachments).split("filename='")[1]
                filename = str(split_v1).split("' ")[0]
            
                if filename.endswith(".pdf"):

                    path = f"CER/{filename}"
                    await channel.send(f"Téléchargement du fichier {filename}, envoyé par <@{message.author.id}>...",delete_after=5)
                    await message.attachments[0].save(fp=path)
                    
                    async with self.bot.db_pool.cursor() as cursor:

                        search_query = '''
                        SELECT file_path FROM depot
                        WHERE user_id = $1;
                        '''

                        search_record = await self.bot.db_pool.fetchone(search_query, message.author.id)
                        if search_record[0] is not None:
                            await channel.send(f'⚠️ <@{message.author.id}>, tu as déjà un CER de déposé sous le nom de {search_record[0]}, veux-tu le remplacer par le nouveau {filename}?', view=ConfirmSQL(path=search_record[0]))

                        query = '''
                                    INSERT INTO depot
                                    (user_id, file_path)
                                    VALUES
                                    ($1, $2)
                                    '''

                        await cursor.execute(query, message.author.id, f"{path}")
                        await cursor.commit()

                else:
                    await channel.send(f"<@{message.author.id}>, il faut envoyer son CER, au format PDF", delete_after=10)                

            await message.delete()

        
async def setup(bot):
    await bot.add_cog(Events(bot))
