import json

from mcp.server.fastmcp import FastMCP

# In-memory mock store data
default_store = {
    "STORE1": {"user_cnt": 18, "manager_cnt": 2},
    "STORE2": {"user_cnt": 20, "manager_cnt": 0},
}

# Create MCP server
mcp = FastMCP("StoreManager")


# Tool: store use add
@mcp.tool()
def add_user(store_name: str, is_manager: bool) -> str:
    cnt_setting = default_store.get(store_name.upper())
    if cnt_setting:
        if is_manager:
            cnt_setting["manager_cnt"] += 1
        else:
            cnt_setting["user_cnt"] += 1
        return f"now {store_name} user {json.dumps(cnt_setting)}"
    return "store not found."


# Tool: store use leave
@mcp.tool()
def user_leave(store_name: str, is_manager: bool) -> str:
    cnt_setting = default_store.get(store_name.upper())
    if cnt_setting:
        if is_manager:
            cnt_setting["manager_cnt"] -= 1
        else:
            cnt_setting["user_cnt"] -= 1
        return f"now {store_name} user {json.dumps(cnt_setting)}"
    return "store not found."


# Tool: store info
@mcp.tool()
def store_info(store_name: str) -> str:
    if cnt_setting := default_store.get(store_name.upper()):
        return f"{store_name} user info {json.dumps(cnt_setting)}"
    return "store not found."


# Resource: Greeting
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}! this is store manage"


if __name__ == "__main__":
    mcp.run(transport="stdio")
