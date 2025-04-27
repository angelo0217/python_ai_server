"""
AutoGen XAI Code Generation and Evaluation System - Advanced Configuration
=======================================
This script demonstrates how to customize and configure the code generation evaluation system.
"""

import os
import json
import time
import requests
import re
import autogen
from dotenv import load_dotenv
import logging
from typing import Dict, List, Any, Optional
import datetime
import argparse

# Import base modules
from enhanced_code_generation_evaluation import (
    XAIAgent,
    CodeGeneratorAgent, 
    CodeEvaluatorAgent, 
    extract_code_from_markdown,
    get_module_name_from_task,
    logger
)

# Load environment variables
load_dotenv()

# Check environment variables
X_API_KEY = os.getenv("X_API_KEY")
if not X_API_KEY:
    raise ValueError("Please set X_API_KEY environment variable")

# Enhanced code generator agent with language-specific optimizations
class EnhancedCodeGeneratorAgent(XAIAgent):
    """Enhanced code generator agent with language-specific optimizations"""
    
    def __init__(self, name: str = "Enhanced Code Generator", language: str = "python", complexity: str = "medium"):
        """
        Initialize enhanced code generator agent
        
        Args:
            name: Agent name
            language: Target programming language ("python", "javascript", "java", "cpp", "go")
            complexity: Code complexity ("simple", "medium", "complex")
        """
        # Language-specific prompts
        language_prompts = {
            "python": """你是一位Python专家，专注于编写清晰、高效且符合PEP 8规范的代码。
请使用现代Python特性（如f-strings、类型注解、dataclasses等）。
优先考虑标准库，必要时再使用第三方库。""",
            
            "javascript": """你是一位JavaScript/TypeScript专家，专注于编写符合现代ES6+标准的代码。
优先使用函数式编程和不可变数据结构，尽量使用async/await而非回调。
适当时请使用TypeScript类型注解以提高代码质量。""",
            
            "java": """你是一位Java专家，专注于编写符合最新Java标准的面向对象代码。
遵循SOLID原则，适当使用设计模式，并注重代码的可测试性。
使用Java新特性如Stream API、Optional、var关键字等。""",
            
            "cpp": """你是一位C++专家，专注于编写高效、安全且现代的C++代码。
遵循C++17/20标准实践，如使用智能指针、避免原始指针、使用auto等。
关注内存安全和性能优化，适当使用STL和并发特性。""",
            
            "go": """你是一位Go专家，专注于编写符合Go惯用法的简洁高效代码。
遵循Go的设计哲学，如简单性、可读性和组合优于继承。
适当使用Go的并发特性如goroutines和channels，注重错误处理。"""
        }
        
        # Complexity-adjusted prompts
        complexity_prompts = {
            "simple": "请编写简单、易于理解的代码，避免过度设计和复杂抽象。适合初学者学习使用。",
            "medium": "请平衡代码的简洁性和功能完整性，提供合理的抽象和模块化设计。",
            "complex": "请编写企业级代码，包含完善的错误处理、日志记录、性能优化和扩展性设计。提供完整的文档和单元测试。"
        }
        
        # Get default prompts (if language not specified)
        lang_prompt = language_prompts.get(language.lower(), language_prompts["python"])
        complex_prompt = complexity_prompts.get(complexity.lower(), complexity_prompts["medium"])
        
        # Combine system prompts
        system_message = f"""你是一位专业的软件开发者，负责根据任务要求编写高质量的代码。

{lang_prompt}

{complex_prompt}

请遵循以下原则:
1. 代码应该高效、清晰且易于理解
2. 提供适当的注释和文档字符串
3. 使用合适的设计模式和最佳实践
4. 避免重复代码，保持代码的模块化
5. 考虑边缘情况和异常处理
6. 确保代码具有良好的可读性和可维护性

请务必提供完整可运行的代码实现，不要省略任何重要部分。
在回复中，请先简要说明你的实现思路，然后提供完整的代码。"""
        
        # Initialize base class
        super().__init__(
            name=name,
            system_message=system_message,
            temperature=0.2  # Use lower temperature for more stable code output
        )
        
        # Save settings for later reference
        self.language = language
        self.complexity = complexity

# Enhanced code evaluation workflow
def run_enhanced_workflow(
    task_description: str,
    language: str = "python",
    complexity: str = "medium",
    iterations: int = 2,
    output_dir: str = "results"
) -> Dict[str, str]:
    """
    Run enhanced code generation and evaluation workflow
    
    Args:
        task_description: Code generation task description
        language: Target programming language
        complexity: Code complexity
        iterations: Number of optimization iterations
        output_dir: Output directory
        
    Returns:
        Dictionary containing generated content from the entire interaction
    """
    # Create agents
    code_generator = EnhancedCodeGeneratorAgent(
        name="Code Generator",
        language=language,
        complexity=complexity
    )
    code_evaluator = CodeEvaluatorAgent(name="Code Evaluator")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Results dictionary
    results = {
        "task_description": task_description,
        "language": language,
        "complexity": complexity,
        "iterations": iterations,
        "iteration_history": []
    }
    
    # First round code generation
    logger.info("="*80)
    logger.info(f"Starting Round 1 code generation (Language: {language}, Complexity: {complexity})")
    logger.info("="*80)
    
    code_prompt = f"""Please write high-quality {language.upper()} code based on the following requirements:

{task_description}

Please provide a complete implementation and ensure the code can run directly."""
    
    current_code_response = code_generator.generate_response(code_prompt)
    
    # Extract actual code from markdown formatted response
    current_code = extract_code_from_markdown(current_code_response)
    
    # Record first round result
    iteration_result = {
        "round": 1,
        "code": current_code,
        "evaluation": "",
    }
    
    # Multiple iteration optimization
    for i in range(iterations):
        # Code evaluation
        logger.info("="*80)
        logger.info(f"Starting Round {i+1} code evaluation")
        logger.info("="*80)
        
        evaluation_prompt = f"""Please evaluate the following {language.upper()} code based on the requirements:

Task Description:
{task_description}

Code Implementation:
```{language}
{current_code}
```

Please evaluate the code quality in detail, identify strengths and weaknesses, and provide specific optimization suggestions.
Pay special attention to best practices and common issues in {language}."""
        
        evaluation = code_evaluator.generate_response(evaluation_prompt)
        iteration_result["evaluation"] = evaluation
        
        # Add to result history
        results["iteration_history"].append(iteration_result.copy())
        
        # Last round doesn't need optimization
        if i == iterations - 1:
            break
        
        # Optimize code based on evaluation
        logger.info("="*80)
        logger.info(f"Starting Round {i+2} code optimization")
        logger.info("="*80)
        
        optimization_prompt = f"""Please optimize your previous {language.upper()} code based on the evaluation feedback:

Original Task:
{task_description}

Your original code implementation:
```{language}
{current_code}
```

Evaluation Feedback:
{evaluation}

Please provide a complete optimized code implementation based on the evaluation feedback.
Pay special attention to addressing the issues identified in the evaluation and adopting the specific improvement suggestions.
Please provide the complete code without omitting any parts."""
        
        optimized_code_response = code_generator.generate_response(optimization_prompt)
        
        # Extract actual code from markdown formatted response
        current_code = extract_code_from_markdown(optimized_code_response)
        
        # Prepare next iteration record
        iteration_result = {
            "round": i+2,
            "code": current_code,
            "evaluation": "",
        }
    
    # Final evaluation
    logger.info("="*80)
    logger.info("Starting final code evaluation")
    logger.info("="*80)
    
    final_evaluation_prompt = f"""Please compare and evaluate the initial and final optimized code versions for the following task:

Task Description:
{task_description}

Initial Code (Round 1):
```{language}
{results["iteration_history"][0]["code"]}
```

Final Code (Round {iterations}):
```{language}
{current_code}
```

Please comprehensively evaluate the improvement in code quality, analyze whether the optimization process has addressed key issues,
and whether it conforms to the best practices of the {language} language. Please provide a detailed final evaluation and score."""
    
    final_evaluation = code_evaluator.generate_response(final_evaluation_prompt)
    results["final_evaluation"] = final_evaluation
    
    logger.info("="*80)
    logger.info("Enhanced code generation and evaluation workflow completed")
    logger.info("="*80)
    
    # Generate appropriate module name
    module_name = get_module_name_from_task(task_description)
    results["module_name"] = module_name
    
    # Get file extension based on language
    file_extensions = {
        "python": ".py",
        "javascript": ".js",
        "java": ".java",
        "cpp": ".cpp",
        "go": ".go"
    }
    file_extension = file_extensions.get(language.lower(), ".txt")
    
    # Save to appropriate files
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{module_name}{file_extension}"
    doc_file_name = f"{module_name}_documentation.md"
    
    # Save code to a source file with appropriate extension
    with open(os.path.join(output_dir, file_name), "w", encoding="utf-8") as f:
        f.write(current_code)
    
    # Save documentation to a Markdown file
    with open(os.path.join(output_dir, doc_file_name), "w", encoding="utf-8") as f:
        f.write(f"# {module_name.replace('_', ' ').title()} ({language.title()})\n\n")
        f.write(f"- **Language**: {language}\n")
        f.write(f"- **Complexity**: {complexity}\n")
        f.write(f"- **Iterations**: {iterations}\n\n")
        
        # Add task description section
        f.write(f"## Task Description\n\n{task_description}\n\n")
        
        # Add usage instructions
        f.write(f"## Usage\n\n")
        f.write(f"The code is available in the file `{file_name}`.\n\n")
        
        # Add language-specific usage instructions
        if language.lower() == "python":
            f.write(f"### How to Use\n\n")
            f.write(f"1. Import the module:\n```python\nimport {module_name}\n```\n\n")
        elif language.lower() == "javascript":
            f.write(f"### How to Use\n\n")
            f.write(f"1. Include the script in your HTML:\n```html\n<script src=\"{file_name}\"></script>\n```\n\n")
        
        # Add code evaluation
        f.write(f"## Code Evaluation\n\n{final_evaluation}\n\n")
        
        # Add iteration history for reference
        f.write(f"## Development History\n\n")
        for i, iter_result in enumerate(results["iteration_history"]):
            f.write(f"### Round {iter_result['round']}\n\n")
            if i < len(results["iteration_history"]) - 1:
                f.write(f"#### Evaluation\n\n{iter_result['evaluation']}\n\n")
        
        # Add both code versions for reference
        f.write(f"## Original Code (for reference)\n\n```{language}\n{results['iteration_history'][0]['code']}\n```\n\n")
        f.write(f"## Final Code (implemented)\n\n```{language}\n{current_code}\n```\n\n")
    
    logger.info(f"Results saved to {output_dir}/{file_name} and {output_dir}/{doc_file_name}")
    print(f"\nFiles generated successfully:")
    print(f"- Code file: {os.path.join(output_dir, file_name)}")
    print(f"- Documentation: {os.path.join(output_dir, doc_file_name)}")
    
    return results

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description="AutoGen XAI Code Generation and Evaluation System - Advanced Configuration")
    
    # Task-related parameters
    parser.add_argument("--task_file", type=str, help="Path to a text file containing the task description")
    parser.add_argument("--task", type=str, help="Task description (provided directly on the command line)")
    
    # Code generation configuration
    parser.add_argument("--language", type=str, default="python", 
                        choices=["python", "javascript", "java", "cpp", "go"],
                        help="Target programming language")
    parser.add_argument("--complexity", type=str, default="medium",
                        choices=["simple", "medium", "complex"],
                        help="Code complexity level")
    
    # Workflow configuration
    parser.add_argument("--iterations", type=int, default=2,
                        help="Number of code optimization iterations")
    parser.add_argument("--output_dir", type=str, default="results",
                        help="Output directory for results")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Get task description
    task_description = None
    if args.task_file:
        try:
            with open(args.task_file, "r", encoding="utf-8") as f:
                task_description = f.read()
        except Exception as e:
            logger.error(f"Error reading task file: {str(e)}")
            return
    elif args.task:
        task_description = args.task
    else:
        # Default example task
        task_description = """
        Implement a file encryption/decryption tool with the following features:
        1. Support for AES and RSA encryption algorithms
        2. Ability to encrypt/decrypt text files and binary files
        3. Provide both command-line interface and simple graphical user interface
        4. Implement key management features (generation, storage, import/export)
        5. Support batch processing of multiple files
        6. Include detailed usage documentation and examples
        """
    
    # Run workflow
    logger.info(f"Starting workflow with the following configuration:")
    logger.info(f"- Language: {args.language}")
    logger.info(f"- Complexity: {args.complexity}")
    logger.info(f"- Iterations: {args.iterations}")
    
    results = run_enhanced_workflow(
        task_description=task_description,
        language=args.language,
        complexity=args.complexity,
        iterations=args.iterations,
        output_dir=args.output_dir
    )
    
    print(f"\nTask completed! Results saved to {args.output_dir} directory")

if __name__ == "__main__":
    main()
