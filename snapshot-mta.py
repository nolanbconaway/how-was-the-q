import sys
import json
import datetime
import time
from app.models import Snapshot, db

# # don't proceed if a weekend
if datetime.datetime.today().weekday() > 4:
    sys.exit()

# list of feed ids to check
feed_ids = [1, 11, 16, 2, 21, 26, 31, 36, 51]

for feed_id in feed_ids:

    # try a handul of times to get the data
    try:
        data = Snapshot.capture(feed_id)
    except Exception as e:
        # empty data if it didn't work
        data = {'_EXCEPTION': str(e)}

    # add it to the database
    snapshot = Snapshot(feed_id, data, data_is_json=False)
    db.session.add(snapshot)
    db.session.commit()

    # log
    print('SNAPSHOT: %d' % feed_id)
