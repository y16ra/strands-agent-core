from __future__ import annotations

import logging

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from strands.tools import tool

from config.settings import load_settings


logger = logging.getLogger(__name__)


@tool
def kb_search(query: str) -> str:
    """Search Bedrock Knowledge Base and return top 3 snippets."""
    settings = load_settings()
    if not settings.knowledge_base_id:
        return ""

    try:
        client = boto3.client("bedrock-agent-runtime", region_name=settings.aws_region)
        response = client.retrieve(
            knowledgeBaseId=settings.knowledge_base_id,
            retrievalQuery={"text": query},
            retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": 3}},
        )
        results = response.get("retrievalResults", [])
        snippets: list[str] = []
        for item in results[:3]:
            text = item.get("content", {}).get("text", "").strip()
            if text:
                snippets.append(text)
        return "\n\n---\n\n".join(snippets)
    except (ClientError, BotoCoreError) as exc:
        logger.exception("Knowledge Base retrieval failed: %s", exc)
        return ""
