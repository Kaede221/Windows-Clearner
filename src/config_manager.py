"""
配置管理模块

管理应用程序的自定义配置，包括用户选择的自定义扫描文件夹。
"""

import json
import logging
import os
from typing import List
from pathlib import Path

logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器，负责保存和加载应用配置"""
    
    CONFIG_FILE = "config/app_config.json"
    
    def __init__(self):
        """初始化配置管理器"""
        self._config = self._load_config()
    
    def _load_config(self) -> dict:
        """
        从文件加载配置
        
        Returns:
            配置字典
        """
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.info(f"配置已从 {self.CONFIG_FILE} 加载")
                    return config
            except Exception as e:
                logger.error(f"加载配置文件失败: {e}", exc_info=True)
                return self._get_default_config()
        else:
            logger.info("配置文件不存在，使用默认配置")
            return self._get_default_config()
    
    def _get_default_config(self) -> dict:
        """
        获取默认配置
        
        Returns:
            默认配置字典
        """
        return {
            "custom_folders": [],
            "auto_check_updates": True
        }
    
    def _save_config(self) -> None:
        """保存配置到文件"""
        try:
            # 确保配置目录存在
            config_dir = os.path.dirname(self.CONFIG_FILE)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            # 保存配置
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=4)
            
            logger.info(f"配置已保存到 {self.CONFIG_FILE}")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}", exc_info=True)
    
    def get_custom_folders(self) -> List[str]:
        """
        获取用户自定义的扫描文件夹列表
        
        Returns:
            文件夹路径列表
        """
        return self._config.get("custom_folders", [])
    
    def set_custom_folders(self, folders: List[str]) -> None:
        """
        设置用户自定义的扫描文件夹列表
        
        Args:
            folders: 文件夹路径列表
        """
        self._config["custom_folders"] = folders
        self._save_config()
        logger.info(f"自定义文件夹已更新: {folders}")
    
    def get_auto_check_updates(self) -> bool:
        """
        获取是否自动检查更新
        
        Returns:
            是否自动检查更新
        """
        return self._config.get("auto_check_updates", True)
    
    def set_auto_check_updates(self, enabled: bool) -> None:
        """
        设置是否自动检查更新
        
        Args:
            enabled: 是否启用
        """
        self._config["auto_check_updates"] = enabled
        self._save_config()
        logger.info(f"自动检查更新已设置为: {enabled}")


# 全局配置管理器实例
config_manager = ConfigManager()
