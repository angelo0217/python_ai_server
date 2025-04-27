"""
AutoGen 代碼生成與優化系統

這個套件提供了一個基於 AutoGen 的智能代理系統，用於代碼生成和優化。
系統包含兩個主要代理：Agent A (代碼編寫者) 和 Agent B (代碼審查者)。
"""

__version__ = "0.1.0"

from .autogen_code_agents import run_code_generation_review_cycle
from .autogen_code_agents_extended import (
    CodeGenerationSystem,
    PREDEFINED_TASKS,
    get_gemini_config
)

__all__ = [
    "run_code_generation_review_cycle",
    "CodeGenerationSystem",
    "PREDEFINED_TASKS",
    "get_gemini_config"
]
