"""
AutoGen XAI Code Generation and Evaluation System - Example Usage
======================================
This script demonstrates how to use the code generation and evaluation system for various programming tasks.
"""

import os
import sys
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import our code generation evaluation modules
from enhanced_code_generation_evaluation import (
    run_code_generation_evaluation_workflow, 
    extract_code_from_markdown,
    get_module_name_from_task
)

# Load environment variables
load_dotenv()

# Check environment variables
if not os.getenv("X_API_KEY"):
    raise ValueError("Please set X_API_KEY environment variable")

def save_results(results, output_dir="example_code"):
    """
    Save results to appropriate files
    
    Args:
        results: Dictionary containing generation results
        output_dir: Directory to save files to
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract module name and code
    module_name = results.get("module_name", "example_module")
    optimized_code = results.get("optimized_code", "")
    
    # Save optimized code as Python file
    with open(os.path.join(output_dir, f"{module_name}.py"), "w", encoding="utf-8") as f:
        f.write(optimized_code)
    
    # Save documentation as Markdown file
    with open(os.path.join(output_dir, f"{module_name}_documentation.md"), "w", encoding="utf-8") as f:
        f.write(f"# {module_name.replace('_', ' ').title()}\n\n")
        
        # Add task description section
        f.write(f"## Task Description\n\n{results.get('task_description', '')}\n\n")
        
        # Add usage instructions
        f.write(f"## Usage\n\n")
        f.write(f"The code is available in the file `{module_name}.py`.\n\n")
        f.write(f"### How to Use\n\n")
        f.write(f"1. Import the module:\n```python\nimport {module_name}\n```\n\n")
        
        # Add code evaluation
        f.write(f"## Code Evaluation\n\n{results.get('final_evaluation', '')}\n\n")
        
        # Add both code versions for reference
        f.write(f"## Original Code (for reference)\n\n```python\n{results.get('initial_code', '')}\n```\n\n")
        f.write(f"## Optimized Code (implemented)\n\n```python\n{optimized_code}\n```\n\n")
    
    print(f"Files generated successfully:")
    print(f"- Code file: {os.path.join(output_dir, f'{module_name}.py')}")
    print(f"- Documentation: {os.path.join(output_dir, f'{module_name}_documentation.md')}")

def main():
    """Run several different code generation evaluation examples"""
    
    # Example task list
    tasks = [
        # Example 1: Data Processing
        {
            "name": "CSV Data Processor",
            "description": """
            Implement a CSV data processing tool with the following features:
            1. Read and parse CSV files
            2. Support data cleaning (handle missing values, outliers, etc.)
            3. Calculate basic statistics (mean, median, standard deviation, etc.)
            4. Support data filtering and sorting
            5. Ability to merge multiple CSV files
            6. Support exporting processed data to new CSV files
            """
        },
        
        # Example 2: Web Application
        {
            "name": "Flask Todo App",
            "description": """
            Implement a simple Todo web application using Flask with the following features:
            1. Users can add, edit, and delete tasks
            2. Support for task categories and priority settings
            3. Deadline reminder functionality
            4. Simple user authentication system
            5. Data storage in SQLite database
            6. Provide RESTful API endpoints
            """
        },
        
        # Example 3: Algorithm Implementation
        {
            "name": "Sorting Algorithms",
            "description": """
            Implement the following sorting algorithms and compare their performance:
            1. Quick Sort
            2. Merge Sort
            3. Heap Sort
            4. Counting Sort
            5. Radix Sort
            Your code should include:
            - Complete implementation of each algorithm
            - Performance testing method
            - Comparison results for different input sizes
            - Function to visualize the comparison results
            """
        }
    ]
    
    # Choose task to run
    # In actual use, modify this index as needed
    task_index = 0  # Default to first task
    
    # Check command line arguments
    if len(sys.argv) > 1:
        try:
            task_index = int(sys.argv[1])
            if task_index < 0 or task_index >= len(tasks):
                print(f"Task index must be between 0-{len(tasks)-1}, using default index 0")
                task_index = 0
        except ValueError:
            print("Command line argument must be an integer, using default index 0")
    
    selected_task = tasks[task_index]
    
    print("="*80)
    print(f"Starting task: {selected_task['name']}")
    print("="*80)
    
    # Run code generation evaluation workflow
    results = run_code_generation_evaluation_workflow(selected_task['description'])
    
    # Extract module name if not already in results
    if "module_name" not in results:
        results["module_name"] = get_module_name_from_task(selected_task['description'])
    
    # Save results to output directory named after the task
    output_dir = f"example_{selected_task['name'].lower().replace(' ', '_')}"
    save_results(results, output_dir)
    
    print("="*80)
    print(f"Task completed! Files have been saved to the {output_dir} directory.")
    print("="*80)

if __name__ == "__main__":
    main()
