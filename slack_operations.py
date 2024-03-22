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
            types="public_channel, private_channel"
        )
        for channel in response['channels']:
            print(f'{channel["name"] , channel["id"] }')

    except SlackApiError as e:
        print("Error fetching conversations: {}".format(e))

# Create Channnel
# https://api.slack.com/methods/conversations.create/code
def create_conversations(client: WebClient):
    try:
        channel_name = f"my-private-channel-{round(time())}"
        response = client.conversations_create(
            name=channel_name,
            is_private=False
        )
        channel_id = response["channel"]["id"]
        print(channel_id)
    # response = client.conversations_archive(channel=channel_id)
    except SlackApiError as e:
        print("Error fetching conversations: {}".format(e))

def invite_user(client: WebClient):
    try:
        response = client.conversations_invite(
            channel='C02SC65KEBD',
            users=['U06Q3MANP29']
        )
        # 別途トークンがいるのか？（ユーザしかできないみたい）
        # response = client.conversations_inviteShared(
        #     channel='C02SC65KEBD',
        #     user_ids=['U06Q3MANP29']
        # )
        print(response)
    except SlackApiError as e:
        print("Error fetching conversations: {}".format(e))
        # 既に参加した状態でAPI実行したとき、以下のレスポンス
        # {'ok': False, 'error': 'already_in_channel', 'errors': [{'user': 'U06Q3MANP29', 'ok': False, 'error': 'already_in_channel'}]}

# @app.event("app_mention")
# def handle_app_mention(body: dict, say, logger,client: WebClient):
#     # time.sleep(3)
#     # ユーザ複数選択時、どういった形で値を受け取るのか？
#     mention = body["event"]
#     print(mention)
#     # メンションされたメッセージを取得
#     text = mention["text"]
#     thread_ts = mention["ts"]
    
#     fetch_conversations(client)
#     # create_conversations(client)
#     # invite_user(client)
    
#     # 例: メンションされたメッセージをログに出力する
#     logger.info(f"メンションされました: {text}")
    
#     # 応答メッセージを送信（スレッドに送信）
#     # https://zenn.dev/t_yng/scraps/8374a9616c235e
#     say(f"{text}", thread_ts=thread_ts)

# if __name__ == "__main__":
#     SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN_SLACK_OPERATIONS")).start()