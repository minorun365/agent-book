import asyncio, os
from strands import Agent, tool
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters
from .agent_executor import invoke

# エージェントの状態を管理
class ApiAgentState:
    def __init__(self):
        self.client = None
        self.queue = None

_state = ApiAgentState()
MCP_MODULE = "awslabs.aws_api_mcp_server.server"

def setup_api_agent(queue):
    """新規キューを受け取り、MCPクライアントを準備"""
    _state.queue = queue
    if queue and not _state.client:
        try:
            env = os.environ.copy()
            env["READ_OPERATIONS_ONLY"] = "true"
            _state.client = MCPClient(
                lambda: stdio_client(StdioServerParameters(
                    command="python",
                    args=["-m", MCP_MODULE], env=env
                ))
            )
        except Exception:
            _state.client = None

def _create_agent():
    """サブエージェントを作成"""
    if not _state.client:
        return None
    return Agent(
        model="anthropic.claude-sonnet-4-20250514-v1:0",
        tools=_state.client.list_tools_sync()
    )

@tool
async def aws_api_agent(query):
    """AWS APIエージェント"""
    if not _state.client:
        return "AWS API MCPクライアントが利用不可です"
    return await invoke(
        "AWS API", query, _state.client,
        _create_agent, _state.queue
    )