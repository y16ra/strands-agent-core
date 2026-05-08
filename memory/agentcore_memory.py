from __future__ import annotations

import logging

from botocore.exceptions import BotoCoreError, ClientError
from strands.types.tools import AgentTool
from strands_tools.agent_core_memory import AgentCoreMemoryToolProvider

from config.settings import load_settings


logger = logging.getLogger(__name__)


def get_memory_tools(session_id: str) -> list[AgentTool]:
    settings = load_settings()
    if not settings.agentcore_memory_enabled:
        logger.info("AgentCore memory is disabled by AGENTCORE_MEMORY_ENABLED=false.")
        return []
    if not settings.agentcore_memory_id:
        logger.warning(
            "AgentCore memory is enabled but AGENTCORE_MEMORY_ID is empty. "
            "Conversation history will not be available."
        )
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
