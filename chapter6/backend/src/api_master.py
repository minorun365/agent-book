import os, asyncio
from strands import Agent, tool
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters
from .agent_executor import invoke

# エージェントの状態を管理
class ApiMasterState:
    def __init__(self):
        self.client = None
        self.queue = None

_state = ApiMasterState()

def setup_api_master(queue):
    """新規キューを受け取り、MCPクライアントを準備"""
    _state.queue = queue
    if queue and not _state.client:
        try:
            _state.client = MCPClient(
                lambda: stdio_client(StdioServerParameters(
                    command="uvx",
                    args=["awslabs.aws-api-mcp-server"],
                    env=os.environ.copy()
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
async def api_master(query):
    """APIマスターエージェント"""
    if not _state.client:
        return "MCPクライアントが利用不可です"
    return await invoke(
        "APIマスター", query, _state.client,
        _create_agent, _state.queue
    )