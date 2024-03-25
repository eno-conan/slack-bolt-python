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
                    'type': 'section',
                    'block_id': 'operation',
                    'text': {
                        'type': 'mrkdwn',
                        'text': '操作を選択'
                    },
                    'accessory': {
                        'type': 'static_select',
                        'placeholder': {
                            'type': 'plain_text',
                            'text': '選択',
                        },
                        'options': [
                            {
                                'text': {
                                    'type': 'plain_text',
                                    'text': 'チャンネル新規作成',
                                },
                                'value': 'create-channel'
                            },
                            {
                                'text': {
                                    'type': 'plain_text',
                                    'text': 'メンバー追加',
                                },
                                'value': 'add-members'
                            },
                        ],
                        'action_id': 'static_select_action'
                    }
                }

# ユーザ複数選択のBLOCK
SELECT_MULTI_USER_BLOCK = {
                            'type': 'input',
                            'block_id': 'select-users',
                            'element': {
                                'type': 'multi_users_select',
                                'placeholder': {
                                    'type': 'plain_text',
                                    'text': 'Select users',
                                },
                                'action_id': 'select-users-action'
                            },
                            'label': {
                                'type': 'plain_text',
                                'text': '対象メンバー',
                            },
                            'optional': False,
                        }

# ボットトークンとソケットモードハンドラーを使ってアプリを初期化
app = App(token = os.environ.get('SLACK_BOT_TOKEN'), 
          signing_secret = os.environ.get("SLACK_SIGNING_SECRET")
          )

# 重複防止
@app.middleware
def skip_retry(logger, request, next):
    if "x-slack-retry-num" not in request.headers:
        next()

# ショートカットでモーダル起動
@app.shortcut('modal-shortcut')
def handle_shortcuts(ack: Ack, body: dict, client: WebClient):
    # 受信した旨をSlackサーバーに伝達
    ack()
    
    # モーダル生成
    client.views_open(
        trigger_id=body['trigger_id'],
        view = {
            'type': 'modal',
            'callback_id': 'modal-id',
            'title': {'type': 'plain_text', 'text': 'Slackチャンネル設定ツール'},
            'close': {'type': 'plain_text', 'text': '閉じる'},
            'blocks': [
                        SELECT_ACTION_DROPDOWN_BLOCK
                        ],
        },
    )

@app.action('static_select_action')
def update_modal(ack: Ack, body: dict, client: WebClient):
    # ボタンのリクエストを確認
    ack()
    
    view = {               
            'type': 'modal',
            'callback_id': 'modal-id',
            'title': {'type': 'plain_text', 'text':'Slackチャンネル設定ツール'},
            'submit': {'type': 'plain_text', 'text': '送信'},
            'close': {'type': 'plain_text', 'text': '閉じる'}
        }

    # ドロップダウンの入力値取得
    selected_operation = body['view']['state']['values']['operation'] \
        ['static_select_action']['selected_option']['value']
    
    if selected_operation == 'create-channel':
        view['blocks'] = [
            {
                'type': 'input',
                'block_id': 'create-channel',
                'element': {
                                'type': 'plain_text_input', 
                                'action_id': 'action-id',
                                'placeholder': {
                                    'type': 'plain_text',
                                    'text': 'チャンネル名入力',
                                }
                            },
                'label': {'type': 'plain_text', 'text': '新規チャンネル名'},
                'optional': False,
            },
            {
			"type": "context",
			"elements": [
				{
					"type": "plain_text",
					"text": "英字・記号について、英字は小文字、記号はハイフン・アンダースコアのみ使用可能",
					"emoji": True
				}
			]
		    },
            SELECT_MULTI_USER_BLOCK
                ]
        client.views_update(
            view_id=body['view']['id'],
            hash=body['view']['hash'],
            view=view
        )
    elif selected_operation == 'add-members':
        view['blocks'] = [
                    {
                        'type': 'input',
                        'label': {
                            'type': 'plain_text',
                            'text': '既存チャンネル名'
                            
                        },
                        'optional': False,
                        'block_id': 'select-channel',
                        'element': {
                            'type': 'conversations_select',
                            # 'type': 'multi_conversations_select',
                            'placeholder': {
                                'type': 'plain_text',
                                'text': ':mega: メンバー追加するチャンネル選択'
                            },
                            'action_id': 'conversations_select-action'
                        }
                    }, 
                    SELECT_MULTI_USER_BLOCK
                ]
        client.views_update(
            view_id=body['view']['id'],
            hash=body['view']['hash'],
            view=view
        )
    else:
        view['blocks']=[
            {
                'type': 'section',
                'text': {
                    'type': 'plain_text',
                    'text': 'This is a plain text section block.',
                }
            }
            ]
        client.views_update(
            view_id=body['view']['id'],
            hash=body['view']['hash'],  
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
@app.view('modal-id')
def handle_submission(ack: Ack, body, client, view: dict, logger:logging.Logger):
    # ユーザに表示する情報
    action = ''
    target_channel_name = ''
    errors = {}

    # 入力値の検証
    submitted_data = view['state']['values']
    if submitted_data.get('create-channel'): # チャンネル新規作成の場合
        action = ' チャンネル新規作成'
        input_channel_name = submitted_data['create-channel']['action-id']['value']
        
        # 入力されたチャンネル名の存在判定
        channels_name = slack_operations.fetch_conversations(client)
        for name in channels_name:
            if input_channel_name == name:
                errors['create-channel'] = '既に存在するチャンネル名です。'
                ack(response_action='errors', errors=errors)
                return
            
        # チャンネル重複なし、チャンネル作成
        channel = slack_operations.create_conversation(client=client,channel_name=input_channel_name)
        input_channel_id = channel['id']
        target_channel_name = channel['name']
    elif submitted_data.get('select-channel'): # チャンネルメンバー追加の場合
        action = 'チャンネルメンバー追加'
        input_channel_id = submitted_data['select-channel']['conversations_select-action']['selected_conversation']
        
        # チャンネル入力箇所にユーザが含まれる場合
        if input_channel_id.startswith('U'):
            errors['select-channel'] = 'チャンネルを選択してください。'
            ack(response_action='errors', errors=errors)
            return

        # チャンネルIDからチャンネル名取得
        channel = slack_operations.getting_conversation_info(client=client,channel_id=input_channel_id)
        target_channel_name = channel['name']
    
    users = submitted_data['select-users']['select-users-action']['selected_users']
    res = slack_operations.invite_users(client,channel_id=input_channel_id, invite_users_list=users)
    
    if res is None:
        errors['select-users'] = '参加メンバーのみ選択されています。'
        ack(response_action='errors', errors=errors)
        return

    # モーダルを閉じる
    ack()
    
    # ユーザーにメッセージを送信
    userId = body['user']['id']
    msg = f'<@{userId}>さんから申請がありました\n\n■申請内容:{action}\n\n■チャンネル名:{target_channel_name}'
    try:
        client.chat_postMessage(channel = os.environ.get('REQUEST_NOTIFY_CHANNEL','work'), text=msg)
    except Exception as e:
        logger.exception(f'Failed to post a message {e}')
        
@app.event('app_mention')
def handle_app_mention(body: dict, say, logger,client: WebClient):
    # メンションされたメッセージを取得

    mention = body['event']
    print(mention)
    # メンションされたメッセージを取得
    text = mention['text']
    thread_ts = mention['ts']
    
    slack_operations.fetch_conversations(client)
    # create_conversations(client)
    # invite_user(client)
    
    # 例: メンションされたメッセージをログに出力する
    logger.info(f'メンションされました: {text}')
    
    # 応答メッセージを送信（スレッドに送信）
    # https://zenn.dev/t_yng/scraps/8374a9616c235e
    say(f'{text}', thread_ts=thread_ts)

# アプリを起動
if __name__ == '__main__':
    SocketModeHandler(app, os.environ.get('SLACK_APP_TOKEN')).start()
    # app.start(port=int(os.environ.get("PORT", 8080)))

# 以下、念のため保存
# スラッシュコマンド
# @app.command('/modal-command')
# def handle_some_command(ack: Ack, body: dict, client: WebClient):
#     # 受信した旨を 3 秒以内に Slack サーバーに伝えます
#     ack()
#     # views.open という API を呼び出すことでモーダルを開きます
#     client.views_open(
#         # 上記で説明した trigger_id で、これは必須項目です
#         # この値は、一度のみ 3 秒以内に使うという制約があることに注意してください
#         trigger_id=body['trigger_id'],
#         # モーダルの内容を view オブジェクトで指定します
#         view={
#             # このタイプは常に 'modal'
#             'type': 'modal',
#             # このモーダルに自分で付けられる ID で、次に説明する @app.view リスナーはこの文字列を指定します
#             'callback_id': 'modal-id',
#             # これは省略できないため、必ず適切なテキストを指定してください
#             'title': {'type': 'plain_text', 'text': 'テストモーダル'},
#             # input ブロックを含まないモーダルの場合は view から削除することをおすすめします
#             # このコード例のように input ブロックがあるときは省略できません
#             'submit': {'type': 'plain_text', 'text': '送信'},
#             # 閉じるボタンのラベルを調整することができます（必須ではありません）
#             'close': {'type': 'plain_text', 'text': '閉じる'},
#             # Block Kit の仕様に準拠したブロックを配列で指定
#             # 見た目の調整は https://app.slack.com/block-kit-builder を使うと便利です
#             'blocks': [
#                 {
#                     # モーダルの通常の使い方では input ブロックを使います
#                     # ブロックの一覧はこちら: https://api.slack.com/reference/block-kit/blocks
#                     'type': 'input',
#                     # block_id / action_id を指定しない場合 Slack がランダムに指定します
#                     # この例のように明に指定することで、@app.view リスナー側での入力内容の取得で
#                     # ブロックの順序に依存しないようにすることをおすすめします
#                     'block_id': 'question-block',
#                     # ブロックエレメントの一覧は https://api.slack.com/reference/block-kit/block-elements
#                     # Works with block types で Input がないものは input ブロックに含めることはできません
#                     'element': {'type': 'plain_text_input', 'action_id': 'input-element'},
#                     # これはモーダル上での見た目を調整するものです
#                     # 同様に placeholder を指定することも可能です 
#                     'label': {'type': 'plain_text', 'text': '質問'},
#                 }
#             ],
#         },
#     )