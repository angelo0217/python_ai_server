"""
AutoGen Code Generation and Evaluation System
=========================
This script implements two agents based on AutoGen:
1. Agent A: Code Generator - Writes code based on task descriptions
2. Agent B: Code Evaluator - Evaluates Agent A's code and provides optimization suggestions

Both agents use the grok-3-latest model and interact for two rounds.
"""

import os
import time
import json
import requests
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Check environment variables
X_API_KEY = os.getenv("X_API_KEY")
if not X_API_KEY:
    raise ValueError("Please set X_API_KEY environment variable")

# Custom Agent class
class XAIAgent:
    """Custom agent using X.AI's grok model for code generation and evaluation"""

    def __init__(self, name, system_message, temperature=0.7):
        """
        Initialize agent

        Args:
            name: Agent name
            system_message: System message/prompt
            temperature: Generation temperature (0.0-1.0)
        """
        self.name = name
        self.system_message = system_message
        self.temperature = temperature
        self.model = "grok-3-latest"
        self.api_url = "https://api.x.ai/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {X_API_KEY}"
        }

        logger.info(f"Successfully initialized {self.name} agent")

    def generate_response(self, prompt):
        """
        Generate response

        Args:
            prompt: Input prompt

        Returns:
            Generated response text
        """
        try:
            # Prepare request data
            messages = [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": prompt}
            ]

            data = {
                "messages": messages,
                "model": self.model,
                "stream": False,
                "temperature": self.temperature
            }

            # Send request
            response = requests.post(
                self.api_url,
                headers=self.headers,
                data=json.dumps(data)
            )

            # Check response status
            response.raise_for_status()
            response_json = response.json()

            # Extract reply content
            content = response_json.get("choices", [{}])[0].get("message", {}).get("content", "")

            return content
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"Error generating response: {str(e)}"

def run_code_generation_evaluation_process(task_description):
    """
    Run code generation and evaluation interaction process

    Args:
        task_description (str): Code generation task description
    """
    # Create code generator agent (Agent A)
    code_generator = XAIAgent(
        name="Code Generator",
        system_message="""你是一位专业的Python开发者，负责根据任务要求编写高质量的代码。
请遵循以下原则:
1. 代码应该高效、清晰且易于理解
2. 提供适当的注释和文档字符串
3. 使用合适的设计模式和最佳实践
4. 避免重复代码，保持代码的模块化
5. 考虑边缘情况和异常处理
6. 确保代码具有良好的可读性和可维护性

您的回复应该包含完整的实现代码，并简要解释您的实现方法。""",
        temperature=0.3  # Lower temperature for code generation
    )

    # Create code evaluator agent (Agent B)
    code_evaluator = XAIAgent(
        name="Code Evaluator",
        system_message="""你是一位经验丰富的代码审查者，负责评估和优化其他开发者的代码。
请遵循以下评估原则:
1. 详细分析代码的性能、可读性和可维护性
2. 找出代码中的潜在问题和改进空间
3. 给出具体的优化建议和可行的解决方案
4. 提供建设性的反馈，指出代码的优点和不足
5. 考虑边缘情况和异常处理是否完整
6. 遵循Python最佳实践和设计模式

您的回复格式应为:
```
## 代码评估
- 优点:
  - [列出代码的优点]
- 需要改进:
  - [列出需要改进的地方]

## 优化建议
1. [具体的优化建议1]
2. [具体的优化建议2]
...

## 总体评分
[1-10分，并简要说明理由]
```""",
        temperature=0.1  # Even lower temperature for evaluation stability
    )

    # Set up two rounds of interaction
    logger.info("="*80)
    logger.info("Starting first round of code generation and evaluation")
    logger.info("="*80)

    # Round 1: Generate code
    logger.info(">> Code generator is generating code...")
    code_prompt = f"""Please write high-quality Python code based on the following requirements:

{task_description}

Please provide a complete implementation and ensure the code can run directly."""

    code_response = code_generator.generate_response(code_prompt)
    logger.info(f"Code generator has completed code generation:\n{'-'*40}\n{code_response}\n{'-'*40}")

    # Evaluate code
    logger.info(">> Code evaluator is evaluating the code...")
    evaluation_prompt = f"""Please evaluate the following code and provide optimization suggestions:

```python
{code_response}
```

This code was written based on these requirements:
{task_description}

Please provide a detailed evaluation and specific optimization suggestions."""

    evaluation_response = code_evaluator.generate_response(evaluation_prompt)
    logger.info(f"Code evaluator has completed evaluation:\n{'-'*40}\n{evaluation_response}\n{'-'*40}")

    # Round 2: Code optimization
    logger.info("="*80)
    logger.info("Starting second round of code optimization")
    logger.info("="*80)

    # Optimize code based on evaluation
    logger.info(">> Code generator is optimizing code based on evaluation...")
    optimization_prompt = f"""Please optimize your previously written code based on this evaluation feedback:

Original code:
```python
{code_response}
```

Evaluation feedback:
{evaluation_response}

Please provide the complete optimized code."""

    optimized_code = code_generator.generate_response(optimization_prompt)
    logger.info(f"Code generator has completed code optimization:\n{'-'*40}\n{optimized_code}\n{'-'*40}")

    # Final evaluation
    logger.info(">> Code evaluator is evaluating the optimized code...")
    final_evaluation_prompt = f"""Please evaluate the following optimized code:

```python
{optimized_code}
```

Compared to the previous code, does this code address the issues pointed out in the previous evaluation?
Please provide a final evaluation."""

    final_evaluation = code_evaluator.generate_response(final_evaluation_prompt)
    logger.info(f"Code evaluator has completed final evaluation:\n{'-'*40}\n{final_evaluation}\n{'-'*40}")

    logger.info("="*80)
    logger.info("Code generation and evaluation process completed")
    logger.info("="*80)

    # Return final results
    return {
        "original_code": code_response,
        "first_evaluation": evaluation_response,
        "optimized_code": optimized_code,
        "final_evaluation": final_evaluation
    }

if __name__ == "__main__":
    # Example task
    task = """
    Implement a simple web crawler with the following features:
    1. Start crawling from a given URL
    2. Parse all links in the web pages
    3. Set crawling depth and maximum number of pages to crawl
    4. Save crawling results to files
    5. Support multi-threaded crawling
    6. Implement basic error handling and retry mechanism
    """

    results = run_code_generation_evaluation_process(task)

    # Save results to file
    with open("Code_Generation_Evaluation_Results.md", "w", encoding="utf-8") as f:
        f.write("# Code Generation and Evaluation Results\n\n")
        f.write(f"## Task Description\n\n{task}\n\n")
        f.write(f"## Original Code\n\n```python\n{results['original_code']}\n```\n\n")
        f.write(f"## First Evaluation\n\n{results['first_evaluation']}\n\n")
        f.write(f"## Optimized Code\n\n```python\n{results['optimized_code']}\n```\n\n")
        f.write(f"## Final Evaluation\n\n{results['final_evaluation']}\n\n")
