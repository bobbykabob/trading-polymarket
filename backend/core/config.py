"""
Configuration management for the arbitrage platform
"""

import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging


class ConfigManager:
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self.load_config()
    
    def load_config(self):
        """Load configuration from YAML files"""
        try:
            # Get the project root directory
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "settings.yaml"
            
            if not config_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
            with open(config_path, 'r') as f:
                self._config = yaml.safe_load(f)
                
            logging.info(f"Configuration loaded from {config_path}")
            
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")
            # Load default configuration
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration if files are not found"""
        return {
            "arbitrage": {
                "min_profit_threshold": 0.05,
                "max_position_size": 1000,
                "fee_threshold": 0.001,
                "slippage_buffer": 0.02,
                "alert_cooldown": 300
            },
            "platforms": {
                "polymarket": {
                    "fee_rate": 0.02,
                    "api_rate_limit": 100,
                    "min_volume": 100
                },
                "kalshi": {
                    "fee_rate": 0.01,
                    "api_rate_limit": 50,
                    "min_volume": 50
                }
            },
            "market_matching": {
                "similarity_threshold": 0.8,
                "fuzzy_threshold": 85,
                "semantic_model": "all-MiniLM-L6-v2"
            },
            "monitoring": {
                "update_interval": 30,
                "batch_size": 20,
                "max_concurrent": 5
            },
            "database": {
                "type": "sqlite",
                "path": "data/arbitrage.db"
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'arbitrage.min_profit_threshold')"""
        if self._config is None:
            self.load_config()
        
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_platform_config(self, platform: str) -> Dict[str, Any]:
        """Get platform-specific configuration"""
        return self.get(f"platforms.{platform}", {})
    
    def get_arbitrage_config(self) -> Dict[str, Any]:
        """Get arbitrage-specific configuration"""
        return self.get("arbitrage", {})
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring-specific configuration"""
        return self.get("monitoring", {})
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database-specific configuration"""
        return self.get("database", {})
    
    def update_config(self, key: str, value: Any):
        """Update a configuration value"""
        if self._config is None:
            self.load_config()
        
        keys = key.split('.')
        config = self._config
        
        # Navigate to the parent dictionary
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the final value
        config[keys[-1]] = value
        logging.info(f"Updated config: {key} = {value}")
    
    def save_config(self):
        """Save current configuration back to file"""
        try:
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "settings.yaml"
            
            with open(config_path, 'w') as f:
                yaml.dump(self._config, f, default_flow_style=False)
                
            logging.info(f"Configuration saved to {config_path}")
            
        except Exception as e:
            logging.error(f"Error saving configuration: {e}")


# Global configuration instance
config = ConfigManager()
