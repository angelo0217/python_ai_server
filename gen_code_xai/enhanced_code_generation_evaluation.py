"""
Enhanced AutoGen Code Generation and Evaluation System
==================================================
This script implements two agents for code generation and evaluation interaction using AutoGen:
1. Agent A: Code Generator - Based on X.AI's grok model, generates code from task descriptions
2. Agent B: Code Evaluator - Based on X.AI's grok model, evaluates code and provides optimization suggestions

The agents interact in a more structured way for two rounds.
"""

import os
import json
import time
import requests
import re
import autogen
from autogen import AssistantAgent, UserProxyAgent
from dotenv import load_dotenv
import logging
from typing import Dict, List, Any, Optional
import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"autogen_xai_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Check environment variables
X_API_KEY = os.getenv("X_API_KEY")
if not X_API_KEY:
    raise ValueError("Please set X_API_KEY environment variable")

# Custom X.AI Agent class
class XAIAgent:
    """Custom XAI agent for code generation and evaluation"""
    
    def __init__(self, name: str, system_message: str, temperature: float = 0.7):
        """
        Initialize XAI agent
        
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
        
        logger.info(f"Successfully initialized XAI agent: {self.name}")
    
    def generate_response(self, prompt: str) -> str:
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
            logger.error(f"Error generating XAI response: {str(e)}")
            return f"Error generating response: {str(e)}"

# Custom code generator agent
class CodeGeneratorAgent(XAIAgent):
    """Code generator agent focused on generating code from task descriptions"""
    
    def __init__(self, name: str = "Code Generator"):
        """Initialize code generator agent"""
        system_message = """你是一位专业的Python开发者，负责根据任务要求编写高质量的代码。
请遵循以下原则:
1. 代码应该高效、清晰且易于理解
2. 提供适当的注释和文档字符串
3. 使用合适的设计模式和最佳实践
4. 避免重复代码，保持代码的模块化
5. 考虑边缘情况和异常处理
6. 确保代码具有良好的可读性和可维护性

请务必提供完整可运行的代码实现，不要省略任何重要部分。
在回复中，请先简要说明你的实现思路，然后提供完整的代码。"""
        
        super().__init__(
            name=name,
            system_message=system_message,
            temperature=0.2  # Use lower temperature for more stable code output
        )

# Custom code evaluator agent
class CodeEvaluatorAgent(XAIAgent):
    """Code evaluator agent focused on evaluating code quality and providing optimization suggestions"""
    
    def __init__(self, name: str = "Code Evaluator"):
        """Initialize code evaluator agent"""
        system_message = """你是一位经验丰富的代码审查者，负责评估和优化其他开发者的代码。
请遵循以下评估原则:
1. 详细分析代码的性能、可读性和可维护性
2. 找出代码中的潜在问题和改进空间
3. 给出具体的优化建议和可行的解决方案
4. 提供建设性的反馈，指出代码的优点和不足
5. 考虑边缘情况和异常处理是否完整
6. 检查是否遵循Python最佳实践和设计模式

请按照以下格式提供评估:

## 代码评估
### 优点
- [列出代码的优点]

### 需要改进
- [列出需要改进的地方]

## 优化建议
1. [具体的优化建议1]
2. [具体的优化建议2]
...

## 总体评分
[1-10分，并简要说明理由]"""
        
        super().__init__(
            name=name,
            system_message=system_message,
            temperature=0.1  # Use even lower temperature for more consistent evaluation
        )

def extract_code_from_markdown(markdown_text):
    """
    Extract code from markdown formatted text that has ```python ... ``` blocks
    
    Args:
        markdown_text: Text potentially containing code blocks
        
    Returns:
        Extracted code without the markdown formatting
    """
    # Look for Python code blocks
    python_code_pattern = r"```(?:python)?\s*([\s\S]*?)```"
    matches = re.findall(python_code_pattern, markdown_text)
    
    if matches:
        # Return the largest code block (likely the complete implementation)
        return max(matches, key=len).strip()
    else:
        # If no code blocks found, return the original text
        return markdown_text

def get_module_name_from_task(task_description):
    """
    Generate a suitable module name from the task description
    
    Args:
        task_description: Task description text
        
    Returns:
        A Python module name (snake_case)
    """
    # Extract the first sentence or first 50 characters
    first_line = task_description.strip().split('\n')[0]
    first_sentence = first_line.split('.')[0]
    
    # Remove unnecessary words and normalize
    name = first_sentence.lower()
    name = re.sub(r'implement\s+a\s+', '', name)
    name = re.sub(r'create\s+a\s+', '', name)
    name = re.sub(r'develop\s+a\s+', '', name)
    name = re.sub(r'build\s+a\s+', '', name)
    
    # Convert to snake_case
    name = re.sub(r'[^\w\s]', '', name)  # Remove punctuation
    name = re.sub(r'\s+', '_', name)     # Replace spaces with underscores
    
    # Ensure name doesn't start with a number
    if re.match(r'^\d', name):
        name = 'x_' + name
        
    # Limit length
    if len(name) > 40:
        name = name[:40]
        
    return name

# Define code generation evaluation workflow function
def run_code_generation_evaluation_workflow(task_description: str) -> Dict[str, str]:
    """
    Run complete code generation and evaluation workflow with two rounds of interaction
    
    Args:
        task_description: Code generation task description
        
    Returns:
        Dictionary containing generated content from the entire interaction
    """
    # Create agents
    code_generator = CodeGeneratorAgent()
    code_evaluator = CodeEvaluatorAgent()
    
    # Dictionary for storing results
    results = {
        "task_description": task_description,
        "initial_code": "",
        "initial_evaluation": "",
        "optimized_code": "",
        "final_evaluation": "",
    }
    
    # First round: code generation
    logger.info("="*80)
    logger.info("Starting first round of code generation")
    logger.info("="*80)
    
    code_prompt = f"""Please write high-quality Python code based on the following requirements:

{task_description}

Please provide a complete implementation and ensure the code can run directly."""
    
    initial_code_response = code_generator.generate_response(code_prompt)
    # Extract actual code from markdown formatted response
    initial_code = extract_code_from_markdown(initial_code_response)
    results["initial_code"] = initial_code
    logger.info(f"First round code generation completed, length: {len(initial_code)} characters")
    
    # First round: code evaluation
    logger.info("="*80)
    logger.info("Starting first round of code evaluation")
    logger.info("="*80)
    
    evaluation_prompt = f"""Please evaluate the following Python code based on the requirements:

Task Description:
{task_description}

Code Implementation:
```python
{initial_code}
```

Please evaluate the code quality in detail, identify strengths and weaknesses, and provide specific optimization suggestions."""
    
    initial_evaluation = code_evaluator.generate_response(evaluation_prompt)
    results["initial_evaluation"] = initial_evaluation
    logger.info(f"First round code evaluation completed, length: {len(initial_evaluation)} characters")
    
    # Second round: code optimization
    logger.info("="*80)
    logger.info("Starting second round of code optimization")
    logger.info("="*80)
    
    optimization_prompt = f"""Please optimize your previous code based on the evaluation feedback:

Original Task:
{task_description}

Your original code implementation:
```python
{initial_code}
```

Evaluation Feedback:
{initial_evaluation}

Please provide an optimized complete code implementation based on the evaluation. Pay special attention to addressing the issues identified in the evaluation."""
    
    optimized_code_response = code_generator.generate_response(optimization_prompt)
    # Extract actual optimized code from markdown formatted response
    optimized_code = extract_code_from_markdown(optimized_code_response)
    results["optimized_code"] = optimized_code
    logger.info(f"Optimized code generation completed, length: {len(optimized_code)} characters")
    
    # Final evaluation
    logger.info("="*80)
    logger.info("Starting final code evaluation")
    logger.info("="*80)
    
    final_evaluation_prompt = f"""Please compare and evaluate the following two code versions:

Task Description:
{task_description}

Original Code:
```python
{initial_code}
```

Optimized Code:
```python
{optimized_code}
```

Please evaluate whether the optimized code addresses the issues identified in the previous evaluation, whether the overall code quality has improved,
and whether there is still room for further improvement. Please provide a detailed final evaluation."""
    
    final_evaluation = code_evaluator.generate_response(final_evaluation_prompt)
    results["final_evaluation"] = final_evaluation
    logger.info(f"Final evaluation completed, length: {len(final_evaluation)} characters")
    
    logger.info("="*80)
    logger.info("Code generation and evaluation workflow completed")
    logger.info("="*80)
    
    # Generate module name from task
    module_name = get_module_name_from_task(task_description)
    results["module_name"] = module_name
    
    return results

def save_results(results: Dict[str, str], output_dir: str = "generated_code") -> None:
    """
    Save workflow results to appropriate files
    
    Args:
        results: Dictionary containing workflow results
        output_dir: Output directory for files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get module name
    module_name = results["module_name"]
    
    # Save optimized code as Python file
    with open(os.path.join(output_dir, f"{module_name}.py"), "w", encoding="utf-8") as f:
        f.write(results["optimized_code"])
    
    # Save documentation as Markdown file
    with open(os.path.join(output_dir, f"{module_name}_documentation.md"), "w", encoding="utf-8") as f:
        f.write(f"# {module_name.replace('_', ' ').title()}\n\n")
        
        # Add task description section
        f.write(f"## Task Description\n\n{results['task_description']}\n\n")
        
        # Add usage instructions
        f.write(f"## Usage\n\n")
        f.write(f"The code is available in the file `{module_name}.py`.\n\n")
        f.write(f"### How to Use\n\n")
        f.write(f"1. Import the module:\n```python\nimport {module_name}\n```\n\n")
        
        # Add code evaluation
        f.write(f"## Code Evaluation\n\n{results['final_evaluation']}\n\n")
        
        # Add both code versions for reference
        f.write(f"## Original Code (for reference)\n\n```python\n{results['initial_code']}\n```\n\n")
        f.write(f"## Optimized Code (implemented)\n\n```python\n{results['optimized_code']}\n```\n\n")
    
    logger.info(f"Results saved to {output_dir}/{module_name}.py and {output_dir}/{module_name}_documentation.md")
    print(f"\nFiles generated successfully:")
    print(f"- Code file: {os.path.join(output_dir, f'{module_name}.py')}")
    print(f"- Documentation: {os.path.join(output_dir, f'{module_name}_documentation.md')}")

if __name__ == "__main__":
    # Example task
    task = """
    Implement a weather data analysis tool with the following features:
    1. Fetch historical weather data for specified cities from the OpenWeatherMap API
    2. Support data visualization (temperature, humidity, pressure, etc.)
    3. Calculate basic statistics (average, maximum, minimum, etc.)
    4. Support exporting data to CSV or JSON format
    5. Implement a simple weather prediction feature (based on historical data)
    6. Error handling and logging
    """
    
    # Run workflow
    results = run_code_generation_evaluation_workflow(task)
    
    # Save results
    save_results(results)
    
    print("="*50)
    print("Code generation and evaluation workflow completed!")
    print("="*50)
