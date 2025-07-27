import asyncio
from typing import Optional, Dict, Any
from strands import Agent, tool
from strands.tools.mcp.mcp_client import MCPClient
from mcp.client.streamable_http import streamablehttp_client
from .agent_executor import invoke_agent

# エージェントの状態
_state: Dict[str, Any] = {"client": None, "queue": None}

def setup_kb_agent(queue: Optional[asyncio.Queue]):
    """新規キューを受け取り、MCPクライアントを準備"""
    global _state
    _state["queue"] = queue
    if queue and not _state["client"]:
        try:
            _state["client"] = MCPClient(
                lambda: streamablehttp_client("https://knowledge-mcp.global.api.aws")
            )
        except Exception:
            _state["client"] = None

def _create_agent():
    """サブエージェントを作成"""
    if not _state["client"]:
        return None
    return Agent(
        model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        tools=_state["client"].list_tools_sync()
    )

@tool
async def aws_kb_agent(query: str) -> str:
    """AWSナレッジエージェント"""
    if not _state["client"]:
        return "AWSナレッジMCPクライアントが利用不可です"
    return await invoke_agent("AWSナレッジ", query, _state["client"], _create_agent, _state["queue"])