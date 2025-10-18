# ml/feedback_system.py
"""
Système de feedback pour améliorer l'agent
"""
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
from datetime import datetime


class FeedbackSystem:
    """Système de collecte et gestion du feedback"""
    
    def __init__(self, feedback_path: Path, logger: Optional[logging.Logger] = None):
        self.feedback_path = feedback_path
        self.feedback_path.parent.mkdir(exist_ok=True)
        self.logger = logger or logging.getLogger(__name__)
        self.feedback_data = self._load_feedback_data()
    
    def _load_feedback_data(self) -> List[Dict[str, Any]]:
        """Charge les données de feedback"""
        if self.feedback_path.exists():
            with open(self.feedback_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def add_feedback(self, user_message: str, predicted_intent: str, 
                    correct_intent: str, confidence: float, user_feedback: str = ""):
        """Ajoute un feedback utilisateur"""
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "predicted_intent": predicted_intent,
            "correct_intent": correct_intent,
            "confidence": confidence,
            "user_feedback": user_feedback,
            "was_correct": predicted_intent == correct_intent
        }
        
        self.feedback_data.append(feedback_entry)
        self._save_feedback_data()
        
        self.logger.info(f"Feedback enregistré: {predicted_intent} -> {correct_intent}")
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """Retourne des statistiques sur le feedback"""
        if not self.feedback_data:
            return {"total_feedback": 0, "accuracy": 0}
        
        correct_predictions = sum(1 for f in self.feedback_data if f['was_correct'])
        total_predictions = len(self.feedback_data)
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
        
        return {
            "total_feedback": total_predictions,
            "correct_predictions": correct_predictions,
            "accuracy": accuracy,
            "recent_feedback": self.feedback_data[-5:]  # 5 derniers feedbacks
        }
    
    def _save_feedback_data(self):
        """Sauvegarde les données de feedback"""
        with open(self.feedback_path, 'w', encoding='utf-8') as f:
            json.dump(self.feedback_data, f, ensure_ascii=False, indent=2)
