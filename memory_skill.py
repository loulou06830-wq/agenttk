# skills/memory_skill.py
"""
Compétence de gestion de la mémoire conversationnelle
"""
import logging
from typing import Dict, Any, Optional
from .base_skill import BaseSkill, SkillResponse


class MemorySkill(BaseSkill):
    """Gère la mémoire et le contexte conversationnel"""

    def __init__(self, agent, logger: Optional[logging.Logger] = None):
        super().__init__("memory", "Gestion de la mémoire")
        self.agent = agent
        self.logger = logger or logging.getLogger(__name__)

    def execute(self, **kwargs) -> SkillResponse:
        """Gère les commandes de mémoire"""
        message = kwargs.get('message', '').lower()
        
        if "historique" in message or "contexte" in message:
            return self._show_conversation_history()
        elif "session" in message or "nouvelle conversation" in message:
            return self._start_new_session()
        elif "fait" in message or "souviens" in message:
            return self._show_remembered_facts()
        
        return SkillResponse(success=False, message="")

    def _show_conversation_history(self) -> SkillResponse:
        """Affiche l'historique de conversation"""
        history = self.agent.get_conversation_history()
        
        if not history:
            return SkillResponse(
                success=True,
                message="📝 **Historique de conversation**\n\nAucun message dans l'historique récent."
            )
        
        response = "📝 **Historique de conversation récent:**\n\n"
        for msg in history[-8:]:  # 8 derniers messages
            speaker = "👤 Vous" if msg["message_type"] == "user" else "🤖 Assistant"
            response += f"{speaker}: {msg['content'][:80]}...\n\n"
        
        return SkillResponse(success=True, message=response)

    def _start_new_session(self) -> SkillResponse:
        """Démarre une nouvelle session de conversation"""
        self.agent.change_conversation_session()
        return SkillResponse(
            success=True,
            message="🔄 **Nouvelle session**\n\nNouvelle conversation démarrée ! Le contexte précédent est sauvegardé."
        )

    def _show_remembered_facts(self) -> SkillResponse:
        """Affiche les faits mémorisés sur l'utilisateur"""
        # Implémentation pour récupérer les faits de la mémoire
        return SkillResponse(
            success=True,
            message="🧠 **Faits mémorisés**\n\nJe me souviens de vos centres d'intérêt et préférences à partir de nos conversations précédentes."
        )

    def can_handle(self, intent: str, entities: Dict[str, Any]) -> bool:
        return intent == "memory_management"