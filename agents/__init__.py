from agents.code_agent import create_code_agent
from agents.doc_agent import create_doc_agent
from agents.research_agent import create_research_agent

AGENT_REGISTRY = {
    "research": create_research_agent,
    "code": create_code_agent,
    "doc": create_doc_agent,
}
