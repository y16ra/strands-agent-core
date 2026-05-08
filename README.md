# strands-agent-core

## 推奨ブラウザ

- 日本語 IME 入力時の `st.chat_input` の挙動差を避けるため、`Chrome` での利用を推奨します。
- `Safari` では日本語入力の確定 Enter が送信として扱われる場合があります。

## 会話履歴（AgentCore Memory）

- 会話履歴参照を有効化するには、`.env` で `AGENTCORE_MEMORY_ENABLED=true` かつ `AGENTCORE_MEMORY_ID` を設定してください。
- `AGENTCORE_MEMORY_ID` が未設定の場合、UI 上は会話できますが履歴参照は無効になります。
- サイドバーの「会話メモリ」表示で、有効/無効の状態を確認できます。
- 「会話リセット」を押すと表示メッセージを消去し、同時に新しい `session_id` を発行するため、過去会話の文脈を引き継ぎません。