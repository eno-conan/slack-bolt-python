# https://slack.dev/bolt-python/ja-jp/concepts#steps
# ちょっと保留？
import os
from slack_bolt import App
from slack_bolt.workflows.step import WorkflowStep
from dotenv import load_dotenv
load_dotenv()

# いつも通りBolt アプリを起動する
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

def edit(ack, step, configure):
    ack()

    blocks = [
        {
            "type": "input",
            "block_id": "task_name_input",
            "element": {
                "type": "plain_text_input",
                "action_id": "name",
                "placeholder": {"type": "plain_text", "text":"Add a task name"},
            },
            "label": {"type": "plain_text", "text":"Task name"},
        },
        {
            "type": "input",
            "block_id": "task_description_input",
            "element": {
                "type": "plain_text_input",
                "action_id": "description",
                "placeholder": {"type": "plain_text", "text":"Add a task description"},
            },
            "label": {"type": "plain_text", "text":"Task description"},
        },
    ]
    configure(blocks=blocks)

def save(ack, view, update):
    ack()

    values = view["state"]["values"]
    task_name = values["task_name_input"]["name"]
    task_description = values["task_description_input"]["description"]

    inputs = {
        "task_name": {"value": task_name["value"]},
        "task_description": {"value": task_description["value"]}
    }
    outputs = [
        {
            "type": "text",
            "name": "task_name",
            "label":"Task name",
        },
        {
            "type": "text",
            "name": "task_description",
            "label":"Task description",
        }
    ]
    update(inputs=inputs, outputs=outputs)

def execute(step, complete, fail):
    inputs = step["inputs"]
    # すべての処理が成功した場合
    outputs = {
        "task_name": inputs["task_name"]["value"],
        "task_description": inputs["task_description"]["value"],
    }
    complete(outputs=outputs)

    # 失敗した処理がある場合
    error = {"message":"Just testing step failure!"}
    fail(error=error)

# WorkflowStep の新しいインスタンスを作成する
ws = WorkflowStep(
    callback_id="add_task",
    edit=edit,
    save=save,
    execute=execute,
)
# ワークフローステップを渡してリスナーを設定する
app.step(ws)