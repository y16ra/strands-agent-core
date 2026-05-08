from __future__ import annotations

import sys
from pathlib import Path

from strands import Agent
from strands.models import BedrockModel

if str(Path(__file__).resolve().parents[1]) not in sys.path:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from config.settings import load_settings
from memory.agentcore_memory import get_memory_tools
from tools.file_tools import write_markdown
from tools.kb_search import kb_search


def create_doc_agent(session_id: str = "default-session") -> Agent:
    settings = load_settings()
    memory_tools = get_memory_tools(session_id)
    return Agent(
        model=BedrockModel(model_id=settings.bedrock_model_id, streaming=True),
        system_prompt=(
            "あなたはドキュメントエージェントです。読みやすいMarkdownで"
            "文書作成や要約を行ってください。必要に応じてkb_searchを使ってください。"
        ),
        tools=[kb_search, write_markdown, *memory_tools],
    )


if __name__ == "__main__":
    agent = create_doc_agent()
    result = agent("API設計レビュー用のチェックリストをMarkdownで作ってください。")
    print(result.message)
