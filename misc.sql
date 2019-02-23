-- Create a joined view of ratings and snapshots.
--
-- I am a big dummy and I do not associate a rating with a particular snapshot
-- so any snapshots <= 18 hours before the rating are good enough.
--
-- In basically all cases it should just be the one, unless something weird
-- happened to me. I have no idea how multiple matches would handle in the
-- groupby-case statements.
--
-- Have to do this right / left join union because the maniacs at mysql don't have an
-- outer join.
-- https://dev.mysql.com/doc/refman/8.0/en/outer-join-simplification.html
CREATE VIEW rating_snapshot_map AS
SELECT s.id as snapshot_id, r.id as rating_id
FROM ratings r
LEFT JOIN mta_snapshots s
ON TIMESTAMPDIFF(HOUR, s.snapshot_dttm, r.rating_dttm) < 18
AND TIMESTAMPDIFF(HOUR, s.snapshot_dttm, r.rating_dttm) >= 0
UNION
SELECT s.id as snapshot_id, r.id as rating_id
FROM ratings r
RIGHT JOIN mta_snapshots s
ON TIMESTAMPDIFF(HOUR, s.snapshot_dttm, r.rating_dttm) < 18
AND TIMESTAMPDIFF(HOUR, s.snapshot_dttm, r.rating_dttm) >= 0


-- Create a tidy view of the ratings mapped to their snapshots.
--
-- So that each rating is a row and each snapshot is a column.
CREATE VIEW daily AS
SELECT
  cast(r.rating_dttm as date) AS dt
, max(r.rating) AS rating
, max((case when (s.feed_id = 1) then s.json_data else NULL end)) AS feed_1
, max((case when (s.feed_id = 11) then s.json_data else NULL end)) AS feed_11
, max((case when (s.feed_id = 16) then s.json_data else NULL end)) AS feed_16
, max((case when (s.feed_id = 2) then s.json_data else NULL end)) AS feed_2
, max((case when (s.feed_id = 21) then s.json_data else NULL end)) AS feed_21
, max((case when (s.feed_id = 26) then s.json_data else NULL end)) AS feed_26
, max((case when (s.feed_id = 31) then s.json_data else NULL end)) AS feed_31
, max((case when (s.feed_id = 36) then s.json_data else NULL end)) AS feed_36
, max((case when (s.feed_id = 51) then s.json_data else NULL end)) AS feed_51
FROM rating_snapshot_map m
JOIN ratings r ON m.rating_id = r.id
JOIN mta_snapshots s ON m.snapshot_id = s.id
group by cast(r.rating_dttm as date)
order by 1 desc;
