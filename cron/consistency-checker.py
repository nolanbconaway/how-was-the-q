"""Confirm that the rating-snapshot map does not contain many-to-many.

It should be ONE rating to MANY snapshots.
"""

from app.models import db, User
import sys

# Each rating should not have multiple snapshots for the same feed.
sql = """
SELECT rating_id
FROM rating_snapshot_map m
INNER JOIN mta_snapshots s ON s.id = m.snapshot_id
WHERE snapshot_id IS NOT NULL AND rating_id IS NOT NULL
GROUP BY rating_id, feed_id
HAVING COUNT(*) > 1
"""

rating_ids = tuple(i for (i,) in db.session.execute(sql))


# each snapshot should not be associated with more than one rating.
sql = """
SELECT snapshot_id
FROM rating_snapshot_map m
WHERE snapshot_id IS NOT NULL AND rating_id IS NOT NULL
GROUP BY snapshot_id
HAVING COUNT(distinct rating_id) > 1
"""

snapshot_ids = tuple(i for (i,) in db.session.execute(sql))

# nothing to do if there are no records
if not any([snapshot_ids, rating_ids]):
    sys.exit(0)

# if you are here there is a problem
# send a notification if we have either case
nolan = User.query.filter_by(is_nolan=1).first()

message = (
    "Consistency checker revealed some suspect cases.\n\n"
    f"""- Ratings with multiple records per feed: `{rating_ids}`\n"""
    f"""- Snapshots with multiple ratings: `{snapshot_ids}`\n"""
)

for attempt in range(5):
    try:
        nolan.message(message)
        break
    except Exception:
        if attempt == 4:
            raise
        else:
            pass
