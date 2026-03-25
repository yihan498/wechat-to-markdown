"""配置加载模块"""
import os
import yaml
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent


def load_config(config_path: str = None) -> dict:
    if config_path is None:
        config_path = ROOT_DIR / "config" / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    db_path = cfg["database"]["path"]
    if not os.path.isabs(db_path):
        cfg["database"]["path"] = str(ROOT_DIR / db_path)

    log_dir = cfg["logging"]["log_dir"]
    if not os.path.isabs(log_dir):
        cfg["logging"]["log_dir"] = str(ROOT_DIR / log_dir)

    return cfg


def get_account(cfg: dict, name: str = None) -> dict:
    """
    按名称查找账号配置；name 为 None 时返回 default 账号。
    返回 {"name": ..., "save_dir": ...}
    """
    accounts = cfg.get("accounts", [])
    if not accounts:
        raise ValueError("config.yaml 中没有配置任何 accounts")

    if name:
        for acc in accounts:
            if acc["name"] == name:
                return acc
        available = [a["name"] for a in accounts]
        raise ValueError(f"找不到账号 '{name}'，可用账号：{available}")

    # 找 default
    for acc in accounts:
        if acc.get("default"):
            return acc
    # 没有标记 default 则返回第一个
    return accounts[0]
