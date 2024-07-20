from bot.config import Config
from commands.users import Users_Command
from commands.discord import Discord_Command
from commands.match import Match_Command
from commands.tasks import PeriodicTaskCog

def main():
    config = Config()
    bot = config.bot

    bot.add_cog(Users_Command(bot))
    bot.add_cog(Discord_Command(bot))
    bot.add_cog(Match_Command(bot))
    bot.add_cog(PeriodicTaskCog(bot))  # Adicione a tarefa periódica

    @bot.event
    async def on_error(event, *args, **kwargs):
        """Event handler for when an error occurs."""
        print(f"Error occurred: {event}")

    bot.run(config.token_discord)

if __name__ == "__main__":
    main()