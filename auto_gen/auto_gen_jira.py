import asyncio
import os

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools

GIT_BASE_URL = "https://github.com/"
JIRA_ENV = {
    "CONFLUENCE_URL": "x",
    "CONFLUENCE_USERNAME": "x",
    "CONFLUENCE_API_TOKEN": "x",
    "JIRA_URL": "x",
    "JIRA_USERNAME": "x",
    "JIRA_API_TOKEN": "x",
}

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def get_gemini_client() -> OpenAIChatCompletionClient:
    return OpenAIChatCompletionClient(
        model="gemini-2.5-flash-preview-05-20",
        api_key=GEMINI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta",
        model_capabilities={
            "json_output": True,
            "vision": True,
            "function_calling": True,
            "structured_output": True,
        },
    )


JIRA_MCP = StdioServerParams(
    command="uvx",
    args=["mcp-atlassian"],
    env=JIRA_ENV,
    read_timeout_seconds=20,
)

GIT_MCP = StdioServerParams(
    command="uvx",
    args=["mcp-server-git"],
    read_timeout_seconds=20,
)


async def jira_agent() -> None:
    jira_tools = await mcp_server_tools(JIRA_MCP)
    agent = AssistantAgent(
        "local_assistant",
        system_message="""
                你是一個本地管理員，專注於處裡本地資訊
                遇到單號之類的關鍵字，會優先使用 jira_tools
                當結束查詢時請說 END
                """,
        model_client=get_gemini_client(),
        tools=jira_tools,
        model_client_stream=True,
    )
    termination = TextMentionTermination("END")
    team = RoundRobinGroupChat(
        [agent],
        termination_condition=termination,
    )
    await Console(team.run_stream(task="幫我閱讀單號 XXXXX"))


async def programmer_agent() -> None:
    git_tools = await mcp_server_tools(GIT_MCP)
    agent = AssistantAgent(
        "local_assistant",
        system_message=f"""
                你是一個專業的開發人員
                使用git開發會先預設使用 git_tools
                git的base網址 {GIT_BASE_URL}，當clone專案時，會顯示clone的絕對位置
                若對話無指定閱讀路徑或文件，會優先閱讀完整專案，學習專案結構，再進行需求修改
                """,
        model_client=get_gemini_client(),
        tools=git_tools,
        model_client_stream=True,
    )
    termination = TextMentionTermination("END")
    team = RoundRobinGroupChat(
        [agent],
        termination_condition=termination,
    )
    await Console(
        team.run_stream(
            task="幫我clone 專案 mop_message_center，並閱讀有專route的資料夾，幫我列出可用的API"
        )
    )


if __name__ == "__main__":
    asyncio.run(programmer_agent())
