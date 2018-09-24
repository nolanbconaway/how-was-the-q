"""Database models."""
import datetime
from app import db, slack_client


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
