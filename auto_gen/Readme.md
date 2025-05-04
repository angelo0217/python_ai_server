# AutoGen 工具集

這個目錄包含基於 Microsoft AutoGen 框架的各種自動化生成與代碼審查工具。AutoGen 是一個用於建構和使用多智能體工作流程的框架，使得 AI 助手能夠互相協作完成各種任務。

## 安裝依賴

### 1. 安裝 AutoGen 相關套件

```shell
uv add autogen-agentchat autogen-ext[openai,magentic-one,azure] litellm[proxy] nest_asyncio pyngrok yfinance google-search-results rich autogenstudio
```

或者使用 pip：

```shell
pip install autogen-agentchat autogen-ext[openai,magentic-one,azure] litellm[proxy] nest_asyncio pyngrok yfinance google-search-results rich autogenstudio
```

### 2. 安裝 Ollama (用於本地模型)

```shell
ollama pull deepseek-r1
```

更多 ollama 模型可以在 [ollama.com](https://ollama.com/library) 查看。

## 功能模組

本目錄包含以下主要工具：

### 1. 代碼審查自動生成 (`code_review_auto_gen.py`)

這個腳本使用 AutoGen 框架建立了一個代碼審查系統，由程式開發者和代碼審查專家組成的團隊共同合作，生成代碼並進行審查。

#### 功能特點

- 自動從任務描述生成完整的代碼實現
- 代碼審查專家對生成的代碼進行審查與反饋
- 可以生成整個前後端專案的結構和代碼文件
- 自動整理輸出結果並保存為標準的專案結構
- 支持多種模型，包括 X.AI 的 Grok 模型

#### 使用方法

```shell
python auto_gen/code_review_auto_gen.py --task "你的任務描述" --output "結果輸出目錄"
```

例如：

```shell
python auto_gen/code_review_auto_gen.py --task "幫我生成一個前後端的平台，前端用簡單的html即可，呼叫後端使用python fastapi 撰寫一個簡單的hello world api，使其可以在頁面上按按鈕呼叫，顯示於畫面"
```

#### 環境設置

設置環境變數 `X_API_KEY` 為您的 X.AI API 密鑰：

```shell
export X_API_KEY=your-xai-api-key
```

或者在 Windows 上：

```
set X_API_KEY=your-xai-api-key
```

### 2. Ollama 自動生成 (`ollama_auto_gen.py`)

這個腳本使用本地 Ollama 模型來進行代碼生成，適合希望在本地運行 AI 模型的使用者。

#### 使用方法

```shell
python auto_gen/ollama_auto_gen.py --task "你的任務描述" --model "模型名稱"
```

例如：

```shell
python auto_gen/ollama_auto_gen.py --task "實現一個計算器功能" --model "deepseek-r1"
```

### 3. MCP 代理整合 (`xai_use_mcp.py`)

這個腳本將 AutoGen 框架與 MCP (多通道代理) 整合，實現更複雜的代理間協作。

#### 使用方法

```shell
python auto_gen/xai_use_mcp.py --task "你的任務描述"
```

## 輸出結果

所有生成的代碼和審查結果會保存在 `code_review_results/` 目錄中，每次運行都會創建一個以時間戳命名的子目錄。輸出結果包括：

- 完整的前後端代碼文件
- 代碼審查過程的對話記錄 (`conversation.txt`)
- 完整的對話記錄 JSON 格式 (`full_conversation.json`)
- 專案說明文件 (`README.md`)

## 常見問題排除

### 文件名稱異常問題

如果生成的結果目錄中包含異常文件名（如含有反引號、「文件：」前綴或中文文件名），可以使用提供的 `fix.py` 腳本進行修復：

```shell
python fix.py code_review_results/your_result_dir
```

### API 連接問題

如果遇到 API 連接問題，請檢查：

1. 環境變數 `X_API_KEY` 是否正確設置
2. 網絡連接是否正常
3. API 服務是否可用

### Ollama 問題

如果使用 Ollama 模型遇到問題：

1. 確認 Ollama 服務是否正在運行 (`ollama serve`)
2. 確認指定的模型是否已下載 (`ollama list`)
3. 對於較大的生成任務，考慮使用記憶體更大的模型

## 進階配置

如需更高級的配置，可以修改各腳本中的相關參數，如：

- 在 `get_xai_client()` 函數中修改模型選項
- 調整系統提示以獲得不同風格的代碼生成
- 自定義代碼審查的標準和流程

## 參考資源

- [AutoGen 官方文檔](https://microsoft.github.io/autogen/)
- [AutoGen Swarm 介紹](https://www.aivi.fyi/aiagents/introduce-autogen-swarm)
- [Ollama 模型庫](https://ollama.com/library)
- [X.AI API 文檔](https://platform.x.ai/docs/introduction)
