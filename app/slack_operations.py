import os
from typing import List
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App, Ack
from slack_bolt.adapter.socket_mode import SocketModeHandler
from time import time
from dotenv import load_dotenv
load_dotenv()
import time

# https://slack.dev/python-slack-sdk/web/index.html#conversations

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
# https://api.slack.com/methods/conversations.create
def create_conversation(client: WebClient,channel_name:str):
    try:
        # channel_name = f'my-private-channel-{round(time())}'
        response = client.conversations_create(
            name=channel_name,
            is_private=False
        )
        channel = response['channel']
        return channel
    except SlackApiError as e:
        print('Error creating conversations: {}'.format(e))

def getting_conversation_info(client: WebClient,channel_id:str):
    try:
        response = client.conversations_info(
        channel=channel_id,
        include_num_members=0
        )
        return response['channel']
    except SlackApiError as e:
        print('Error getting conversation info: {}'.format(e))

def invite_users(client: WebClient,channel_id:str,invite_users_list:List[str]):
    try:
        response = client.conversations_invite(
            channel=channel_id,
            users=invite_users_list
            # users=['U06Q3MANP29']
        )
        return response
    except SlackApiError as e:
        print('Error inviting conversations: {}'.format(e))