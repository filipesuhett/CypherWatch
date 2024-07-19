from bot.valorant_account import ValorantAccount

class User:
    def __init__(self, discord_id):
        self.discord_id = discord_id
        self.valorant_accounts = []

    def add_account(self, account_name, account_id=None):
        # Check if account already exists
        if not any(acc.account_name == account_name for acc in self.valorant_accounts):
            account = ValorantAccount(account_name, account_id)
            self.valorant_accounts.append(account)
            return True
        return False

    def to_dict(self):
        return {
            'discord_id': self.discord_id,
            'valorant_accounts': [acc.to_dict() for acc in self.valorant_accounts]
        }

    @classmethod
    def from_dict(cls, data):
        user = cls(data['discord_id'])
        user.valorant_accounts = [ValorantAccount.from_dict(acc) for acc in data.get('valorant_accounts', [])]
        return user
