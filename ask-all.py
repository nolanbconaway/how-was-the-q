"""Ask all users."""

import datetime
import json
from app.models import User

# don't proceed if a weekend
if datetime.datetime.today().weekday() > 4:
    sys.exit()

# do it
statuses = User.ask_all()
print(json.dumps(statuses))
