import os
import json

def load_users():
    os.makedirs("data", exist_ok=True)
    path = "data/users.json"
    if not os.path.exists(path):
        sample_data = {
            "123456": {"pin": "1111", "balance": 1000},
            "654321": {"pin": "2222", "balance": 2000}
        }
        with open(path, "w") as f:
            json.dump(sample_data, f, indent=4)

    with open(path, "r") as f:
        data = json.load(f)
        from PyQt6.lupdate.user import User
        users = {card: User(card, info["pin"], info["balance"]) for card, info in data.items()}
        return users
