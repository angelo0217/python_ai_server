1.  **下載 `get-pip.py`：**
    你可以使用 `curl` 或 `wget` 從官方來源下載 `get-pip.py`。

    ```bash
    curl -O [https://bootstrap.pypa.io/get-pip.py](https://bootstrap.pypa.io/get-pip.py)
    # 或
    wget [https://bootstrap.pypa.io/get-pip.py](https://bootstrap.pypa.io/get-pip.py)
    ```

2.  **使用 `uv` 執行 `get-pip.py`：**
    切換到你下載 `get-pip.py` 的目錄，然後執行以下命令：

    ```bash
    uv run python get-pip.py
    ```

    這個命令會指示 `uv` 使用 Python 解釋器來執行 `get-pip.py` 腳本，從而下載並安裝 `pip` 及其相關依賴（如 `setuptools` 和 `wheel`）。

3.  **安裝 mcp[cli]：**
    ```bash
    pip install mcp[cli]
    ```

4.  **使用 uv 執行 mcp 安裝 sotre_count_mcp.py：**
    ```bash
    uv run mcp install sotre_count_mcp.py
    ```
    這會自動安裝到有 mcp 設定的地方。

5.  ** mcp inspector 可測試 **
    ```
    npx @modelcontextprotocol/inspector
    ```