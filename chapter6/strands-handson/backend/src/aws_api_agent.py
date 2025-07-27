import asyncio, os
from typing import Optional, Dict, Any
from strands import Agent, tool
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters
from .agent_executor import invoke_agent

# エージェントの状態
_state: Dict[str, Any] = {"client": None, "queue": None}

def setup_api_agent(queue: Optional[asyncio.Queue]):
    """新規キューを受け取り、MCPクライアントを準備"""
    global _state
    _state["queue"] = queue
    if queue and not _state["client"]:
        try:
            _state["client"] = MCPClient(
                lambda: stdio_client(StdioServerParameters(
                    command="python",
                    args=["-m", "awslabs.aws_api_mcp_server.server"],
                    env=os.environ.copy()
                ))
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
async def aws_api_agent(query: str) -> str:
    """AWS APIエージェント"""
    if not _state["client"]:
        return "AWS API MCPクライアントが利用不可です"
    return await invoke_agent(
        "AWS API", query, _state["client"], _create_agent, _state["queue"]
    )