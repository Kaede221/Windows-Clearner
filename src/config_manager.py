"""
配置管理器模块

负责加载和保存应用程序配置。
"""

import json
import logging
import os
from typing import Any, Dict

from .models import AppConfig, ScanConfig, JunkCategory

logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器，负责加载和保存应用程序配置"""
    
    CONFIG_FILE = "config.json"
    
    def load_config(self) -> AppConfig:
        """
        从文件加载配置
        
        如果配置文件不存在或损坏，返回默认配置
        
        Returns:
            AppConfig: 应用程序配置
        """
        try:
            if not os.path.exists(self.CONFIG_FILE):
                logger.info("配置文件不存在，使用默认配置")
                return self.get_default_config()
            
            with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            # 解析配置字典
            config = self._dict_to_config(config_dict)
            logger.info("成功加载配置文件")
            return config
            
        except json.JSONDecodeError as e:
            logger.error(f"配置文件格式错误: {e}，使用默认配置")
            return self.get_default_config()
            
        except Exception as e:
            logger.error(f"加载配置文件时出错: {e}，使用默认配置", exc_info=True)
            return self.get_default_config()
    
    def save_config(self, config: AppConfig) -> None:
        """
        保存配置到文件
        
        Args:
            config: 要保存的应用程序配置
        """
        try:
            # 将配置转换为字典
            config_dict = self._config_to_dict(config)
            
            # 保存到文件
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            logger.info("成功保存配置文件")
            
        except Exception as e:
            logger.error(f"保存配置文件时出错: {e}", exc_info=True)
            raise
    
    def get_default_config(self) -> AppConfig:
        """
        获取默认配置
        
        Returns:
            AppConfig: 默认应用程序配置
        """
        # 默认启用所有垃圾类别（除了自定义路径）
        enabled_categories = {
            JunkCategory.TEMP_FILES,
            JunkCategory.WINDOWS_UPDATE_CACHE,
            JunkCategory.RECYCLE_BIN,
            JunkCategory.BROWSER_CACHE,
            JunkCategory.THUMBNAIL_CACHE
        }
        
        scan_config = ScanConfig(
            enabled_categories=enabled_categories,
            excluded_paths=[],
            custom_patterns=[],
            max_file_age_days=None
        )
        
        return AppConfig(
            scan_config=scan_config,
            ui_theme="light",
            language="zh_CN",
            auto_check_updates=True
        )
    
    def _config_to_dict(self, config: AppConfig) -> Dict[str, Any]:
        """
        将 AppConfig 对象转换为字典
        
        Args:
            config: 应用程序配置
        
        Returns:
            Dict: 配置字典
        """
        return {
            "scan_config": {
                "enabled_categories": [cat.name for cat in config.scan_config.enabled_categories],
                "excluded_paths": config.scan_config.excluded_paths,
                "custom_patterns": config.scan_config.custom_patterns,
                "max_file_age_days": config.scan_config.max_file_age_days
            },
            "ui_theme": config.ui_theme,
            "language": config.language,
            "auto_check_updates": config.auto_check_updates
        }
    
    def _dict_to_config(self, config_dict: Dict[str, Any]) -> AppConfig:
        """
        将字典转换为 AppConfig 对象
        
        Args:
            config_dict: 配置字典
        
        Returns:
            AppConfig: 应用程序配置
        """
        # 解析扫描配置
        scan_config_dict = config_dict.get("scan_config", {})
        
        # 将类别名称转换为枚举
        enabled_categories = set()
        for cat_name in scan_config_dict.get("enabled_categories", []):
            try:
                enabled_categories.add(JunkCategory[cat_name])
            except KeyError:
                logger.warning(f"未知的垃圾类别: {cat_name}")
        
        # 如果没有启用的类别，使用默认配置
        if not enabled_categories:
            logger.warning("配置中没有启用的类别，使用默认配置")
            return self.get_default_config()
        
        scan_config = ScanConfig(
            enabled_categories=enabled_categories,
            excluded_paths=scan_config_dict.get("excluded_paths", []),
            custom_patterns=scan_config_dict.get("custom_patterns", []),
            max_file_age_days=scan_config_dict.get("max_file_age_days")
        )
        
        return AppConfig(
            scan_config=scan_config,
            ui_theme=config_dict.get("ui_theme", "light"),
            language=config_dict.get("language", "zh_CN"),
            auto_check_updates=config_dict.get("auto_check_updates", True)
        )
