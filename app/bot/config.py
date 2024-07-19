import os
import pytz
import json
import discord
from bot.bot import Bot
from bot.user_manager import UserManager

class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        # Variables
        self.channel_name = os.getenv('CHANNEL_NAME')
        self.timeout = int(os.getenv('TIMEOUT'))
        self.token_discord = os.getenv('DISCORD_TOKEN')
        self.brazil = pytz.timezone("America/Sao_Paulo")
        self.guild_id = os.getenv('GUILD_ID')
        self.dry_run = os.getenv('DRY_RUN')
        self.users = UserManager.load_users()
        
        # Initialize the bot
        intents = discord.Intents.all()
        intents.message_content = True
        self.bot = Bot(command_prefix='/', help_command=None, intents=intents)
    
    def save_users(self):
        """Save the users to a JSON file."""
        UserManager.save_users(self.users)
