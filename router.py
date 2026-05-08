from __future__ import annotations

import os

from strands import Agent
from strands.models import BedrockModel

from agents import AGENT_REGISTRY
from config.settings import load_settings


_MODE_TO_AGENT_KEY = {
    "リサーチ": "research",
    "コード": "code",
    "ドキュメント": "doc",
}


def _create_classifier_agent() -> Agent:
    settings = load_settings()
    if settings.aws_profile:
        os.environ["AWS_PROFILE"] = settings.aws_profile
    os.environ["AWS_REGION"] = settings.aws_region

    model = BedrockModel(model_id=settings.bedrock_model_id, streaming=False)
    return Agent(model=model)


def _classify_agent(message: str) -> str:
    classifier = _create_classifier_agent()
    prompt = (
        "次のユーザー入力を分類し、必ず research / code / doc のいずれか1語だけ返してください。\n"
        f"入力: {message}"
    )
    response_message = classifier(prompt).message
    if isinstance(response_message, str):
        result = response_message.strip().lower()
    elif isinstance(response_message, dict):
        # Strands may return structured content blocks.
        content = response_message.get("content", [])
        if isinstance(content, list):
            texts: list[str] = []
            for block in content:
                if isinstance(block, dict) and isinstance(block.get("text"), str):
                    texts.append(block["text"])
            result = " ".join(texts).strip().lower()
        else:
            result = str(response_message).strip().lower()
    else:
        result = str(response_message).strip().lower()

    if result in AGENT_REGISTRY:
        return result
    for key in AGENT_REGISTRY:
        if key in result:
            return key
    return "research"


def route(message: str, mode: str, session_id: str = "default-session") -> Agent:
    if mode == "自動":
        key = _classify_agent(message)
        return AGENT_REGISTRY[key](session_id)

    key = _MODE_TO_AGENT_KEY.get(mode, "research")
    return AGENT_REGISTRY[key](session_id)
