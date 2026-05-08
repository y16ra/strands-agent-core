# strands-agent-core

## 推奨ブラウザ

- 日本語 IME 入力時の `st.chat_input` の挙動差を避けるため、`Chrome` での利用を推奨します。
- `Safari` では日本語入力の確定 Enter が送信として扱われる場合があります。

## 会話履歴（AgentCore Memory）

- 会話履歴参照を有効化するには、`.env` で `AGENTCORE_MEMORY_ENABLED=true` かつ `AGENTCORE_MEMORY_ID` を設定してください。
- `AGENTCORE_MEMORY_ID` が未設定の場合、UI 上は会話できますが履歴参照は無効になります。
- サイドバーの「会話メモリ」表示で、有効/無効の状態を確認できます。
- 「会話リセット」を押すと表示メッセージを消去し、同時に新しい `session_id` を発行するため、過去会話の文脈を引き継ぎません。

## Knowledge Base（Bedrock）

### 有効化に必要な設定

`.env` に以下を設定してください。

- `AWS_REGION`（例: `ap-northeast-1`）
- `AWS_PROFILE`（ローカルで利用するAWSプロファイル）
- `KNOWLEDGE_BASE_ID`（例: `J4VRNU38PF`）

`KNOWLEDGE_BASE_ID` が空の場合、`kb_search` は空文字を返し、ナレッジベース検索は無効になります。

### 動作確認

1. AWS認証確認

```bash
aws sts get-caller-identity
```

2. KBが参照可能か確認

```bash
aws bedrock-agent get-knowledge-base --knowledge-base-id <YOUR_KB_ID>
```

3. Retrieve API確認（KB検索）

```bash
aws bedrock-agent-runtime retrieve \
  --knowledge-base-id <YOUR_KB_ID> \
  --retrieval-query '{"text":"テストクエリ"}' \
  --retrieval-configuration '{"vectorSearchConfiguration":{"numberOfResults":3}}'
```

### よくあるエラー

- `ValidationException: The provided model identifier is invalid`
  - `BEDROCK_MODEL_ID` がリージョンに合っていない可能性があります。
  - `ap-northeast-1` では `us.*` ではなく、推論プロファイルID（`apac.*` / `jp.*` / `global.*`）を使う必要がある場合があります。
  - 例: `BEDROCK_MODEL_ID=apac.anthropic.claude-sonnet-4-20250514-v1:0`

- `AccessDeniedException`
  - 実行主体（`AWS_PROFILE` のIAMユーザー/ロール）に `bedrock-agent-runtime:Retrieve` など必要権限が不足しています。

- `ResourceNotFoundException`
  - `KNOWLEDGE_BASE_ID` の誤り、または `AWS_REGION` とKB作成リージョンの不一致が考えられます。