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
    """
    Adds a new user or manager to a specified store and returns the updated counts.
    If the store is not found, an error will be returned.

    :param store_name: The name of the store (e.g., "STORE1", "STORE2").
    :param is_manager: True if adding a manager, False if adding a regular user.
    :return: A JSON string of the updated store counts.
    :raises RpcError: If the store name is not found.
    """
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
    """
    Removes a user or manager from a specified store and returns the updated counts.
    Counts will not go below zero. If the store is not found, an error will be returned.

    :param store_name: The name of the store (e.g., "STORE1", "STORE2").
    :param is_manager: True if removing a manager, False if removing a regular user.
    :return: A JSON string of the updated store counts.
    :raises RpcError: If the store name is not found.
    """
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
def get_store_info(store_name: str) -> str:
    """
    Retrieves the current user and manager counts for a specified store.
    If the store is not found, an error will be returned.

    :param store_name: The name of the store (e.g., "STORE1", "STORE2").
    :return: A JSON string detailing the store's user and manager counts.
    :raises RpcError: If the store name is not found.
    """
    if cnt_setting := default_store.get(store_name.upper()):
        return f"{store_name} user info {json.dumps(cnt_setting)}"
    return "store not found."


# Resource: Greeting
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """
    Provides a personalized greeting message from the StoreManagerService.

    :param name: The name of the person to greet.
    :return: A personalized greeting string.
    """
    logger.info(f"Received greeting request for {name}")
    return f"Hello, {name}! This is the Store Manager Service."


if __name__ == "__main__":
    mcp.run(transport="stdio")
