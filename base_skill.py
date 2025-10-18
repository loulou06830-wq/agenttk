# skills/base_skill.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from dataclasses import dataclass


@dataclass
class SkillResponse:
    success: bool
    message: str
    data: Dict[str, Any] = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}


class BaseSkill(ABC):
    """Classe de base pour toutes les compétences"""

    def __init__(self, name: str = None, agent=None, logger: logging.Logger = None):
        self.name = name
        self.agent = agent
        self.logger = logger or logging.getLogger(__name__)

        # Initialisation par défaut si name n'est pas fourni
        if not self.name:
            self.name = self.__class__.__name__.replace('Skill', '').lower()

    def initialize(self, agent):
        """Initialise la compétence avec l'agent"""
        self.agent = agent

    @abstractmethod
    def can_handle(self, intent: str, entities: Dict[str, Any]) -> bool:
        """Détermine si la compétence peut gérer l'intention"""
        pass

    @abstractmethod
    def execute(self, intent: str, message: str, entities: Dict[str, Any]) -> SkillResponse:
        """Exécute la compétence"""
        pass

    def _log(self, level: str, message: str):
        """Méthode de logging helper"""
        if self.logger:
            getattr(self.logger, level)(message)