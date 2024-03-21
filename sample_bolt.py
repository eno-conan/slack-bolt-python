import os
import logging
from slack_bolt import App, Ack, Say, BoltContext, Respond
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient

# デバッグレベルのログを有効化
logging.basicConfig(level=logging.DEBUG)

from dotenv import load_dotenv
load_dotenv()

# ボットトークンとソケットモードハンドラーを使ってアプリを初期化
app = App(token=os.environ.get("SLACK_BOT_TOKEN2"))

# アプリ（slack-management-app）をワークフロー内のメンション経由で呼び出す
@app.event("app_mention")
def handle_app_mention(body, say, logger):
    # メンションされたメッセージを取得
    text = body["event"]["text"]
    logger.info(f"メンションされました: {text}")
    
    # 応答メッセージを送信
    say(f"メンションを受信しました: {text}")

# ショートカットを使って必要事項を入力
@app.shortcut("modal-shortcut")
def handle_shortcuts(ack: Ack, body: dict, client: WebClient):
    # 受信した旨を 3 秒以内に Slack サーバーに伝達
    ack()
    # 組み込みのクライアントで views_open を呼び出し
    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "modal-id",
            "title": {"type": "plain_text", "text": "Slack操作お助けマン"},
            "submit": {"type": "plain_text", "text": "送信"},
            "close": {"type": "plain_text", "text": "閉じる"},
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "操作を選択"
                    },
                    "accessory": {
                        "type": "static_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "選択",
                            "emoji": True
                        },
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "チャンネル新規作成",
                                    "emoji": True
                                },
                                "value": "create-channel"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "メンバー追加",
                                    "emoji": True
                                },
                                "value": "add-members"
                            },
                        ],
                        "action_id": "static_select_action"
                    }
                },                
            ],
        },
    )

# モーダルに含まれる、`button_abc` という action_id のボタンの呼び出しをリッスン
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
    # block_idだけ動的みたい
    block_id = body["view"]["blocks"][0]["block_id"]
    # 入力値取得
    selected_operation = body["view"]["state"]["values"][block_id]["static_select_action"]["selected_option"]["value"]
    
    if selected_operation == 'create-channel':
        view["blocks"] = [
                    {
                        "type": "input",
                        "block_id": "text-input",
                        "element": {"type": "plain_text_input", "action_id": "action-id",
                                    "placeholder": {
                                        "type": "plain_text",
                                        "text": "チャンネル名入力",
                                        "emoji": True
                                        }
                                    },
                        "label": {"type": "plain_text", "text": "新規チャンネル名",},
                        "optional": True,
                    },
                    {
                        "type": "input",
                        "element": {
                            "type": "multi_users_select",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Select users",
                                "emoji": True
                            },
                            "action_id": "multi_users_select-action"
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "対象メンバー",
                            "emoji": True
                        }
                    },
                ]
        client.views_update(
            # view_id を渡すこと
            view_id=body["view"]["id"],
            # 競合状態を防ぐためのビューの状態を示す文字列
            hash=body["view"]["hash"],
            # 更新後の blocks を含むビューのペイロード
            view=view
        )
    elif selected_operation== 'add-members':
        view["blocks"] = [
                    {
                        "type": "input",
                        "label": {
                            "type": "plain_text",
                            "text": "既存チャンネル名",
                            "emoji": True
                        },
                        "optional": True,
                        "element": {
                            "type": "conversations_select",
                            # "type": "multi_conversations_select",
                            "placeholder": {
                                "type": "plain_text",
                                "text": ":mega: メンバーを追加するチャンネル選択",
                                "emoji": True
                            }
                        }
                    }, 
                    {
                        "type": "input",
                        "element": {
                            "type": "multi_users_select",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "選択してください",
                                "emoji": True
                            },
                            "action_id": "multi_users_select-action"
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "対象メンバー",
                            "emoji": True
                        }
                    },  
                ]
        client.views_update(
            # view_id を渡すこと
            view_id=body["view"]["id"],
            # 競合状態を防ぐためのビューの状態を示す文字列
            hash=body["view"]["hash"],
            # 更新後の blocks を含むビューのペイロード
            view=view
        )
    else:
        view["blocks"]=[
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": "This is a plain text section block.",
                    "emoji": True
                }
            }
            ]
        # 不正？不具合
        client.views_update(
        # view_id を渡すこと
        view_id=body["view"]["id"],
        # 競合状態を防ぐためのビューの状態を示す文字列
        hash=body["view"]["hash"],
        # 更新後の blocks を含むビューのペイロード
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

# 「送信」ボタンが押されたときに呼び出されます
@app.view("modal-id")
# @app.view({"type": "view_closed", "callback_id": "modal-id"})
def handle_view_submission(ack: Ack, view: dict, logger: logging.Logger):
    ack()
    # state.values.{block_id}.{action_id}
    logger.info(view["state"]["values"])


# アプリを起動
if __name__ == "__main__":
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN2")).start()

# 以下、参考コード
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

# view.callback_id にマッチング（この値で固定でいいのか？）
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