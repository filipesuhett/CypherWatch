import discord
from discord.ext import commands, tasks
from bot.config import Config

class PeriodicTaskCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config()
        self.channel_id = self.config.guild_id  # Substitua por um ID de canal específico, se necessário
        self.check_situation.start()  # Inicia a tarefa periódica

    @tasks.loop(minutes=1)
    async def check_situation(self):
        # Iterar através dos usuários e imprimir as contas de Valorant
        for user in self.config.users:
            print(f'User ID: {user.discord_id}')
            for account in user.valorant_accounts:
                print(f'Account Name: {account.account_name}, PUUID: {account.puuid}, Region: {account.region}')

        # Exemplo de envio de mensagem a um canal no Discord
        channel = self.bot.get_channel(self.channel_id)
        if channel:
            await channel.send("Atualização das contas de Valorant dos usuários foi realizada!")

    @check_situation.before_loop
    async def before_check_situation(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user} has connected to Discord!')

def setup(bot):
    bot.add_cog(PeriodicTaskCog(bot))
