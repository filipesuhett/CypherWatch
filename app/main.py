from bot.config import Config
from commands.users import Users_Command
from commands.discord import Discord_Command
import sys

def main():
    config = Config()
    bot = config.bot

    bot.add_cog(Users_Command(bot))
    bot.add_cog(Discord_Command(bot))

    @bot.event
    async def on_error(event, *args, **kwargs):
        """Event handler for when an error occurs."""
        print(f"Error occurred: {event}")
    
    bot.run(config.token_discord)

if __name__ == "__main__":
    main()
