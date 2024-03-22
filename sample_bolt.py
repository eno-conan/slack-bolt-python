import os
import logging
from slack_bolt import App, Ack, Say, BoltContext, Respond
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
import slack_operations

logging.basicConfig(level=logging.INFO)

from dotenv import load_dotenv
load_dotenv()

# 操作選択のためのドロップダウンBLOCK
SELECT_ACTION_DROPDOWN_BLOCK = {
                    "type": "section",
                    "block_id": "operation",
                    "text": {
                        "type": "mrkdwn",
                        "text": "操作を選択"
                    },
                    "accessory": {
                        "type": "static_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "選択",
                        },
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "チャンネル新規作成",
                                },
                                "value": "create-channel"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "メンバー追加",
                                },
                                "value": "add-members"
                            },
                        ],
                        "action_id": "static_select_action"
                    }
                }

# ユーザ複数選択のBLOCK
SELECT_MULTI_USER_BLOCK = {
                            "type": "input",
                            "block_id": "select-users",
                            "element": {
                                "type": "multi_users_select",
                                "placeholder": {
                                    "type": "plain_text",
                                    "text": "Select users",
                                },
                                "action_id": "select-users-action"
                            },
                            "label": {
                                "type": "plain_text",
                                "text": "対象メンバー",
                            },
                            "optional": False,
                        }

# ボットトークンとソケットモードハンドラーを使ってアプリを初期化
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# ショートカットでモーダル起動
@app.shortcut("modal-shortcut")
def handle_shortcuts(ack: Ack, body: dict, client: WebClient):
    # 受信した旨を3秒以内にSlackサーバーに伝達
    ack()
    # モーダル生成
    client.views_open(
        trigger_id=body["trigger_id"],
        view = {
            "type": "modal",
            "callback_id": "modal-id",
            "title": {"type": "plain_text", "text": "Slack操作お助けマン"},
            "close": {"type": "plain_text", "text": "閉じる"},
            "blocks": [
                        SELECT_ACTION_DROPDOWN_BLOCK
                        ],
        },
    )

@app.action("static_select_action")
def update_modal(ack: Ack, body: dict, client: WebClient):
    # ボタンのリクエストを確認
    ack()
    view = {               
            "type": "modal",
            "callback_id": "modal-id",
            "title": {"type": "plain_text", "text":"Slackお助けマン"},
            "submit": {"type": "plain_text", "text": "送信"},
            "close": {"type": "plain_text", "text": "閉じる"}
        }

    # ドロップダウンの入力値取得
    selected_operation = body["view"]["state"]["values"]['operation'] \
        ["static_select_action"]["selected_option"]["value"]
    
    if selected_operation == 'create-channel':
        view["blocks"] = [
            {
                "type": "input",
                "block_id": "create-channel",
                "element": {
                                "type": "plain_text_input", 
                                "action_id": "action-id",
                                "placeholder": {
                                    "type": "plain_text",
                                    "text": "チャンネル名入力",
                                }
                            },
                "label": {"type": "plain_text", "text": "新規チャンネル名"},
                "optional": False,
            },
            SELECT_MULTI_USER_BLOCK
                ]
        client.views_update(
            view_id=body["view"]["id"],
            hash=body["view"]["hash"],
            view=view
        )
    elif selected_operation== 'add-members':
        view["blocks"] = [
                    {
                        "type": "input",
                        "label": {
                            "type": "plain_text",
                            "text": "既存チャンネル名"
                            
                        },
                        "optional": False,
                        "block_id": "select-channel",
                        "element": {
                            "type": "conversations_select",
                            # "type": "multi_conversations_select",
                            "placeholder": {
                                "type": "plain_text",
                                "text": ":mega: メンバーを追加するチャンネル選択"
                            },
                            "action_id": "conversations_select-action"
                        }
                    }, 
                    SELECT_MULTI_USER_BLOCK
                ]
        client.views_update(
            view_id=body["view"]["id"],
            hash=body["view"]["hash"],
            view=view
        )
    else:
        view["blocks"]=[
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": "This is a plain text section block.",
                }
            }
            ]
        client.views_update(
        view_id=body["view"]["id"],
        hash=body["view"]["hash"],
        
        view=view
                # {
                #     "type": "section",
                #     "text": {"type": "plain_text", "text":"You updated the modal!"}
                # },
                # {
                #     "type": "image",
                #     "image_url": "https://media.giphy.com/media/SVZGEcYt7brkFUyU90/giphy.gif",
                #     "alt_text":"Yay!The modal was updated"
                # }
    )

# view_submissionリクエストを処理
@app.view("modal-id")
def handle_submission(ack: Ack, body, client, view: dict, logger:logging.Logger):
    submitted_data = view["state"]["values"]
    
    # 【入力値検証】
    # チャンネル入力でユーザが含まれる場合
    # ユーザ入力にチャンネルが含まれる場合
    # 新規チャンネル側で入力したチャンネルが既に存在する場合
    
    if submitted_data.get('create-channel'):
        # チャンネル新規作成
        create_channel_name = submitted_data['create-channel']['action-id']['value']
        print(create_channel_name)
    elif submitted_data.get('select-channel'):
        # チャンネルメンバー追加
        target_channel = submitted_data['select-channel']['conversations_select-action']['selected_conversation']
        print(target_channel)
    else:
        pass
    users = submitted_data['select-users']['select-users-action']['selected_users']
    print(users)
        
    # slack_operations.fetch_conversations(client)
    # errors = {}
    # if hopes_and_dreams is not None and len(hopes_and_dreams) <= 5:
    #     errors["create-channel"] = "The value must be longer than 5 characters"
    #     # client.chat_postMessage(channel=user, text=msg)
    # if len(errors) > 0:
    #     print("AAA")
    #     ack(response_action="errors", errors=errors)
    #     return
    
    # モーダルを閉じる
    ack()
    
    # 入力結果をユーザーに送信
    userId = body["user"]["id"]
    msg = f"<@{userId}>さんから申請がありました\n"

    # ユーザーにメッセージを送信
    try:
        client.chat_postMessage(channel='C06QD36AEUA', text=msg)
    except Exception as e:
        logger.exception(f"Failed to post a message {e}")

# アプリを起動
if __name__ == "__main__":
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()

# 以下、念のため保存
# メンションによる処理呼び出し
# @app.event("app_mention")
# def handle_app_mention(body: dict, say, logger,client: WebClient):
#     # メンションされたメッセージを取得
#     # text = body["event"]["text"]
#     # logger.info(f"メンションされました: {text}")
#     # # 応答メッセージを送信
#     # say(f"メンションを受信しました: {text}")
    
#     # time.sleep(3)
#     mention = body["event"]
#     print(mention)
#     # メンションされたメッセージを取得
#     text = mention["text"]
#     thread_ts = mention["ts"]
    
#     slack_operations.fetch_conversations(client)
#     # create_conversations(client)
#     # invite_user(client)
    
#     # 例: メンションされたメッセージをログに出力する
#     logger.info(f"メンションされました: {text}")
    
#     # 応答メッセージを送信（スレッドに送信）
#     # https://zenn.dev/t_yng/scraps/8374a9616c235e
#     say(f"{text}", thread_ts=thread_ts)

# スラッシュコマンド
# @app.command("/modal-command")
# def handle_some_command(ack: Ack, body: dict, client: WebClient):
#     # 受信した旨を 3 秒以内に Slack サーバーに伝えます
#     ack()
#     # views.open という API を呼び出すことでモーダルを開きます
#     client.views_open(
#         # 上記で説明した trigger_id で、これは必須項目です
#         # この値は、一度のみ 3 秒以内に使うという制約があることに注意してください
#         trigger_id=body["trigger_id"],
#         # モーダルの内容を view オブジェクトで指定します
#         view={
#             # このタイプは常に "modal"
#             "type": "modal",
#             # このモーダルに自分で付けられる ID で、次に説明する @app.view リスナーはこの文字列を指定します
#             "callback_id": "modal-id",
#             # これは省略できないため、必ず適切なテキストを指定してください
#             "title": {"type": "plain_text", "text": "テストモーダル"},
#             # input ブロックを含まないモーダルの場合は view から削除することをおすすめします
#             # このコード例のように input ブロックがあるときは省略できません
#             "submit": {"type": "plain_text", "text": "送信"},
#             # 閉じるボタンのラベルを調整することができます（必須ではありません）
#             "close": {"type": "plain_text", "text": "閉じる"},
#             # Block Kit の仕様に準拠したブロックを配列で指定
#             # 見た目の調整は https://app.slack.com/block-kit-builder を使うと便利です
#             "blocks": [
#                 {
#                     # モーダルの通常の使い方では input ブロックを使います
#                     # ブロックの一覧はこちら: https://api.slack.com/reference/block-kit/blocks
#                     "type": "input",
#                     # block_id / action_id を指定しない場合 Slack がランダムに指定します
#                     # この例のように明に指定することで、@app.view リスナー側での入力内容の取得で
#                     # ブロックの順序に依存しないようにすることをおすすめします
#                     "block_id": "question-block",
#                     # ブロックエレメントの一覧は https://api.slack.com/reference/block-kit/block-elements
#                     # Works with block types で Input がないものは input ブロックに含めることはできません
#                     "element": {"type": "plain_text_input", "action_id": "input-element"},
#                     # これはモーダル上での見た目を調整するものです
#                     # 同様に placeholder を指定することも可能です 
#                     "label": {"type": "plain_text", "text": "質問"},
#                 }
#             ],
#         },
#     )

# スラッシュコマンドでの入力処理
# @app.view("modal-id")
# def handle_view_events(ack: Ack, view: dict, logger: logging.Logger):
#     # 送信された input ブロックの情報はこの階層以下に入っています
#     inputs = view["state"]["values"]
#     # 最後の "value" でアクセスしているところはブロックエレメントのタイプによっては異なります
#     # パターンによってどのように異なるかは後ほど詳細を説明します
#     question = inputs.get("question-block", {}).get("input-element", {}).get("value")
#     # 入力チェック
#     if len(question) < 5:
#         # エラーメッセージをモーダルに表示
#         # （このエラーバインディングは input ブロックにしかできないことに注意）
#         ack(response_action="errors", errors={"question-block": "質問は 5 文字以上で入力してください"})
#         return

#     # 正常パターン、実際のアプリではこのタイミングでデータを保存したりする
#     logger.info(f"Received question: {question}")

#     # 空の応答はこのモーダルを閉じる（ここまで 3 秒以内である必要あり）
#     ack()