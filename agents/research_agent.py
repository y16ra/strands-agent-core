from __future__ import annotations

import sys
from pathlib import Path

from strands import Agent
from strands.models import BedrockModel

if str(Path(__file__).resolve().parents[1]) not in sys.path:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from config.settings import load_settings
from memory.agentcore_memory import get_memory_tools
from tools.kb_search import kb_search
from tools.web_search import web_search


def create_research_agent(session_id: str = "default-session") -> Agent:
    settings = load_settings()
    memory_tools = get_memory_tools(session_id)
    return Agent(
        model=BedrockModel(model_id=settings.bedrock_model_id, streaming=True),
        system_prompt=(
            "あなたはリサーチエージェントです。事実ベースで情報を整理し、"
            "見出し付きのMarkdownで要約してください。必要に応じてkb_searchを使ってください。"
        ),
        tools=[web_search, kb_search, *memory_tools],
    )


if __name__ == "__main__":
    agent = create_research_agent()
    result = agent("AIエージェント開発の最近のトレンドを3点で教えてください。")
    print(result.message)
