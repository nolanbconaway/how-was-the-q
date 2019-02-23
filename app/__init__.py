"""How was the Q train app."""

import json
import os
import datetime

# slack api
from slackclient import SlackClient

# flask essentials
from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template
from werkzeug.exceptions import BadRequest

# flask extensions
from flask_sqlalchemy import SQLAlchemy

# load dotenv
import dotenv

if os.path.exists(".env"):
    dotenv.load_dotenv(dotenv_path=".env")
elif os.path.exists("../.env"):
    dotenv.load_dotenv(dotenv_path="../.env")

# tokens
SLACK_BOT_OAUTH_ACCESS_TOKEN = os.getenv("SLACK_BOT_OAUTH_ACCESS_TOKEN")
SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
SECRET_PASSWORD = os.getenv("SECRET_PASSWORD")

# init vars
app = Flask(__name__)
slack_client = SlackClient(SLACK_BOT_OAUTH_ACCESS_TOKEN)

# set up extensions
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# within app imports.
# Learn to live with the pycodestyle E402 because the imports are circular.
from app.models import Rating, User


@app.route("/healthcheck")
def healthcheck():
    """Health check."""
    return "YESOK"


def is_regular_message(event_data):
    """Check if an event is like a conversational message."""
    if (
        event_data["type"] == "event_callback"
        and "event" in event_data
        and "bot_id" not in event_data["event"]
        and "type" in event_data["event"]
        and "message" == event_data["event"]["type"]
        and "text" in event_data["event"]
    ):
        return True
    return False


def message_handler(event_data):
    """Handle conversational style messages.

    Does not return anything.
    """
    # get message info
    message = event_data["event"]["text"].lower()
    slack_user_id = event_data["event"]["user"]
    slack_channel_id = event_data["event"]["channel"]

    # DISABLE HANDLER: Set the enabled flag to false.
    if any(x == message for x in ("stop", "disable")):
        user = User.get(slack_user_id)
        if not user or not user.enabled:
            user.message("You're not getting Q train messages as-is...")
            return
        user.enabled = False
        db.session.commit()
        user.message("Ok! I'll stop asking you about the Q train.")
        return

    # get user object for remaining handlers.
    user = User.get_or_create(slack_user_id, slack_channel_id)

    # ENABLE HANDLER: Set the enabled flag to true.
    if any(x == message for x in ("start", "enable")):
        if user.enabled:
            user.message("You're already set up for Q train messages!")
            return
        user.enabled = True
        db.session.commit()
        user.message("Ok! I'll start asking you about the Q train.")
        return

    # ASK HANDLER: see if the user wants the question
    if message == "ask":
        if not user.enabled:
            user.message(
                "If you want to get this question regularly, just send me a "
                "message like: `enable`."
            )
        user.ask()
        return

    return


@app.route("/action", methods=["POST"])
def action():
    """Handle actions."""
    # get POST request data
    event_data = json.loads(request.data.decode("utf-8"))

    # handle the challenge if there was one
    if "challenge" in event_data:
        return jsonify(event_data.get("challenge"))

    # do nothing if this is a bot message
    if "bot_id" in event_data["event"]:
        return "OK"

    # Handle messages in the DM.
    if is_regular_message(event_data):
        message_handler(event_data)

    # otherwise do nothing
    return "OK"


@app.route("/interact", methods=["POST"])
def interact():
    """Handle interactions."""
    # get POST form data
    payload = json.loads(request.form["payload"])

    # handle the Q question
    if payload["callback_id"] == "q_ask":
        response = payload["actions"][0]["value"]
        user_slack_id = payload["user"]["id"]
        slack_channel_id = payload["channel"]["id"]

        # get user object, append rating
        user = User.get_or_create(user_slack_id, slack_channel_id)
        user.ratings.append(Rating(rating=response))
        db.session.commit()

        if response == "bad":
            return "Ouch, sorry bud :slightly_frowning_face:"
        elif response == "ok":
            return "Ok! I got it."
        elif response == "good":
            return "Nice! :ok_hand:"

    # otherwise do nothing
    return "OK"


@app.route("/", methods=["GET"])
def webui():
    """Render the web ui."""
    return render_template(
        "index.html", ratings=Rating.query.order_by(-Rating.rating_dttm).all()
    )
