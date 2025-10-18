# skills/ml_skill.py
"""
Compétence de gestion de l'apprentissage automatique
"""
import logging
from typing import Dict, Any, Optional
from .base_skill import BaseSkill, SkillResponse


class MLSkill(BaseSkill):
    """Gère l'apprentissage automatique et les statistiques"""
    
    def __init__(self, agent, logger: Optional[logging.Logger] = None):
        super().__init__("ml_skill", "Gestion de l'apprentissage automatique")
        self.agent = agent
        self.logger = logger or logging.getLogger(__name__)
    
    def execute(self, **kwargs) -> SkillResponse:
        """Gère les commandes ML"""
        message = kwargs.get('message', '').lower()
        
        if "statistique" in message or "stats" in message:
            return self._show_stats()
        
        elif "entraînement" in message or "train" in message:
            return self._retrain_model()
        
        elif "feedback" in message:
            return self._show_feedback()
        
        return SkillResponse(success=False, message="")
    
    def _show_stats(self) -> SkillResponse:
        """Affiche les statistiques ML"""
        stats = self.agent.get_ml_stats()
        
        if not stats.get("ml_enabled"):
            return SkillResponse(
                success=True,
                message="🤖 **Apprentissage automatique**\n\n"
                       "❌ Système ML désactivé\n\n"
                       "Activez-le dans config.yaml pour améliorer la reconnaissance d'intentions."
            )
        
        model_info = stats["model"]
        feedback_stats = stats["feedback"]
        
        response = "🤖 **Statistiques Apprentissage Automatique**\n\n"
        
        response += f"📊 **Modèle :**\n"
        response += f"• Entraîné : {'✅' if model_info['is_trained'] else '❌'}\n"
        response += f"• Exemples d'entraînement : {model_info['training_examples']}\n"
        
        if model_info['intents_count']:
            response += f"• Intentions reconnues : {len(model_info['intents_count'])}\n"
        
        response += f"\n📈 **Performance :**\n"
        response += f"• Précision : {feedback_stats.get('accuracy', 0):.1%}\n"
        response += f"• Feedback total : {feedback_stats.get('total_feedback', 0)}\n"
        
        return SkillResponse(success=True, message=response)
    
    def _retrain_model(self) -> SkillResponse:
        """Relance l'entraînement du modèle"""
        if hasattr(self.agent, 'ml_classifier') and self.agent.ml_classifier:
            self.agent.ml_classifier._train_model()
            return SkillResponse(
                success=True,
                message="🔄 **Entraînement ML**\n\n"
                       "Modèle ré-entraîné avec les données actuelles !\n\n"
                       "Utilisez 'stats ml' pour voir les nouvelles statistiques."
            )
        
        return SkillResponse(
            success=False,
            message="❌ Système ML non disponible"
        )
    
    def _show_feedback(self) -> SkillResponse:
        """Affiche les feedbacks récents"""
        stats = self.agent.get_ml_stats()
        
        if not stats.get("ml_enabled"):
            return SkillResponse(success=False, message="")
        
        feedback_stats = stats["feedback"]
        recent_feedback = feedback_stats.get("recent_feedback", [])
        
        response = "📝 **Feedbacks Récents**\n\n"
        
        if not recent_feedback:
            response += "Aucun feedback récent.\n\n"
            response += "Le système apprend de vos interactions automatiquement !"
        else:
            for fb in recent_feedback[-3:]:  # 3 derniers feedbacks
                status = "✅" if fb['was_correct'] else "❌"
                response += f"{status} '{fb['user_message'][:30]}...'\n"
                if not fb['was_correct']:
                    response += f"   Prédit: {fb['predicted_intent']} → Correct: {fb['correct_intent']}\n"
        
        return SkillResponse(success=True, message=response)
    
    def can_handle(self, intent: str, entities: Dict[str, Any]) -> bool:
        return intent == "system_info" and any(word in entities.get("search_query", "") for word in ["ml", "statistique", "entraînement"])
