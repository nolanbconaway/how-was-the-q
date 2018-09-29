"""Ask all users."""

import datetime
import sys
from app.models import User

# don't proceed if a weekend
if datetime.datetime.today().weekday() > 4:
    sys.exit()

# do it
statuses = User.ask_all()
for k, v in statuses.items():
    print(k, v)
