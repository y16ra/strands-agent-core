from __future__ import annotations

import sys
from pathlib import Path

from strands import Agent
from strands.models import BedrockModel

if str(Path(__file__).resolve().parents[1]) not in sys.path:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from config.settings import load_settings
from memory.agentcore_memory import get_memory_tools
from tools.file_tools import get_git_diff, list_changed_files, read_file


def create_code_agent(session_id: str = "default-session") -> Agent:
    settings = load_settings()
    memory_tools = get_memory_tools(session_id)
    return Agent(
        model=BedrockModel(model_id=settings.bedrock_model_id, streaming=True),
        system_prompt=(
            "あなたはコードエージェントです。コード生成・レビュー・デバッグ支援を行い、"
            "必要に応じてMarkdownコードブロックで回答してください。"
            "コードレビュー依頼を受けたとき、ファイルパス指定がない場合は "
            "list_changed_files/get_git_diff を使って差分を自動取得してレビューしてください。"
            "レビュー結果は重大度順に、バグ・リスク・回帰を優先して報告してください。"
        ),
        tools=[read_file, list_changed_files, get_git_diff, *memory_tools],
    )


if __name__ == "__main__":
    agent = create_code_agent()
    result = agent("PythonでFibonacciを返す関数を書いて解説してください。")
    print(result.message)
