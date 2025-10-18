# skills/system_info.py
"""
Compétence informations système
"""
import platform
import sys
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from .base_skill import BaseSkill, SkillResponse


class SystemInfoSkill(BaseSkill):
    """Donne des informations système"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        super().__init__("system_info", "Informations système")
        self.logger = logger or logging.getLogger(__name__)

    def execute(self, **kwargs) -> SkillResponse:
        """Affiche les informations système"""
        message = kwargs.get('message', '').lower()

        if any(word in message for word in ["info", "système", "system"]):
            return self._get_system_info()
        elif any(word in message for word in ["aide", "help"]):
            return self._get_help()
        else:
            return self._get_capabilities()

    def _get_system_info(self) -> SkillResponse:
        """Retourne les informations système"""
        try:
            python_version = platform.python_version()
            system = platform.system()
            current_path = Path.cwd()

            response = [
                "🖥️ **Informations Système :**",
                f"• **Système** : {system}",
                f"• **Python** : {python_version}",
                f"• **Répertoire** : {current_path}",
            ]

            return SkillResponse(
                success=True,
                message="\n".join(response),
                data={
                    "system": system,
                    "python_version": python_version,
                    "current_path": str(current_path)
                }
            )

        except Exception as e:
            self.logger.error(f"Erreur info système: {e}")
            return SkillResponse(
                success=False,
                message="❌ Impossible de récupérer les informations système."
            )

    def _get_capabilities(self) -> SkillResponse:
        """Affiche les capacités"""
        capabilities = [
            "🔧 **Mes capacités :**",
            "",
            "📝 **Gestion de tâches**",
            "  • Ajouter des tâches",
            "  • Lister les tâches",
            "",
            "🧮 **Calculs mathématiques**",
            "  • Opérations basiques",
            "  • Fonctions avancées",
            "",
            "🕐 **Temps et date**",
            "  • Heure actuelle",
            "  • Date du jour",
            "",
            "📁 **Gestion de fichiers**",
            "  • Créer des dossiers",
            "  • Lister les fichiers",
            "",
            "💡 Tapez 'aide' pour plus d'informations"
        ]

        return SkillResponse(
            success=True,
            message="\n".join(capabilities)
        )

    def _get_help(self) -> SkillResponse:
        """Affiche l'aide"""
        help_text = """
**📋 AIDE - Commandes disponibles**

**TÂCHES**
• 'ajoute une tâche [description]'
• 'liste les tâches'

**CALCULS** 
• 'calcule [expression]'
• 'combien fait [expression]'

**TEMPS**
• 'quelle heure est-il ?'
• 'quelle date sommes-nous ?'

**FICHIERS**
• 'crée un dossier [nom]'
• 'liste les fichiers'

**RECHERCHE WEB**
• 'recherche [sujet]'
• 'cherche [sujet]' 
• 'trouve [sujet]'
• 'météo [ville]'


**SYSTÈME**
• 'info système'
• 'aide'
"""
        return SkillResponse(
            success=True,
            message=help_text
        )

    def can_handle(self, intent: str, entities: Dict[str, Any]) -> bool:
        return intent == "system_info"
