# agent_core/config.py
"""
Gestionnaire de configuration
"""
import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Gestionnaire de configuration"""

    def __init__(self, config_data: Dict[str, Any]):
        self._config = config_data

    def get(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur de configuration"""
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def get_path(self, key: str, default: Optional[str] = None) -> Path:
        """Récupère un chemin"""
        path_str = self.get(key, default)
        if path_str is None:
            raise ValueError(f"Chemin non trouvé: {key}")
        return Path(path_str)

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> 'Config':
        """Charge la configuration"""
        if config_path is None:
            config_path = "config.yaml"

        config_path = Path(config_path)

        if not config_path.exists():
            print(f"⚠️  Fichier {config_path} non trouvé, configuration par défaut")
            return cls.get_default_config()

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            return cls(config_data)
        except Exception as e:
            print(f"⚠️  Erreur lecture config: {e}")
            return cls.get_default_config()

    @classmethod
    def get_default_config(cls) -> 'Config':
        """Configuration par défaut"""
        default_config = {
            'agent': {
                'name': 'AgentTK',
                'version': '1.0.0',
                'language': 'fr'
            },
            'database': {
                'path': 'data/agent.db'
            },
            'nlp': {
                'confidence_threshold': 0.6
            },
            'skills': {
                'enabled': ['calculator', 'time_skill', 'task_manager', 'file_manager', 'system_info']
            },
            'logging': {
                'level': 'INFO'
            }
        }
        return cls(default_config)