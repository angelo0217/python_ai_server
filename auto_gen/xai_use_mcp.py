import asyncio
import os

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams, SseServerParams, mcp_server_tools

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
        },
    )


async def main():
    model_client = get_xai_client()
    server_params = StdioServerParams(
        command="python",
        args=["store_count_mcp.py"],
        read_timeout_seconds=10,
    )
    # server_params = StdioServerParams(
    #     command="mcp-proxy",
    #     args=["http://localhost:8082/sse"],
    #     read_timeout_seconds=10,
    # )
    db_params = SseServerParams(
        url="http://localhost:8082/sse", headers={}
    )

    try:
        store_tools = await mcp_server_tools(server_params)
        db_tools = await mcp_server_tools(db_params)

        tools = store_tools + db_tools
        async with McpWorkbench(server_params) as mcp:
            agent = AssistantAgent(
                "local_assistant",
                system_message="""
                你是一個本地管理員，專注於處裡本地資訊，當結束查詢時請說 END
                """,
                model_client=model_client,
                # workbench=mcp, # use StdioServerParams need setting this
                tools=tools, # use SseServerParams need setting this
                model_client_stream=True,
            )

            termination = TextMentionTermination("END")
            team = RoundRobinGroupChat(
                [agent],
                termination_condition=termination,
            )
            # await Console(team.run_stream(task="目前有哪些表格能使用"))
            await Console(team.run_stream(task="STORE1 有幾人, 又有哪些db能用，再給我一個sqlalchemy的範例"))
    except Exception as ex:
        print(ex)
    finally:
        # 关闭模型客户端资源
        await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())
