from __future__ import annotations

import logging

from botocore.exceptions import BotoCoreError, ClientError
from strands.types.tools import AgentTool
from strands_tools.agent_core_memory import AgentCoreMemoryToolProvider

from config.settings import load_settings


logger = logging.getLogger(__name__)


def get_memory_tools(session_id: str) -> list[AgentTool]:
    settings = load_settings()
    if not settings.agentcore_memory_enabled or not settings.agentcore_memory_id:
        return []
    try:
        provider = AgentCoreMemoryToolProvider(
            memory_id=settings.agentcore_memory_id,
            actor_id=settings.agentcore_actor_id,
            session_id=session_id,
            namespace=settings.agentcore_namespace,
            region=settings.aws_region,
        )
        return provider.tools
    except (ClientError, BotoCoreError, ValueError) as exc:
        logger.exception("AgentCore memory provider init failed: %s", exc)
        return []
