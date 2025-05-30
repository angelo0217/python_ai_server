import asyncio
import os

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools

X_API_KEY = os.getenv("X_API_KEY")


def get_ai_client() -> OpenAIChatCompletionClient:  # type: ignore
    # "Mimic OpenAI API using Local LLM Server."
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
    # return OpenAIChatCompletionClient(
    #     model="llama3.2:latest",
    #     api_key="ollama",
    #     base_url="http://localhost:11434/v1",
    #     model_capabilities={
    #         "json_output": False,
    #         "vision": False,
    #         "function_calling": True,
    #     },
    # )


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
    args=["@dillip285/mcp-terminal", "--allowed-paths", "D:\\"],
    # args=["-y", "@simonb97/server-win-cli"],
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
                ## 角色與行為：
                你是一位專業的資深軟體開發人員，擅長使用中文進行交流和解釋。
                你的主要工作目錄是 D:\opt。
                你將通過 **輸出特定JSON格式的指令** 來間接操作工具 (尤其是 Git) 以完成任務。
                git 基礎位置在 {GIT_BASE_URL}
                """
        +
                """
                ## 工作行為：
                會看目前有哪些工具可以達到需求，並操作工具去執行
                
                ## 結束工作行為
                會告知git clone位置的絕對路徑
                會給出 END 字眼來做結束
                """,
        model_client=get_ai_client(),
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
            task="""
            幫我執行
            1、clone 專案 python_mcp_server
            2、新建一個 release/demo的分支
            3、在新的分支上新建一個簡單的demo.json範例，內容隨意
            4、然後發布pull request 回 main
            5、給我 pull request 位置
            """
        )
    )


if __name__ == "__main__":
    asyncio.run(programmer_agent())
