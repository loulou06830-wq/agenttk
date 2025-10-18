# skills/file_manager.py
"""
Gestionnaire de fichiers
"""
import os
import re
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from .base_skill import BaseSkill, SkillResponse


class FileManager(BaseSkill):
    """Gère les opérations sur les fichiers"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        super().__init__("file_manager", "Gestion des fichiers")
        self.logger = logger or logging.getLogger(__name__)

    def execute(self, **kwargs) -> SkillResponse:
        """Exécute une opération sur les fichiers"""
        message = kwargs.get('message', '').lower()

        if any(word in message for word in ["creer", "créer", "faire", "dossier"]):
            return self._create_directory(message)
        elif any(word in message for word in ["lister", "afficher", "fichiers"]):
            return self._list_directory()
        else:
            return SkillResponse(
                success=False,
                message="❌ Opération non reconnue. Essayez 'crée un dossier' ou 'liste les fichiers'."
            )

    def _create_directory(self, message: str) -> SkillResponse:
        """Crée un dossier"""
        dir_name = self._extract_directory_name(message)

        if not dir_name:
            return SkillResponse(
                success=False,
                message="❌ Je n'ai pas compris le nom du dossier. Essayez : 'crée un dossier test'"
            )

        try:
            path = Path(dir_name)
            path.mkdir(exist_ok=True, parents=True)

            if path.exists():
                return SkillResponse(
                    success=True,
                    message=f"✅ Dossier créé : '{dir_name}'",
                    data={"directory": str(path.resolve())}
                )
            else:
                return SkillResponse(
                    success=False,
                    message=f"❌ Le dossier '{dir_name}' n'a pas pu être créé"
                )

        except Exception as e:
            self.logger.error(f"Erreur création dossier: {e}")
            return SkillResponse(
                success=False,
                message=f"❌ Erreur lors de la création : {str(e)}"
            )

    def _list_directory(self) -> SkillResponse:
        """Liste le contenu du dossier"""
        try:
            current_dir = Path.cwd()
            items = list(current_dir.iterdir())

            directories = []
            files = []

            for item in items:
                if item.is_dir():
                    directories.append(f"📁 {item.name}/")
                else:
                    files.append(f"📄 {item.name}")

            response_parts = [f"📂 Contenu de {current_dir}:"]

            if directories:
                response_parts.append("\nDossiers:")
                response_parts.extend(directories[:5])

            if files:
                response_parts.append("\nFichiers:")
                response_parts.extend(files[:5])

            if not directories and not files:
                response_parts.append("\n📭 Le dossier est vide")

            return SkillResponse(
                success=True,
                message="\n".join(response_parts)
            )

        except Exception as e:
            self.logger.error(f"Erreur listing dossier: {e}")
            return SkillResponse(
                success=False,
                message=f"❌ Erreur lors du listing : {str(e)}"
            )

    def _extract_directory_name(self, message: str) -> str:
        """Extrait le nom du dossier"""
        patterns = [
            r'(?:creer|créer|faire)\s+(?:un\s+)?(?:dossier|repertoire)\s+(.+)',
            r'crée\s+un\s+dossier\s+(.+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return ""

    def can_handle(self, intent: str, entities: Dict[str, Any]) -> bool:
        return intent == "file_operation"