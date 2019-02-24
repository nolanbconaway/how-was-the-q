"""Remove MTA snapshot records without a rating.

Basically to save space. I'm not _made of money_.
"""

import datetime
import sys
import os

# hack to get parent dir on the path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from app.models import db, Snapshot

# query a view of ratings outer joined to snapshots
sql = "SELECT snapshot_id FROM rating_snapshot_map WHERE rating_id IS NULL"

seconds_in_day = 86400

# delete em
for (snapshot_id,) in db.session.execute(sql).fetchall():
    snapshot = Snapshot.query.get(snapshot_id)
    age_delta = datetime.datetime.utcnow() - snapshot.snapshot_dttm

    # only delete after 24h. The view only joins if the rating is within 18 but I like
    # having a little slack.
    if age_delta.total_seconds() < seconds_in_day:
        continue
    else:
        db.session.delete(snapshot)

# commit
db.session.commit()
