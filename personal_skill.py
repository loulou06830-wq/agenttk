# skills/personal_skill.py - VERSION CORRIGÉE
"""
Compétence pour les questions personnelles sur l'agent
"""
import logging
from typing import Dict, Any, Optional
from .base_skill import BaseSkill, SkillResponse


class PersonalSkill(BaseSkill):
    """Répond aux questions sur l'agent lui-même"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        super().__init__("personal", "Informations personnelles de l'agent")
        self.logger = logger or logging.getLogger(__name__)
    
    def execute(self, **kwargs) -> SkillResponse:
        """Répond aux questions personnelles"""
        message = kwargs.get('message', '').lower()
        
        self.logger.info(f"Traitement question personnelle: '{message}'")
        
        if any(word in message for word in ["appelle", "nom"]):
            return SkillResponse(
                success=True,
                message="🤖 Je m'appelle **AgentTK** ! Je suis votre assistant IA personnel.\n\n"
                       "Vous pouvez simplement m'appeler **AgentTK** ou me donner le nom que vous préférez ! 😊"
            )
        
        elif any(word in message for word in ["qui es-tu", "tu es qui", "qui es tu"]):
            return SkillResponse(
                success=True,
                message="🤖 **Je suis AgentTK** !\n\n"
                       "• Votre assistant IA personnel\n"
                       "• Développé pour vous aider au quotidien\n"
                       "• Capable de calculs, recherches, gestion de tâches, et bien plus !\n\n"
                       "Tapez 'aide' pour voir tout ce que je peux faire ! 🚀"
            )
        
        elif any(word in message for word in ["faire", "capacité", "capable", "peux"]):
            return SkillResponse(
                success=True,
                message="🔧 **Mes capacités :**\n\n"
                       "🧮 **Calculs** - Calculatrice avancée\n"
                       "🕐 **Temps** - Heure et date actuelles\n"
                       "📝 **Tâches** - Gestion de todo-list\n"
                       "📁 **Fichiers** - Création et listing de dossiers\n"
                       "🔍 **Recherche** - Connaissances + recherche web automatique\n"
                       "🖥️ **Système** - Informations techniques\n"
                       "🤖 **Dialogue** - Conversations intelligentes\n\n"
                       "Tapez 'aide' pour les détails complets ! 📋"
            )
        
        elif any(word in message for word in ["ça va", "comment vas", "comment ça"]):
            return SkillResponse(
                success=True,
                message="😊 Très bien, merci ! Prêt à vous aider.\n\n"
                       "Et vous, comment allez-vous aujourd'hui ?"
            )
        
        # Réponse par défaut pour les questions personnelles non reconnues
        return SkillResponse(
            success=True,
            message="🤖 Je suis **AgentTK**, votre assistant IA !\n\n"
                   "Je peux vous aider avec :\n"
                   "• Des calculs mathématiques 🧮\n"
                   "• La gestion de tâches 📝\n"
                   "• Des recherches d'information 🔍\n"
                   "• La gestion de fichiers 📁\n"
                   "• Et bien plus encore !\n\n"
                   "Tapez 'aide' pour voir toutes mes fonctionnalités !"
        )
    
    def can_handle(self, intent: str, entities: Dict[str, Any]) -> bool:
        return intent == "personal"
