import asyncio
from strands import Agent, tool
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters
from .agent_executor import invoke

# エージェントの状態を管理
class StrandsMasterState:
    def __init__(self):
        self.client = None
        self.queue = None

_state = StrandsMasterState()

def setup_strands_master(queue):
    """新規キューを受け取り、MCPクライアントを準備"""
    _state.queue = queue
    if queue and not _state.client:
        try:
            _state.client = MCPClient(
                lambda: stdio_client(StdioServerParameters(
                    command="uvx", args=["strands-agents-mcp-server"]
                ))
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
async def strands_master(query):
    """Strandsマスターエージェント"""
    if not _state.client:
        return "StrandsマスターMCPクライアントが利用不可です"
    return await invoke(
        "Strandsマスター", query, _state.client,
        _create_agent, _state.queue
    )