import os
import pytz
import discord
from bot.bot import Bot
from bot.user_manager import UserManager
from bot.user import User
from bot.user import User
from bot.async_api_manager import AsyncAPIManager

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
        self.api_keys = os.getenv('API_KEYS').split(",")
        self.api_key = os.getenv('API_KEY')  # Assumes multiple API keys are comma-separated
        self.users = UserManager.load_users()

        # Ensure all accounts have the 'has_notificated' and 'to_mark' fields
        self.ensure_additional_fields()

        # Initialize the bot
        intents = discord.Intents.all()
        intents.message_content = True
        self.bot = Bot(command_prefix='/', help_command=None, intents=intents)

        # Initialize API manager
        self.api_manager = AsyncAPIManager(self.api_keys)

    def ensure_additional_fields(self):
        for user in self.users:
            for account in user.valorant_accounts:
                if not hasattr(account, 'has_notificated'):
                    account.has_notificated = False
                if not hasattr(account, 'to_mark'):
                    account.to_mark = False
        self.save_users()

    def save_users(self):
        """Save the users to a JSON file."""
        UserManager.save_users(self.users)

    def add_user(self, discord_id):
        """Add a new user if not already in the list."""
        if not any(user.discord_id == discord_id for user in self.users):
            user = User(discord_id)
            self.users.append(user)
            self.save_users()
            return user
        return None

    def update_user(self, discord_id, account_name, account_id=None):
        """Update an existing user with a new Valorant account."""
        user = next((user for user in self.users if user.discord_id == discord_id), None)
        if user:
            user.add_account(account_name, account_id)
            self.save_users()
            return user
        return None
    
    async def make_request(self, url, params=None):
        return await self.api_manager.get(url, params=params)