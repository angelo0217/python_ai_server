# AutoGen Gemini 代码生成评估系统使用指南

## 项目概述

本项目使用AutoGen框架和Gemini-2.5-pro-exp-03-25模型实现了一个代码生成与评估系统，由两个智能体协作完成：

1. **Agent A（代码生成器）**：根据任务描述自动生成高质量的代码
2. **Agent B（代码评估器）**：评估代码质量，提供优化建议

两个智能体通过多轮交互完成代码优化，形成一个完整的代码生成-评估-优化流程。

## 安装依赖

首先，请安装所需依赖：

```bash
pip install -r requirements.txt
```

或者直接安装以下依赖：

```bash
pip install python-dotenv>=1.0.0 pyautogen>=0.2.18 google-generativeai>=0.3.1 matplotlib>=3.8.0 pandas>=2.1.1 numpy>=1.26.0
```

## 环境配置

1. 复制`.env.example`文件为`.env`
2. 编辑`.env`文件，添加您的Google API密钥：

```
X_API_KEY=your_api_key_here
```

## 文件说明

本项目包含以下主要文件：

- `code_generation_evaluation.py`：基础版代码生成评估系统
- `enhanced_code_generation_evaluation.py`：增强版代码生成评估系统，提供更完善的功能
- `examples.py`：展示不同任务场景的示例
- `advanced_config.py`：支持高级配置和自定义的版本
- `requirements.txt`：依赖列表
- `.env.example`：环境变量示例文件

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

## 自定义任务

您可以通过以下方式自定义任务：

1. 修改代码中的示例任务
2. 使用`--task`参数提供任务描述
3. 使用`--task_file`参数从文件读取任务描述

## 输出结果

系统的输出结果包括：

1. 控制台日志：显示整个工作流程的进度
2. Markdown文件：包含完整的代码生成、评估和优化历史
3. 日志文件：记录详细的系统运行信息

## 常见问题

1. **API密钥问题**：确保您有有效的Google API密钥，并正确设置在`.env`文件中
2. **依赖问题**：确保安装了正确版本的依赖，特别是pyautogen和google-generativeai
3. **内存问题**：处理大型代码生成任务时，可能需要更多内存资源

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

## 进阶使用

高级用户可以通过修改源代码进一步自定义系统行为，例如：

1. 调整模型参数（温度、top-p等）
2. 修改系统提示以适应特定领域
3. 添加更多评估维度
4. 实现更复杂的交互流程

---

希望这个指南能帮助您充分利用AutoGen Gemini代码生成评估系统。如有任何问题，请参考代码中的注释或查看相关文档。
