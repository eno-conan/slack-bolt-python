import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App, Ack
from slack_bolt.adapter.socket_mode import SocketModeHandler
from time import time
from dotenv import load_dotenv
load_dotenv()
import time

# https://slack.dev/python-slack-sdk/web/index.html#conversations

# app = App(token=os.environ.get("SLACK_BOT_TOKEN_SLACK_OPERATIONS"))

'''
流れとしては・・・
1. メンションで処理呼び出し受け付け
'''
# Listup channels
# https://api.slack.com/methods/conversations.list/code
def fetch_conversations(client: WebClient):
    try:
        response = client.conversations_list(
            types='public_channel, private_channel'
        )
        channels_name = []
        for channel in response['channels']:
            channels_name.append(channel['name'])
        return channels_name

    except SlackApiError as e:
        print('Error fetching conversations: {}'.format(e))

# Create Channnel
# https://api.slack.com/methods/conversations.create/code
def create_conversations(client: WebClient):
    try:
        channel_name = f'my-private-channel-{round(time())}'
        response = client.conversations_create(
            name=channel_name,
            is_private=False
        )
        channel_id = response['channel']['id']
        print(channel_id)
    # response = client.conversations_archive(channel=channel_id)
    except SlackApiError as e:
        print('Error fetching conversations: {}'.format(e))

def invite_user(client: WebClient):
    try:
        response = client.conversations_invite(
            channel='C02SC65KEBD',
            users=['U06Q3MANP29']
        )
        print(response)
    except SlackApiError as e:
        print('Error fetching conversations: {}'.format(e))
        # 既に参加した状態でAPI実行したとき、以下のレスポンス
        # {'ok': False, 'error': 'already_in_channel', 'errors': [{'user': 'U06Q3MANP29', 'ok': False, 'error': 'already_in_channel'}]}