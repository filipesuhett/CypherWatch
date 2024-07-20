import discord
from discord.ext import commands, tasks
from bot.config import Config
from funcs.func_aux import verify_match

class PeriodicTaskCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config()
        self.channel_id = 1154468589206765628  # ID do canal como um inteiro
        self.check_situation.start()  # Inicia a tarefa periódica

    @tasks.loop(minutes=1)
    async def check_situation(self):
        channel = self.bot.get_channel(self.channel_id)

        for user in self.config.users:
            for account in user.valorant_accounts:
                embed = await verify_match(account.puuid, account.region, Config().api_key)  # Await here
                if embed:
                    if channel:
                        try:
                            # Enviar mensagem com menção ao usuário
                            user_mention = f"<@{user.discord_id}>"
                            await channel.send(f"{user_mention} Match details:", embed=embed)
                        except discord.Forbidden:
                            print(f'Não tenho permissão para enviar mensagens no canal {self.channel_id}')
                        except discord.HTTPException as e:
                            print(f'Ocorreu um erro ao tentar enviar a mensagem: {e}')
                    else:
                        print(f'Canal com ID {self.channel_id} não encontrado.')

    @check_situation.before_loop
    async def before_check_situation(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user} has connected to Discord!')

def setup(bot):
    bot.add_cog(PeriodicTaskCog(bot))
