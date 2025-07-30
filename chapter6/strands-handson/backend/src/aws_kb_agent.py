import asyncio
from strands import Agent, tool
from strands.tools.mcp.mcp_client import MCPClient
from mcp.client.streamable_http import streamablehttp_client
from .agent_executor import invoke

# エージェントの状態を管理
class KbAgentState:
    def __init__(self):
        self.client = None
        self.queue = None

_state = KbAgentState()

def setup_kb_agent(queue):
    """新規キューを受け取り、MCPクライアントを準備"""
    _state.queue = queue
    if queue and not _state.client:
        try:
            _state.client = MCPClient(
                lambda: streamablehttp_client(
                    "https://knowledge-mcp.global.api.aws"
                )
            )
        except Exception:
            _state.client = None

def _create_agent():
    """サブエージェントを作成"""
    if not _state.client:
        return None
    return Agent(
        model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        tools=_state.client.list_tools_sync()
    )

@tool
async def aws_kb_agent(query):
    """AWSナレッジエージェント"""
    if not _state.client:
        return "AWSナレッジMCPクライアントが利用不可です"
    return await invoke(
        "AWSナレッジ", query, _state.client,
        _create_agent, _state.queue
    )