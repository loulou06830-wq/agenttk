# skills/sentiment_skill.py
"""
Analyse de sentiment et adaptation du ton
"""
import logging
from typing import Dict, Any, Optional
from textblob import TextBlob
from .base_skill import BaseSkill, SkillResponse


class SentimentSkill(BaseSkill):
    """Analyse le sentiment et adapte le ton des réponses"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        super().__init__("sentiment", "Analyse de sentiment")
        self.logger = logger or logging.getLogger(__name__)
        
        # Mapping sentiment → style de réponse
        self.ton_mapping = {
            "positive": {
                "style": "enthousiaste",
                "emojis": ["😊", "🎉", "🌟", "💫", "👍"],
                "phrases": ["Super !", "Génial !", "Avec plaisir !", "Excellent !"]
            },
            "neutral": {
                "style": "professionnel", 
                "emojis": ["😐", "💼", "📊", "🔍"],
                "phrases": ["Bien reçu.", "Je comprends.", "Voici les informations."]
            },
            "negative": {
                "style": "empathique",
                "emojis": ["😔", "🤗", "💝", "🫂"],
                "phrases": ["Je comprends votre frustration.", "Je suis là pour vous aider.", "Pardon pour ce désagrément."]
            },
            "angry": {
                "style": "calmant",
                "emojis": ["☮️", "🕊️", "🌊", "🧘"],
                "phrases": ["Je comprends que vous soyez contrarié.", "Prenons cela calmement.", "Je vais vous aider à résoudre ce problème."]
            }
        }

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyse le sentiment d'un texte"""
        try:
            # Utiliser TextBlob pour l'analyse (support français)
            blob = TextBlob(text)
            
            # Score de sentiment (-1 à +1)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Déterminer la catégorie
            if polarity > 0.3:
                sentiment = "positive"
            elif polarity < -0.3:
                if polarity < -0.6:
                    sentiment = "angry"
                else:
                    sentiment = "negative"
            else:
                sentiment = "neutral"
            
            return {
                "sentiment": sentiment,
                "polarity": polarity,
                "subjectivity": subjectivity,
                "confidence": abs(polarity)
            }
            
        except Exception as e:
            self.logger.error(f"Erreur analyse sentiment: {e}")
            return {"sentiment": "neutral", "polarity": 0, "subjectivity": 0, "confidence": 0}

    def adapt_response_ton(self, original_response: str, sentiment: str) -> str:
        """Adapte le ton d'une réponse selon le sentiment"""
        if sentiment not in self.ton_mapping:
            sentiment = "neutral"
            
        ton_config = self.ton_mapping[sentiment]
        
        # Ajouter un préfixe adapté
        import random
        prefix = random.choice(ton_config["phrases"])
        emoji = random.choice(ton_config["emojis"])
        
        # Adapter le style sans changer le contenu informatif
        adapted_response = f"{emoji} {prefix} {original_response}"
        
        return adapted_response

    def execute(self, **kwargs) -> SkillResponse:
        """Analyse le sentiment d'un message"""
        message = kwargs.get('message', '')
        
        if not message:
            return SkillResponse(success=False, message="Aucun message à analyser")
        
        sentiment_data = self.analyze_sentiment(message)
        
        response = (
            f"🎭 **Analyse de Sentiment**\n\n"
            f"**Message:** '{message}'\n"
            f"**Sentiment:** {sentiment_data['sentiment']}\n"
            f"**Score:** {sentiment_data['polarity']:.2f}\n"
            f"**Confiance:** {sentiment_data['confidence']:.2f}"
        )
        
        return SkillResponse(
            success=True,
            message=response,
            data=sentiment_data
        )

    def can_handle(self, intent: str, entities: Dict[str, Any]) -> bool:
        return intent == "sentiment_analysis"