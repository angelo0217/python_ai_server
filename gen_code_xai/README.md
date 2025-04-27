# AutoGen XAI 代码生成评估系统

这个项目使用 AutoGen 框架和 X.AI 的 Grok 模型实现了一个代码生成与评估系统，由两个智能体协作完成：

1. **Agent A（代码生成器）**：根据任务描述自动生成高质量的代码
2. **Agent B（代码评估器）**：评估代码质量，提供优化建议

两个智能体通过多轮交互完成代码优化，形成一个完整的代码生成-评估-优化流程。

## 安装依赖

首先，请安装所需依赖：

```bash
pip install python-dotenv pyautogen requests
```

## 环境配置

1. 复制`.env.example`文件为`.env`
2. 编辑`.env`文件，添加您的X.AI API密钥：

```
X_API_KEY=your_xai_api_key_here
```

注意：您需要有X.AI的API密钥才能使用此系统。

## 文件说明

本项目包含以下主要文件：

- `code_generation_evaluation.py`：基础版代码生成评估系统
- `enhanced_code_generation_evaluation.py`：增强版代码生成评估系统，提供更完善的功能
- `examples.py`：展示不同任务场景的示例
- `advanced_config.py`：支持高级配置和自定义的版本
- `requirements.txt`：依赖列表
- `.env.example`：环境变量示例文件

## 三个主要文件的差异

本系统提供了三个不同复杂度和功能层次的实现版本，从基础到高级：

### `code_generation_evaluation.py` vs `enhanced_code_generation_evaluation.py` vs `advanced_config.py`

#### 功能特性比较

| 特性 | code_generation_evaluation | enhanced_code_generation_evaluation | advanced_config |
|------|----------------------------|-------------------------------------|-----------------|
| 基本代码生成 | ✓ | ✓ | ✓ |
| 代码评估 | ✓ | ✓ | ✓ |
| 代码优化 | ✓ | ✓ | ✓ |
| 详细日志 | 基本 | 增强 | 增强 |
| 多语言支持 | 仅Python | 仅Python | 多种语言 |
| 复杂度设置 | 固定 | 固定 | 可配置 |
| 命令行参数 | 无 | 无 | ✓ |
| 迭代次数控制 | 固定2轮 | 固定2轮 | 可配置 |
| 文件输出 | 基本 | 增强 | 高度定制 |

#### 使用场景

- **code_generation_evaluation.py**：
  - 适合初次使用系统的用户
  - 快速测试基本功能
  - Python代码生成的简单任务

- **enhanced_code_generation_evaluation.py**：
  - 更稳定的生产环境使用
  - 需要详细日志和更好输出的情况
  - 仍然只针对Python代码生成

- **advanced_config.py**：
  - 需要生成多种语言代码的场景
  - 需要通过命令行控制参数的情况
  - 需要不同代码复杂度设置的用户
  - 需要更多迭代轮次的复杂任务

#### 如何选择

- 如果想要快速测试：使用`code_generation_evaluation.py`
- 如果需要更好的Python代码生成：使用`enhanced_code_generation_evaluation.py`
- 如果需要高度定制化和多语言支持：使用`advanced_config.py`

## 使用方法

### 基础用法

运行基础版代码生成评估系统：

```bash
python code_generation_evaluation.py
```

### 示例任务

运行示例任务（包含数据处理、Web应用和算法实现）：

```bash
python examples.py
```

您可以通过命令行参数选择要运行的示例任务：

```bash
python examples.py 0  # 运行数据处理任务
python examples.py 1  # 运行Web应用任务
python examples.py 2  # 运行算法实现任务
```

### 高级配置

高级配置支持多种编程语言、不同复杂度级别和多轮迭代：

```bash
python advanced_config.py --language python --complexity medium --iterations 2
```

可用参数：

- `--language`：编程语言（python, javascript, java, cpp, go）
- `--complexity`：代码复杂度（simple, medium, complex）
- `--iterations`：优化迭代次数
- `--task`：直接在命令行提供任务描述
- `--task_file`：从文件读取任务描述
- `--output_dir`：结果输出目录

示例：

```bash
# 使用JavaScript生成简单复杂度的代码，进行3轮迭代
python advanced_config.py --language javascript --complexity simple --iterations 3

# 从文件读取任务描述
python advanced_config.py --task_file tasks/my_task.txt --language python

# 直接提供任务描述
python advanced_config.py --task "实现一个简单的天气预报应用，可以获取和显示特定城市的未来5天天气预报"
```

## 输出文件

系统生成两种类型的输出文件：

1. **源代码文件**：
   - 包含完整的代码实现，可以直接运行或导入使用
   - 文件命名基于任务内容，扩展名基于编程语言（如.py、.js等）

2. **文档文件**：
   - 包含任务描述、使用说明、代码评估结果
   - 保留原始代码和优化代码的记录，方便比较和学习
   - 提供详细的使用指导，帮助用户理解如何使用生成的代码

## 模型说明

此系统使用X.AI的Grok模型（grok-3-latest）通过X.AI的API进行调用：

```
API端点: https://api.x.ai/v1/chat/completions
```

## 自定义任务

您可以通过以下方式自定义任务：

1. 修改代码中的示例任务
2. 使用`--task`参数提供任务描述
3. 使用`--task_file`参数从文件读取任务描述

## 常见问题

1. **API密钥问题**：确保您有有效的X.AI API密钥，并正确设置在`.env`文件中
2. **依赖问题**：确保安装了正确版本的依赖，特别是pyautogen和requests
3. **调用限制**：X.AI API可能有调用频率限制，如果遇到错误，请稍后再试

## 性能优化

- 调整`temperature`参数可以控制代码生成的创造性和稳定性
- 增加迭代次数可获得更优质的代码，但会增加API调用次数
- 对于复杂任务，建议使用`complexity=complex`参数获得更完善的实现

## 示例任务描述

以下是一些可以尝试的任务描述示例：

```
实现一个简单的网络爬虫，可以从指定网页抓取内容并保存为本地文件。

创建一个任务管理器应用，支持添加、删除、编辑和标记任务完成状态。

实现一个简单的机器学习模型，可以预测房价基于面积、卧室数量和地区等特征。

开发一个文件加密工具，支持AES加密算法和密码保护。

创建一个简单的RESTful API服务，提供基本的CRUD操作和用户认证。
```

---

希望这个指南能帮助您充分利用AutoGen XAI代码生成评估系统。如有任何问题，请参考代码中的注释或相关文档。
