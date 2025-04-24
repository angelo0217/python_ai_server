from typing import Any, List, Dict, Optional, Union
import asyncio
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server import Server
import uvicorn
import sqlite3
import aiosqlite
import json
import os
from datetime import datetime
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

# 初始化 FastMCP 伺服器，命名為 "sql_operator"
mcp = FastMCP("sql_operator")

# 常數
DB_PATH = "database.sqlite"  # 資料庫路徑


async def execute_query(
    query: str, params: Optional[Union[List, Dict]] = None
) -> List[Dict[str, Any]]:
    """執行 SQL 查詢並返回結果。"""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, params or [])

            if query.strip().upper().startswith(("SELECT", "PRAGMA")):
                rows = await cursor.fetchall()
                result = [dict(row) for row in rows]
                return result
            else:
                await db.commit()
                return [{"affected_rows": cursor.rowcount, "last_row_id": cursor.lastrowid}]
    except aiosqlite.Error as e:
        print(f"SQL 錯誤：{e}")
        return [{"error": str(e)}]
    except Exception as e:
        print(f"發生未預期的錯誤：{e}")
        return [{"error": str(e)}]


def init_database() -> None:
    """初始化資料庫，如果資料表不存在則創建。"""
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 建立一個測試資料表
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            age INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        )

        # 插入一些測試資料
        test_data = [
            ("張三", "zhang@example.com", 30),
            ("李四", "li@example.com", 25),
            ("王五", "wang@example.com", 35),
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO users (name, email, age) VALUES (?, ?, ?)", test_data
        )

        conn.commit()
        conn.close()
        print("資料庫已初始化")


def format_result(result: List[Dict[str, Any]]) -> str:
    """格式化查詢結果為可讀字串。"""
    if not result:
        return "查詢完成，沒有返回資料。"

    if "error" in result[0]:
        return f"錯誤：{result[0]['error']}"

    if "affected_rows" in result[0]:
        return f"執行成功！影響的行數：{result[0]['affected_rows']}，最後插入的ID：{result[0]['last_row_id']}"

    # 將結果格式化為表格形式的字串
    headers = result[0].keys()
    rows = [[str(row.get(header, "")) for header in headers] for row in result]

    # 計算每列的最大寬度
    widths = [
        max(len(header), max([len(row[i]) for row in rows])) for i, header in enumerate(headers)
    ]

    # 創建分隔線
    separator = "+" + "+".join("-" * (width + 2) for width in widths) + "+"

    # 創建表頭
    header_str = "|" + "|".join(f" {h:<{widths[i]}} " for i, h in enumerate(headers)) + "|"

    # 創建資料行
    data_rows = []
    for row in rows:
        data_rows.append(
            "|" + "|".join(f" {cell:<{widths[i]}} " for i, cell in enumerate(row)) + "|"
        )

    # 組合表格
    table = [separator, header_str, separator] + data_rows + [separator]

    return f"查詢結果 ({len(result)} 筆資料)：\n" + "\n".join(table)


@mcp.tool()
async def execute_sql(query: str) -> str:
    """執行 SQL 查詢。

    Args:
        query: SQL 查詢語句。
    """
    result = await execute_query(query)
    return format_result(result)


@mcp.tool()
async def get_table_structure(table_name: str) -> str:
    """取得指定資料表的結構。

    Args:
        table_name: 資料表名稱。
    """
    query = f"PRAGMA table_info({table_name})"
    result = await execute_query(query)
    return format_result(result)


@mcp.tool()
async def list_tables() -> str:
    """列出資料庫中的所有資料表。"""
    query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    result = await execute_query(query)
    return format_result(result)


@mcp.tool()
async def insert_data(table_name: str, data_json: str) -> str:
    """插入資料到指定的資料表。

    Args:
        table_name: 資料表名稱。
        data_json: 要插入的資料，格式為 JSON 字串。例如：{"name": "張三", "email": "zhang@example.com", "age": 30}
    """
    try:
        data = json.loads(data_json)
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        values = list(data.values())

        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        result = await execute_query(query, values)
        return format_result(result)
    except json.JSONDecodeError:
        return "錯誤：提供的 JSON 格式不正確"
    except Exception as e:
        return f"錯誤：{e}"


@mcp.tool()
async def update_data(table_name: str, data_json: str, condition: str) -> str:
    """更新指定資料表中的資料。

    Args:
        table_name: 資料表名稱。
        data_json: 要更新的資料，格式為 JSON 字串。例如：{"name": "新名字", "age": 31}
        condition: 更新條件（WHERE 子句），例如："id = 1"
    """
    try:
        data = json.loads(data_json)
        set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
        values = list(data.values())

        query = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
        result = await execute_query(query, values)
        return format_result(result)
    except json.JSONDecodeError:
        return "錯誤：提供的 JSON 格式不正確"
    except Exception as e:
        return f"錯誤：{e}"


@mcp.tool()
async def delete_data(table_name: str, condition: str) -> str:
    """從指定資料表中刪除資料。

    Args:
        table_name: 資料表名稱。
        condition: 刪除條件（WHERE 子句），例如："id = 1"。留空刪除所有資料（小心使用！）
    """
    query = f"DELETE FROM {table_name}"
    if condition.strip():
        query += f" WHERE {condition}"

    result = await execute_query(query)
    return format_result(result)


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """建立一個 Starlette 應用程式，用於提供 MCP 伺服器的 SSE 介面。"""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send,  # noqa: SLF001
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
        middleware=middleware,
    )


if __name__ == "__main__":
    mcp_server = mcp._mcp_server

    import argparse

    parser = argparse.ArgumentParser(description="運行基於 SSE 的 MCP SQL 伺服器")
    parser.add_argument("--host", default="0.0.0.0", help="綁定的 Host")
    parser.add_argument("--port", type=int, default=8082, help="監聽的 Port")
    parser.add_argument("--db", default=DB_PATH, help="資料庫路徑")
    args = parser.parse_args()

    # 設定資料庫路徑
    DB_PATH = args.db

    # 初始化資料庫
    init_database()

    print(f"SQL MCP 伺服器啟動中，資料庫路徑：{DB_PATH}")
    print(f"訪問地址：http://{args.host}:{args.port}/sse")

    # 綁定 SSE 請求處理到 MCP 伺服器
    starlette_app = create_starlette_app(mcp_server, debug=True)

    uvicorn.run(starlette_app, host=args.host, port=args.port)
