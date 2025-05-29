import asyncio
import os

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools

X_API_KEY = os.getenv("X_API_KEY")


def get_xai_client() -> OpenAIChatCompletionClient:  # type: ignore
    "Mimic OpenAI API using Local LLM Server."
    return OpenAIChatCompletionClient(
        model="grok-3-beta",
        api_key=X_API_KEY,
        base_url="https://api.x.ai/v1",
        model_capabilities={
            "json_output": True,
            "vision": True,
            "function_calling": True,
            "structured_output": True,  # Added missing field
        },
    )


GIT_BASE_URL = "https://github.com/angelo0217"
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

TERMINAL_MCP = StdioServerParams(
    command="npx",
    args=["@dillip285/mcp-terminal", "--allowed-paths", "/d"],
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
    terminal_tools = await mcp_server_tools(TERMINAL_MCP)

    tools = git_tools + terminal_tools
    agent = AssistantAgent(
        "local_assistant",
        system_message=f"""
                你是一個專業的開發人員。
                專案操作位置 D:\\
                使用git開發會先預設使用 git_tools 若失敗則用 terminal_tools。
                git的base網址 {GIT_BASE_URL}，當clone專案時，並且會組合git的base網址 + 專案名稱去clone，會顯示clone的絕對位置。
                **請注意：當要求clone專案時，必須提供專案的完整Git URL。如果缺少此資訊，我將無法執行操作並會要求你提供。**
                若對話無指定閱讀路徑或文件，會優先閱讀完整專案，學習專案結構，再進行需求修改。
                
                所有活動結束時或告一段落，就會給我 END 的結語
                """,
        model_client=get_xai_client(),
        tools=tools,
        model_client_stream=True,
    )
    termination = TextMentionTermination("END")
    team = RoundRobinGroupChat(
        [agent],
        termination_condition=termination,
    )
    await Console(
        team.run_stream(
            task="幫我clone 專案 python_mcp_server，新建一個 release/demo的分支，在新的分支上新建一個簡單的demo.json範例，內容隨意，然後發布pull request 回 main,給我 pull request 位置"
        )
    )


if __name__ == "__main__":
    asyncio.run(programmer_agent())
