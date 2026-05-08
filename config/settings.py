from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    aws_region: str
    aws_profile: str
    bedrock_model_id: str
    knowledge_base_id: str
    tavily_api_key: str
    brave_api_key: str
    agentcore_memory_enabled: bool
    agentcore_memory_id: str
    agentcore_actor_id: str
    agentcore_namespace: str


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        aws_region=os.getenv("AWS_REGION", "ap-northeast-1"),
        aws_profile=os.getenv("AWS_PROFILE", "default"),
        bedrock_model_id=os.getenv(
            "BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0"
        ),
        knowledge_base_id=os.getenv("KNOWLEDGE_BASE_ID", ""),
        tavily_api_key=os.getenv("TAVILY_API_KEY", ""),
        brave_api_key=os.getenv("BRAVE_API_KEY", ""),
        agentcore_memory_enabled=os.getenv("AGENTCORE_MEMORY_ENABLED", "true").lower()
        == "true",
        agentcore_memory_id=os.getenv("AGENTCORE_MEMORY_ID", ""),
        agentcore_actor_id=os.getenv("AGENTCORE_ACTOR_ID", "local-user"),
        agentcore_namespace=os.getenv("AGENTCORE_NAMESPACE", "default"),
    )
