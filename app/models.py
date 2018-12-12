"""Database models."""
import datetime
import time
import os
import json
import requests

# gtfs utils
import google
from google.transit import gtfs_realtime_pb2
from protobuf_to_dict import protobuf_to_dict

# within app imports
from app import db, slack_client

# get the MTA key
MTA_API_KEY = os.getenv('MTA_API_KEY')


class User(db.Model):
    """Database model for a user object."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    slack_id = db.Column(db.String(50), unique=True, nullable=False)
    slack_channel_id = db.Column(db.String(50), unique=True, nullable=False)
    signup_dttm = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.utcnow
    )
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    ratings = db.relationship('Rating', backref='user')

    @classmethod
    def get_or_create(cls, slack_id, slack_channel_id):
        """Get or create a user."""
        # check if user exists
        user = cls.get(slack_id)
        if user:
            return user

        # make a new user and add it.
        user = cls(slack_id=slack_id, slack_channel_id=slack_channel_id)
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def get(cls, slack_id):
        """Get a user from their slack_id."""
        return cls.query.filter_by(slack_id=slack_id).first()

    @classmethod
    def ask_all(cls):
        """Ask all enabled users."""
        statuses = {}
        for user in cls.query.filter_by(enabled=True).all():
            try:
                user.ask()
                statuses[user.id] = True
            except Exception:
                statuses[user.id] = False
        return statuses

    def message(self, text=None, **kwargs):
        """Quick wrapper to send a slack message to the user."""
        return slack_client.api_call(
            "chat.postMessage",
            channel=self.slack_channel_id,
            text=text,
            **kwargs
        )

    def ask(self):
        """Ask the user the question."""
        attach = [
            {
                "fallback": "Upgrade your Slack client.",
                "color": "#cfb439",
                "callback_id": "q_ask",
                "actions": [
                    {
                        "name": "response",
                        "text": "Great!",
                        "type": "button",
                        "value": "good",
                        "style": "primary",
                    },
                    {
                        "name": "response",
                        "text": "Just OK.",
                        "type": "button",
                        "value": "ok",
                        "style": "default",
                    },
                    {
                        "name": "response",
                        "text": "Real bad.",
                        "type": "button",
                        "value": "bad",
                        "style": "danger",
                    }
                ]
            }
        ]

        return self.message(
            text="How was the Q this morning?",
            attachments=attach
        )


class Rating(db.Model):
    """Database model for a rating object."""

    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    rating_dttm = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.utcnow
    )
    rating = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class GTFSWasEmptyError(Exception):
    """Quick exception for me."""
    pass

class Snapshot(db.Model):
    """Database model for a MTA status snapshots."""

    __tablename__ = 'mta_snapshots'

    id = db.Column(db.Integer, primary_key=True)
    snapshot_dttm = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.utcnow
    )
    feed_id = db.Column(db.Integer, nullable=False)
    json_data = db.Column(db.String(65535), nullable=True)

    def __init__(self, feed_id, data, data_is_json=True):
        self.feed_id = feed_id
        self.json_data = data if data_is_json else json.dumps(data)

    @staticmethod
    def capture(feed_id, retries=100, timeout=1):
        """Get GTFS data from MTS for a single feed."""
        def get():
            res = requests.get(
                'http://datamine.mta.info/mta_esi.php',
                params=dict(key=MTA_API_KEY, feed_id=feed_id)
            )
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(res.content)
            feed_dict = protobuf_to_dict(feed)
            if not feed_dict:
                raise GTFSWasEmptyError
            if 'entity' not in feed_dict:
                raise KeyError
            return feed_dict

        for retry in range(retries):
            try:
                r = get()
                break
            except (RuntimeWarning,
                    KeyError,
                    GTFSWasEmptyError,
                    google.protobuf.message.DecodeError):
                time.sleep(1)

        return r
