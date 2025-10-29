"""
防逆流控制系统主入口
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入并运行主应用
from src.ui.app import main

if __name__ == "__main__":
    main()
