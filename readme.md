# How was the Q this morning? Slack Data Collector.

Most weekdays I take the Q train from Parkside ave to Herald Square. Sometimes
the commute is quite nice, about 40 mins. But other times the trip can become
a big hassle, in which I have to think about where I might transfer lines to
avoid massive delays.

If I knew ahead of time whether the Q line will be crushed, then I would walk
to another line nearby and avoid all of it. But the usual sources of
information (MTA twitter, official MTA apps, etc) provide only limited support:

- The notifications are usually sent out too late. Sometimes it's as much as 30
mins before I'll see anything online, during which time I've already committed
to the Q and am living the nightmare.
- The notifications do not account for many cross-line dependencies. For
example, most delays on the B line will eventually surface along the Q. So
then I'll find myself checking the status of multiple train lines to get
information that is too old to be of any use.

## What I am doing

I am going to use machine learning to forecast delays on the Q. The MTA offers
free access to real-time data. I only need to come up with labelled training
data to learn a model which predicts whether my morning train will be delayed.

This repo specifies an API which interacts with Slack through a bot user. Every
day the bot asks me how my train ride was, and that's my training labels.

A scheduled script captures the MTA realtime GTFS data through their API. I set
it up to run every day right before I leave for work. With some time, I'll have
enough training data to predict my morning train's delays from the state of the
MTA per its API data.


## TODO

- [x] Schedule asks.
- [ ] Fix messages from repeat-sending? IDK whats happening here.
- [x] Backup system.
- [x] Move scheduled ask from an endpoint to an in-app script only.
- [ ] Message handlers should be slash commands like `/q ask`.
- [ ] Add cancel button to ask UI.
- [ ] Add context to the bot response for the question.
