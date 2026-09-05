import os
import requests
from dotenv import load_dotenv
load_dotenv()

def send_slack_message(state):
    token = REDACTED
    channel = os.getenv("SLACK_CHANNEL")

    response = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        },
        json={
            "channel": channel,
            "text": state["summary"]
        }
    ).json()

    if not response.get("ok"):
        raise RuntimeError(response)

    print("Slack message sent.")
    return {}
