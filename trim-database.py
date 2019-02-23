"""Remove MTA snapshot records without a rating.

Basically to save space. I'm not _made of money_.
"""

from app.models import db, Snapshot

sql = """
SELECT snapshot_id
FROM rating_snapshot_map
WHERE rating_id IS NULL
"""

# delete em
for (snapshot_id,) in db.session.execute(sql):
    snapshot = Snapshot.query.get(snapshot_id)
    db.session.delete(snapshot)

# commit
db.session.commit()
