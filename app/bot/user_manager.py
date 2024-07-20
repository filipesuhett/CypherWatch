import json
import os
from bot.user import User

class UserManager:
    @staticmethod
    def load_users():
        """Load users from a JSON file."""
        if os.path.exists('users.json'):
            with open('users.json', 'r') as f:
                user_data = json.load(f)
                return [User.from_dict(data) for data in user_data]
        return []

    @staticmethod
    def save_users(users):
        """Save the users to a JSON file."""
        with open('users.json', 'w') as f:
            json.dump([user.to_dict() for user in users], f, indent=4)