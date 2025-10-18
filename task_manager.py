# skills/task_manager.py
"""
Gestionnaire de tâches
"""
import re
import logging
from typing import Dict, Any, Optional
from .base_skill import BaseSkill, SkillResponse
from memory.database import DatabaseManager


class TaskManager(BaseSkill):
    """Gestionnaire de tâches"""

    def __init__(self, db: DatabaseManager, logger: Optional[logging.Logger] = None):
        super().__init__("task_manager", "Gestion des tâches")
        self.db = db
        self.logger = logger or logging.getLogger(__name__)

    def execute(self, **kwargs) -> SkillResponse:
        """Exécute une opération sur les tâches"""
        intent = kwargs.get('intent', '')
        message = kwargs.get('message', '')
        entities = kwargs.get('entities', {})

        if intent == "task_add":
            return self._add_task(entities, message)
        elif intent == "task_list":
            return self._list_tasks()
        else:
            return SkillResponse(
                success=False,
                message="Je ne sais pas quelle action de tâche effectuer."
            )

    def _add_task(self, entities: Dict[str, Any], message: str) -> SkillResponse:
        """Ajoute une tâche"""
        task_description = entities.get("task_description", "")

        if not task_description:
            task_description = self._extract_task_description(message)
            if not task_description:
                return SkillResponse(
                    success=False,
                    message="Je n'ai pas compris quelle tâche ajouter. Exemple: 'ajoute une tâche faire les courses'"
                )

        task_id = self.db.add_task(task_description.strip())

        if task_id > 0:
            return SkillResponse(
                success=True,
                message=f"✅ Tâche ajoutée : '{task_description}' (ID: {task_id})",
                data={"task_id": task_id}
            )
        else:
            return SkillResponse(
                success=False,
                message="❌ Erreur lors de l'ajout de la tâche."
            )

    def _list_tasks(self) -> SkillResponse:
        """Liste les tâches"""
        tasks = self.db.get_pending_tasks()

        if not tasks:
            return SkillResponse(
                success=True,
                message="📝 Aucune tâche en attente !"
            )

        response = "📋 Vos tâches en attente :\n"
        for task in tasks:
            response += f"• {task['title']} (ID: {task['id']})\n"

        return SkillResponse(
            success=True,
            message=response,
            data={"tasks": tasks, "count": len(tasks)}
        )

    def _extract_task_description(self, message: str) -> str:
        """Extrait la description de la tâche"""
        description = re.sub(
            r'ajouter|creer|nouvelle|tache|todo',
            '', message, flags=re.IGNORECASE
        )
        return description.strip()

    def can_handle(self, intent: str, entities: Dict[str, Any]) -> bool:
        return intent.startswith("task_")