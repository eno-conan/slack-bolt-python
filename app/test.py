# reference
# https://note.com/marina1017/n/n4cdf5cd3e2d0
# https://slack.dev/bolt-python/concepts # Adapters
from slack_bolt import App
import os
from dotenv import load_dotenv
load_dotenv()

app = App(
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    token=os.environ.get("SLACK_BOT_TOKEN")
)

# There is nothing specific to Flask here!
# App is completely framework/runtime agnostic
@app.command("/modal-command")
def hello(body, ack):
    ack(f"Hi <@{body['user_id']}>!")

# Initialize Flask app
from flask import Flask, request
flask_app = Flask(__name__)

# SlackRequestHandler translates WSGI requests to Bolt's interface
# and builds WSGI response from Bolt's response.
from slack_bolt.adapter.flask import SlackRequestHandler

# Register routes to Flask app
@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    # handler runs App's dispatch method
    return handler.handle(request)


if __name__ == "__main__":
    handler = SlackRequestHandler(app)
    flask_app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

