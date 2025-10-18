# ml/training_data.py
"""
Données d'entraînement pour le classificateur d'intentions
"""
import json
from pathlib import Path
from typing import List, Dict, Any
from skills.base_skill import BaseSkill, SkillResponse


class TrainingData:
    """Gère les données d'entraînement pour le ML"""
    
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.data_path.parent.mkdir(exist_ok=True)
        self.training_examples = self._load_training_data()
    
    def _load_training_data(self) -> List[Dict[str, Any]]:
        """Charge les données d'entraînement depuis le fichier"""
        if self.data_path.exists():
            with open(self.data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Données initiales de base
            base_data = [
                # Salutations
                {"text": "bonjour", "intent": "greeting", "confidence": 1.0},
                {"text": "salut", "intent": "greeting", "confidence": 1.0},
                {"text": "hello", "intent": "greeting", "confidence": 1.0},
                {"text": "coucou", "intent": "greeting", "confidence": 1.0},
                {"text": "bonsoir", "intent": "greeting", "confidence": 1.0},
                
                # Calculs
                {"text": "calcule 2+2", "intent": "calculation", "confidence": 1.0},
                {"text": "combien fait 5*3", "intent": "calculation", "confidence": 1.0},
                {"text": "10/2", "intent": "calculation", "confidence": 1.0},
                {"text": "3.14 * 2", "intent": "calculation", "confidence": 1.0},
                
                # Temps
                {"text": "quelle heure est-il", "intent": "time", "confidence": 1.0},
                {"text": "quelle date sommes-nous", "intent": "time", "confidence": 1.0},
                {"text": "on est quel jour", "intent": "time", "confidence": 1.0},
                
                # Recherche
                {"text": "recherche intelligence artificielle", "intent": "web_search", "confidence": 1.0},
                {"text": "cherche python", "intent": "web_search", "confidence": 1.0},
                {"text": "trouve des informations sur", "intent": "web_search", "confidence": 1.0},
                
                # Tâches
                {"text": "ajoute une tâche", "intent": "task_add", "confidence": 1.0},
                {"text": "nouvelle tâche", "intent": "task_add", "confidence": 1.0},
                {"text": "liste les tâches", "intent": "task_list", "confidence": 1.0},
                
                # Fichiers
                {"text": "crée un dossier", "intent": "file_operation", "confidence": 1.0},
                {"text": "liste les fichiers", "intent": "file_operation", "confidence": 1.0},
                
                # Personnel
                {"text": "qui es-tu", "intent": "personal", "confidence": 1.0},
                {"text": "comment tu t'appelles", "intent": "personal", "confidence": 1.0},
                
                # Au revoir
                {"text": "au revoir", "intent": "farewell", "confidence": 1.0},
                {"text": "bye", "intent": "farewell", "confidence": 1.0},
                {"text": "à plus", "intent": "farewell", "confidence": 1.0},
            ]
            self._save_training_data(base_data)
            return base_data
    
    def add_training_example(self, text: str, intent: str, confidence: float = 1.0):
        """Ajoute un nouvel exemple d'entraînement"""
        self.training_examples.append({
            "text": text.lower(),
            "intent": intent,
            "confidence": confidence
        })
        self._save_training_data(self.training_examples)
    
    def get_training_data(self) -> List[Dict[str, Any]]:
        """Retourne toutes les données d'entraînement"""
        return self.training_examples
    
    def _save_training_data(self, data: List[Dict[str, Any]]):
        """Sauvegarde les données d'entraînement"""
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
