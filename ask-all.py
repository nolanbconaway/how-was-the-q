"""Ask all users."""

from app import User
import json
statuses = User.ask_all()
print(json.dumps(statuses))
