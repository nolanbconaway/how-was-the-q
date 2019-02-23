"""Remove MTA snapshot records without a rating.

Basically to save space. I'm not _made of money_.
"""

from app.models import db, Snapshot
import datetime

# query a view of ratings outer joined to snapshots
sql = """
SELECT snapshot_id
FROM rating_snapshot_map
WHERE rating_id IS NULL
"""

seconds_in_day = 86400

# delete em
for (snapshot_id,) in db.session.execute(sql):
    snapshot = Snapshot.query.get(snapshot_id)
    age_seconds = datetime.datetime.now() - snapshot.snapshot_dttm

    # only delete after 24h. The view only joins if the rating is within 18 but i think
    # there might be a timezone bug so lets keep em around for a day.
    if age_seconds < seconds_in_day:
        continue
    else:
        db.session.delete(snapshot)

# commit
db.session.commit()
