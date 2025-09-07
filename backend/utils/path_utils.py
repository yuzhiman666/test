from pathlib import Path

# 获取当前文件（path_utils.py）的绝对路径
current_file = Path(__file__).resolve()

# 确定项目根目录（AUTO_FINANCE_POC）
# 假设当前文件位于 AUTO_FINANCE_POC/utils/ 目录下
# 则需要向上两级目录才能到达根目录
PROJECT_ROOT = current_file.parent.parent

# 验证根目录是否正确（检查是否存在标志性子目录）
if not (PROJECT_ROOT / "config").exists():
    raise RuntimeError(
        f"自动检测的项目根目录 {PROJECT_ROOT} 不正确，请手动调整路径层级"
    )

""" # 定义各子目录路径
AGENTS_DIR = PROJECT_ROOT / "agents"       # 代理相关目录
CONFIG_DIR = PROJECT_ROOT / "config"       # 配置文件目录
HUMAN_IN_LOOP_DIR = PROJECT_ROOT / "human-in-loop-demo"  # 人工介入演示目录
WORKFLOW_DIR = PROJECT_ROOT / "workflow"   # 工作流目录
UTILS_DIR = PROJECT_ROOT / "utils"         # 工具函数目录

# 确保所有目录存在（不存在则创建）
for dir_path in [
    AGENTS_DIR,
    CONFIG_DIR,
    HUMAN_IN_LOOP_DIR,
    WORKFLOW_DIR,
    UTILS_DIR
]:
    dir_path.mkdir(exist_ok=True, parents=True)

# 可以进一步定义各目录下的常用文件路径
# 例如配置文件、日志文件等
DEFAULT_CONFIG = CONFIG_DIR / "config.yaml"
LOG_FILE = UTILS_DIR / "log_config.log" """
