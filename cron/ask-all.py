"""Ask all users."""

import datetime
import sys
import os

# hack to get parent dir on the path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from app.models import User

# don't proceed if a weekend
if datetime.datetime.today().weekday() > 4:
    sys.exit()

# do it
statuses = User.ask_all()
for k, v in statuses.items():
    print(k, v)
