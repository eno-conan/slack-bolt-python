# Slackチャンネル設定

### 起動前の確認
##### ローカルから動かす場合
- SocketModeがonであることを確認
  - https://app.slack.com/app-settings/T027R1Z6T1A/A06QVGGE360/socket-mode
##### CloudRunで動かす場合
- SocketModeがoffであることを確認（必ずoffにしないといけない？）

### Slack API
- メンバー招待(conversations_invite)
  - 参加済のメンバーを含めた場合、以下のレスポンスを取得するが、処理自体は完結するみたい（errorsキーの情報参照）
    ```
    {'ok': True, 'channel': {'id': 'C06QD36AEUA', 'name': 'work', 'is_channel': True, 'is_group': False, 'is_im': False, 'is_mpim': False, 'is_private': False, 'created': 1710897662, 'is_archived': False, 'is_general': False, 'unlinked': 0, 'name_normalized': 'work', 'is_shared': False, 'is_org_shared': False, 'is_pending_ext_shared': False, 'pending_shared': [], 'context_team_id': 'T027R1Z6T1A', 'updated': 1710897662953, 'parent_conversation': None, 'creator': 'U027K20TC91', 'is_ext_shared': False, 'shared_team_ids': ['T027R1Z6T1A'], 'pending_connected_team_ids': [], 'is_member': True, 'last_read': '1711066830.235299', 'topic': {'value': '', 'creator': '', 'last_set': 0}, 'purpose': {'value': '', 'creator': '', 'last_set': 0}, 'previous_names': []}, 'errors': [{'user': 'U027K20TC91', 'ok': False, 'error': 'already_in_channel'}]}
    ```
  - 参加しているメンバーしかいない場合
    ```
    {'ok': False, 'error': 'already_in_channel', 'errors': [{'user': 'U027K20TC91', 'ok': False, 'error': 'already_in_channel'}]}
    ```

- チャンネル作成
  - [チャンネル名の命名規則](https://api.slack.com/methods/conversations.create#naming)
  ```
  Channel names may only contain lowercase letters, numbers, hyphens, and underscores, and must be 80 characters or less. When calling this method, we recommend storing both the channel's id and name value that returned in the response.
  ```