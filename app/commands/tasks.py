import discord
from discord.ext import commands, tasks
from bot.config import Config
from funcs.func_aux import verify_match, update_account
import asyncio
class PeriodicTaskCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config()
        self.channel_id = 1264224851216957493  # ID do canal como um inteiro
        self.check_situation.start()   # Inicia a tarefa periódica
        self.update_all_nicknames.start()

    @tasks.loop(minutes=10)
    async def check_situation(self):
        channel = self.bot.get_channel(self.channel_id)

        count = 0  # Contador para rastrear o número de contas processadas

        for user in self.config.users:
            for account in user.valorant_accounts:
                if account.has_notificated == False:  # Verifica se o usuário possui notificação
                    embed = await verify_match(account.puuid, account.region, Config().api_key)  # Await here
                    if embed:
                        if channel:
                            try:
                                # Enviar mensagem com menção ao usuário
                                user_mention = f"<@{user.discord_id}>"
                                # user_mention = f""
                                if account.to_mark:
                                    await channel.send(f"{user_mention} Match details:", embed=embed)
                                else:
                                    await channel.send(f"Match details:", embed=embed)
                                account.has_notificated = True
                            except discord.Forbidden:
                                print(f'Não tenho permissão para enviar mensagens no canal {self.channel_id}')
                            except discord.HTTPException as e:
                                print(f'Ocorreu um erro ao tentar enviar a mensagem: {e}')
                        else:
                            print(f'Canal com ID {self.channel_id} não encontrado.')
                    else:
                        account.has_notificated = False
                else:
                    account.has_notificated = False
                count += 1  # Incrementa o contador

    @tasks.loop(hours=1)
    async def update_all_nicknames(self):
        await asyncio.sleep(120)
        print('Updating all nicknames...')
        for user in self.config.users:
            for account in user.valorant_accounts:
                nick_verified = await update_account(account.puuid, account.region, account.account_name)
                if nick_verified != True:
                    print(f'old nickname: {account.account_name}, new nickname: {nick_verified}')
                    account.update_nickname(nick_verified)
        self.config.save_users()
                    
    @check_situation.before_loop
    async def before_check_situation(self):
        await self.bot.wait_until_ready()
        
    @update_all_nicknames.before_loop
    async def before_update_all_nicknames(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user} has connected to Discord!')

def setup(bot):
    bot.add_cog(PeriodicTaskCog(bot))
