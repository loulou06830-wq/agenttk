# agent_core/agent.py
import logging
import random
import threading
import time
import json
import uuid
from typing import Any, Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass

# === IMPORTS POUR L'ANALYSE DE SENTIMENT ===
try:
    from textblob import TextBlob
    from textblob_fr import PatternTagger, PatternAnalyzer

    SENTIMENT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  TextBlob non disponible: {e}")
    SENTIMENT_AVAILABLE = False

try:
    from skills.self_improvement import SelfImprovementSkill, ImprovementResult

    SELF_IMPROVEMENT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Compétence SelfImprovement non disponible: {e}")
    SELF_IMPROVEMENT_AVAILABLE = False


    # Créer des classes factices pour éviter les erreurs
    class ImprovementResult:
        def __init__(self, success, patterns_added, examples_added, message):
            self.success = success
            self.patterns_added = patterns_added
            self.examples_added = examples_added
            self.message = message


    class SelfImprovementSkill:
        def __init__(self):
            pass

        def improve_intent_recognition(self, intent):
            return ImprovementResult(False, [], [], "SelfImprovement non disponible")

from .config import Config
from .logger import setup_logger
from memory.database import DatabaseManager
from nlp.intent_recognizer import IntentRecognizer
from skills.base_skill import BaseSkill, SkillResponse

import sys
import os

# Ajouter le chemin racine au path Python
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

ML_AVAILABLE = False
MLIntentClassifier = None
FeedbackSystem = None

try:
    from ml.intent_classifier import MLIntentClassifier
    from ml.feedback_system import FeedbackSystem

    ML_AVAILABLE = True
    print("🎉 Modules ML importés avec succès!")
except ImportError as e:
    print(f"⚠️  Impossible d'importer les modules ML: {e}")
    # Essayer une autre méthode d'import
    try:
        import ml.intent_classifier
        import ml.feedback_system

        MLIntentClassifier = ml.intent_classifier.MLIntentClassifier
        FeedbackSystem = ml.feedback_system.FeedbackSystem
        ML_AVAILABLE = True
        print("🎉 Modules ML chargés via import alternatif!")
    except ImportError as e2:
        print(f"❌ Échec des imports ML: {e2}")


@dataclass
class Intent:
    """Représente une intention (pour la compatibilité)"""
    name: str
    confidence: float
    entities: Dict[str, Any]
    skill: str = ""


class Agent:
    """Agent conversationnel intelligent avec ML, Auto-Amélioration, Sentiment et Mémoire"""

    def __init__(self, name: str = "AgentTK", config_path: Optional[str] = None):
        self.name = name
        self.config = Config.load(config_path)

        # Logger
        log_level = self.config.get('logging.level', 'INFO')
        log_file = self.config.get('logging.file')
        self.logger = setup_logger("agent", log_level, log_file)

        # Composants
        self._setup_database()
        self._setup_nlp()
        self._setup_ml_system()
        self.skills = self._initialize_skills()

        # Système d'auto-amélioration
        if SELF_IMPROVEMENT_AVAILABLE:
            self.self_improvement = SelfImprovementSkill()
            self.logger.info("✅ Système d'auto-amélioration initialisé")
        else:
            self.self_improvement = None
            self.logger.warning("⚠️  Système d'auto-amélioration non disponible")

        # === SYSTÈME D'ANALYSE DE SENTIMENT ===
        self.sentiment_available = SENTIMENT_AVAILABLE
        self.sentiment_history = []

        # Mapping des tons selon le sentiment
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
                "phrases": ["Je comprends votre frustration.", "Je suis là pour vous aider.",
                            "Pardon pour ce désagrément."]
            },
            "angry": {
                "style": "calmant",
                "emojis": ["☮️", "🕊️", "🌊", "🧘"],
                "phrases": ["Je comprends que vous soyez contrarié.", "Prenons cela calmement.",
                            "Je vais vous aider à résoudre ce problème."]
            }
        }

        # === SYSTÈME DE MÉMOIRE CONVERSATIONNELLE ===
        self.conversation_memory = {}
        self.current_session_id = self._generate_session_id()
        self.conversation_context = []
        self.max_context_length = 10

        # Faits utilisateur mémorisés
        self.user_facts = {
            "preferences": {},
            "interests": {},
            "conversation_topics": []
        }

        self.logger.info(f"Agent '{name}' initialisé avec auto-amélioration")
        self.logger.info(f"✅ Analyse de sentiment {'activée' if SENTIMENT_AVAILABLE else 'désactivée'}")
        self.logger.info("✅ Mémoire conversationnelle initialisée")

    def _generate_session_id(self) -> str:
        """Génère un ID unique pour la session"""
        return str(uuid.uuid4())[:8]

    def _setup_database(self):
        """Initialise la base de données"""
        db_path = self.config.get_path('database.path')
        self.db = DatabaseManager(db_path, self.logger)

    def _setup_nlp(self):
        """Initialise le NLP"""
        nlp_config = self.config.get('nlp', {})
        self.intent_recognizer = IntentRecognizer(nlp_config, self.logger)

    def _setup_ml_system(self):
        """Initialise le système d'apprentissage automatique"""
        ml_enabled = self.config.get('ml.enabled', True) and ML_AVAILABLE

        if ml_enabled:
            try:
                ml_data_dir = Path("ml_data")
                ml_data_dir.mkdir(exist_ok=True)

                # Classificateur ML
                model_path = ml_data_dir / "intent_classifier.pkl"
                data_path = ml_data_dir / "training_data.json"
                self.ml_classifier = MLIntentClassifier(model_path, data_path, self.logger)

                # Système de feedback
                feedback_path = ml_data_dir / "feedback_data.json"
                self.feedback_system = FeedbackSystem(feedback_path, self.logger)

                self.logger.info("✅ Système ML initialisé")
            except Exception as e:
                self.logger.error(f"❌ Erreur initialisation ML: {e}")
                self.ml_classifier = None
                self.feedback_system = None
        else:
            self.ml_classifier = None
            self.feedback_system = None
            if not ML_AVAILABLE:
                self.logger.info("ℹ️  Module ML non disponible")
            else:
                self.logger.info("ℹ️  Système ML désactivé dans la config")

    def _initialize_skills(self) -> Dict[str, BaseSkill]:
        """Initialise les compétences et les lie entre elles"""
        skills = {}
        enabled_skills = self.config.get('skills.enabled', [])

        skill_mappings = {
            'calculator': ('skills.calculator', 'Calculator'),
            'time_skill': ('skills.time_skill', 'TimeSkill'),
            'task_manager': ('skills.task_manager', 'TaskManager'),
            'file_manager': ('skills.file_manager', 'FileManager'),
            'system_info': ('skills.system_info', 'SystemInfoSkill'),
            'web_search': ('skills.web_search', 'WebSearchSkill'),
            'knowledge': ('skills.knowledge_skill', 'KnowledgeSkill'),
            'personal': ('skills.personal_skill', 'PersonalSkill'),
            'self_improvement': ('skills.self_improvement', 'SelfImprovementSkill'),
        }

        # D'abord créer toutes les compétences
        for skill_name in enabled_skills:
            if skill_name in skill_mappings:
                module_path, class_name = skill_mappings[skill_name]
                try:
                    module = __import__(module_path, fromlist=[class_name])
                    skill_class = getattr(module, class_name)

                    if skill_name == 'task_manager':
                        skills[skill_name] = skill_class(self.db, self.logger)
                    else:
                        skills[skill_name] = skill_class(self.logger)

                    self.logger.info(f"✅ Compétence chargée: {skill_name}")

                except Exception as e:
                    self.logger.warning(f"Impossible de charger {skill_name}: {e}")

        # Ensuite lier les compétences entre elles
        if 'knowledge' in skills and 'web_search' in skills:
            skills['knowledge'].set_web_search_skill(skills['web_search'])
            self.logger.info("✅ Compétences Knowledge et WebSearch liées")

        return skills

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyse le sentiment d'un texte"""
        if not self.sentiment_available:
            return {"sentiment": "neutral", "polarity": 0, "confidence": 0}

        try:
            # Utiliser TextBlob avec analyseur français
            blob = TextBlob(text, analyzer=PatternAnalyzer(), pos_tagger=PatternTagger())

            polarity = blob.sentiment[0]  # Score entre -1 et +1

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
                "confidence": abs(polarity),
                "timestamp": time.time()
            }

        except Exception as e:
            self.logger.error(f"Erreur analyse sentiment: {e}")
            return {"sentiment": "neutral", "polarity": 0, "confidence": 0}

    def adapt_response_ton(self, original_response: str, sentiment: str) -> str:
        """Adapte le ton d'une réponse selon le sentiment"""
        if sentiment not in self.ton_mapping:
            sentiment = "neutral"

        ton_config = self.ton_mapping[sentiment]

        # Ajouter un préfixe adapté (aléatoire pour variété)
        prefix = random.choice(ton_config["phrases"])
        emoji = random.choice(ton_config["emojis"])

        # Adapter le style sans changer le contenu informatif
        adapted_response = f"{emoji} {prefix} {original_response}"

        return adapted_response

    def _update_conversation_memory(self, message: str, response: str, intent: str, sentiment: str):
        """Met à jour la mémoire de conversation"""
        # Ajouter au contexte récent
        conversation_entry = {
            "timestamp": time.time(),
            "user_message": message,
            "agent_response": response,
            "intent": intent,
            "sentiment": sentiment
        }

        self.conversation_context.append(conversation_entry)

        # Garder seulement les N derniers messages
        if len(self.conversation_context) > self.max_context_length:
            self.conversation_context = self.conversation_context[-self.max_context_length:]

        # Extraire et mémoriser des faits utilisateur
        self._extract_user_facts(message, intent, sentiment)

    def _extract_user_facts(self, message: str, intent: str, sentiment: str):
        """Extrait des faits utilisateur du message"""
        message_lower = message.lower()

        # Mémoriser les centres d'intérêt des recherches
        if intent == "web_search":
            # Extraire le sujet de recherche comme intérêt
            if "python" in message_lower:
                self.user_facts["interests"]["programming"] = self.user_facts["interests"].get("programming", 0) + 1
            if "ia" in message_lower or "intelligence artificielle" in message_lower:
                self.user_facts["interests"]["ai"] = self.user_facts["interests"].get("ai", 0) + 1
            if "jeu" in message_lower or "gaming" in message_lower:
                self.user_facts["interests"]["gaming"] = self.user_facts["interests"].get("gaming", 0) + 1

        # Mémoriser les préférences de ton
        if sentiment in ["positive", "negative"]:
            self.user_facts["preferences"]["tone_preference"] = sentiment

        # Sujets de conversation récurrents
        if intent not in ["greeting", "thanks", "farewell"]:
            self.user_facts["conversation_topics"].append({
                "topic": intent,
                "timestamp": time.time(),
                "message": message[:50] + "..." if len(message) > 50 else message
            })

    def _enhance_with_memory(self, response: str, intent: str, current_message: str) -> str:
        """Améliore la réponse avec la mémoire conversationnelle"""
        enhanced_response = response

        # Référence au contexte précédent pour la continuité
        if len(self.conversation_context) >= 2:
            last_intent = self.conversation_context[-1]["intent"]

            # Si l'utilisateur poursuit le même sujet
            if last_intent == intent and intent in ["web_search", "calculation"]:
                enhanced_response = f"🔍 Suite à votre demande précédente : {response}"

        # Personnalisation basée sur les intérêts connus
        user_interests = list(self.user_facts["interests"].keys())
        if user_interests:
            top_interest = max(self.user_facts["interests"],
                               key=self.user_facts["interests"].get,
                               default=None)

            if top_interest and top_interest in current_message.lower():
                if top_interest == "programming":
                    enhanced_response = f"💻 En tant que passionné de programmation : {response}"
                elif top_interest == "ai":
                    enhanced_response = f"🧠 Vu votre intérêt pour l'IA : {response}"

        return enhanced_response

    def _save_interaction_with_sentiment(self, message: str, response: str, intent: str,
                                         confidence: float, sentiment_data: Dict):
        """Sauvegarde une interaction avec données de sentiment (méthode CORRIGÉE)"""
        try:
            # Essayer d'abord avec les arguments positionnels (méthode standard)
            self.db.save_interaction(message, response, intent, confidence)

            # Sauvegarder les données de sentiment séparément
            self._save_sentiment_data(message, response, intent, confidence, sentiment_data)

        except Exception as e:
            self.logger.error(f"❌ Erreur sauvegarde interaction: {e}")
            # Sauvegarder quand même les données de sentiment
            self._save_sentiment_data(message, response, intent, confidence, sentiment_data)

    def _save_sentiment_data(self, message: str, response: str, intent: str,
                             confidence: float, sentiment_data: Dict):
        """Sauvegarde les données de sentiment dans un fichier séparé"""
        try:
            sentiment_dir = Path("ml_data")
            sentiment_dir.mkdir(exist_ok=True)

            sentiment_file = sentiment_dir / "sentiment_log.json"

            sentiments = []
            if sentiment_file.exists():
                try:
                    with open(sentiment_file, 'r', encoding='utf-8') as f:
                        sentiments = json.load(f)
                except Exception as e:
                    self.logger.warning(f"⚠️  Impossible de lire le fichier sentiment: {e}")
                    sentiments = []

            sentiment_entry = {
                "timestamp": time.time(),
                "session_id": self.current_session_id,
                "message": message,
                "response": response,
                "intent": intent,
                "confidence": confidence,
                "sentiment": sentiment_data["sentiment"],
                "polarity": sentiment_data["polarity"],
                "confidence_sentiment": sentiment_data["confidence"],
                "ml_used": self.ml_classifier is not None and self.ml_classifier.is_trained
            }

            sentiments.append(sentiment_entry)

            # Garder seulement les 1000 dernières entrées
            if len(sentiments) > 1000:
                sentiments = sentiments[-1000:]

            with open(sentiment_file, 'w', encoding='utf-8') as f:
                json.dump(sentiments, f, ensure_ascii=False, indent=2)

            self.logger.info(f"💾 Données de sentiment sauvegardées pour: {message[:30]}...")

        except Exception as e:
            self.logger.error(f"❌ Erreur sauvegarde données sentiment: {e}")

    def auto_improve_intent(self, intent_name: str) -> ImprovementResult:
        """Améliore automatiquement une intention via recherche web"""
        if not self.self_improvement:
            return ImprovementResult(False, [], [], "Système d'auto-amélioration non disponible")

        try:
            result = self.self_improvement.improve_intent_recognition(intent_name)

            if result.success:
                # Ajouter les nouveaux patterns au système de règles
                patterns_added = 0
                if hasattr(self.intent_recognizer, 'add_pattern'):
                    for pattern in result.patterns_added:
                        if self.intent_recognizer.add_pattern(intent_name, pattern):
                            patterns_added += 1
                            self.logger.info(f"➕ Pattern ajouté pour {intent_name}: {pattern}")
                else:
                    self.logger.warning("⚠️  Méthode add_pattern non disponible dans IntentRecognizer")

                # Ajouter les exemples d'entraînement ML
                examples_added = 0
                if self.ml_classifier and hasattr(self.ml_classifier, 'add_training_example'):
                    for example in result.examples_added:
                        # Gérer différents formats d'exemples
                        if isinstance(example, dict):
                            text = example.get("text", "")
                            intent = example.get("intent", intent_name)
                        else:
                            text = str(example)
                            intent = intent_name

                        if text and len(text.strip()) > 0:
                            success = self.ml_classifier.add_training_example(text.strip(), intent)
                            if success:
                                examples_added += 1
                                self.logger.info(f"➕ Exemple ML: '{text}' → {intent}")

                # Mettre à jour le message de résultat
                if patterns_added > 0 or examples_added > 0:
                    result.message = f"✅ Auto-amélioration réussie!\n• {patterns_added} patterns ajoutés\n• {examples_added} exemples d'entraînement\n• Intentions: {intent_name}"

                    # Sauvegarder les améliorations
                    self._save_improvements(intent_name, result)
                else:
                    result = ImprovementResult(False, [], [],
                                               "Aucune amélioration appliquée (patterns ou exemples vides)")

            return result

        except Exception as e:
            error_msg = f"Erreur lors de l'auto-amélioration: {str(e)}"
            self.logger.error(error_msg)
            return ImprovementResult(False, [], [], error_msg)

    def _save_improvements(self, intent_name: str, result: ImprovementResult):
        """Sauvegarde les améliorations dans un fichier"""
        try:
            improvements_dir = Path("ml_data")
            improvements_dir.mkdir(exist_ok=True)

            improvements_file = improvements_dir / "improvements.json"
            improvements_data = {}

            if improvements_file.exists():
                try:
                    with open(improvements_file, 'r', encoding='utf-8') as f:
                        improvements_data = json.load(f)
                except:
                    improvements_data = {}

            if intent_name not in improvements_data:
                improvements_data[intent_name] = []

            improvements_data[intent_name].append({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "patterns_added": result.patterns_added,
                "examples_added": len(result.examples_added),
                "message": result.message
            })

            with open(improvements_file, 'w', encoding='utf-8') as f:
                json.dump(improvements_data, f, ensure_ascii=False, indent=2)

            self.logger.info(f"💾 Améliorations sauvegardées pour {intent_name}")

        except Exception as e:
            self.logger.error(f"❌ Erreur sauvegarde améliorations: {e}")

    def improve_unknown_intent(self, user_message: str) -> Optional[str]:
        """Améliore les intentions inconnues en devinant l'intention"""
        if not self.self_improvement:
            return None

        guessed_intent = self._guess_intent_from_context(user_message)

        if guessed_intent and guessed_intent != "unknown":
            self.logger.info(f"🤔 Auto-amélioration devinée: '{user_message}' → {guessed_intent}")
            result = self.auto_improve_intent(guessed_intent)

            # Ajouter ce message comme exemple
            if self.ml_classifier and hasattr(self.ml_classifier, 'add_training_example'):
                self.ml_classifier.add_training_example(user_message, guessed_intent)

            if result.success:
                return f"🔧 Auto-amélioration: '{user_message}' → {guessed_intent}"

        return None

    def _guess_intent_from_context(self, message: str) -> str:
        """Devine l'intention basée sur le contenu du message"""
        message_lower = message.lower()

        if any(word in message_lower for word in
               ['bonjour', 'salut', 'coucou', 'hello', 'salu', 'hey', 'comment ça va', 'sa va']):
            return "greeting"
        elif any(word in message_lower for word in
                 ['cherche', 'recherche', 'trouve', 'information', 'c est quoi', 'qui est', 'résume', 'resume',
                  'donne info']):
            return "web_search"
        elif any(word in message_lower for word in
                 ['calcule', 'calcul', 'combien', 'addition', 'soustraction', 'fois', 'divisé', 'math']):
            return "calculation"
        elif any(word in message_lower for word in ['heure', 'date', 'temps', 'quel jour', 'quelle heure']):
            return "time"
        elif any(word in message_lower for word in ['tâche', 'todo', 'ajoute', 'liste', 'rappelle']):
            return "task_add"
        elif any(word in message_lower for word in ['merci', 'remercie', 'thanks']):
            return "thanks"

        return "unknown"

    def _preprocess_message(self, message: str) -> str:
        """Corrige les fautes d'orthographe courantes"""
        corrections = {
            'sa va': 'ça va',
            'combiens': 'combien',
            'combient': 'combien',
            'egale': 'égale',
            'apprend': 'apprends',
            'salu': 'salut',
            'bounjour': 'bonjour',
            'bonsoir': 'bonsoir',
            'svp': 's\'il vous plaît',
            'stp': 's\'il te plaît',
            'c est': 'c\'est',
            'j ai': 'j\'ai',
            'd accord': 'd\'accord',
            'est ce que': 'est-ce que',
            'qu elle': 'qu\'elle',
            'lorsque je': 'quand je',
            'lorsqu il': 'quand il',
            'comment va tu': 'comment vas-tu',
            'comment vas tu': 'comment vas-tu',
            'resume': 'résume',
            'c est quoi': 'c\'est quoi',
            'qu est ce': 'qu\'est-ce',
            'commen': 'comment',
        }

        message_lower = message.lower()
        for wrong, correct in corrections.items():
            if wrong in message_lower:
                message = message.replace(wrong, correct)

        return message

    def process_message(self, message: str) -> str:
        """Traite un message utilisateur avec analyse de sentiment et mémoire"""
        message = self._preprocess_message(message.strip())

        if not message:
            return "Je n'ai pas reçu de message."

        self.logger.info(f"Message reçu: {message}")

        # ÉTAPE 1: Analyse de sentiment
        sentiment_data = self.analyze_sentiment(message)
        self.sentiment_history.append({
            "message": message,
            "sentiment": sentiment_data,
            "timestamp": time.time()
        })

        self.logger.info(f"Sentiment détecté: {sentiment_data['sentiment']} (score: {sentiment_data['polarity']:.2f})")

        # ÉTAPE 2: Reconnaissance d'intention
        intent_result = self._recognize_intent_with_ml(message)
        self.logger.info(f"Intention détectée: {intent_result.name} ({intent_result.confidence:.2f})")

        # ÉTAPE 3: Auto-amélioration si intention inconnue
        if intent_result.name == "unknown" and intent_result.confidence < 0.3:
            improvement_msg = self.improve_unknown_intent(message)
            if improvement_msg:
                self.logger.info(improvement_msg)

        # ÉTAPE 4: Traitement par compétence
        response = self._handle_with_skill(intent_result, message)

        # ÉTAPE 5: Réponse par défaut si nécessaire
        if not response:
            response = self._get_default_response(intent_result)

        # ÉTAPE 6: Amélioration avec mémoire conversationnelle
        response_with_memory = self._enhance_with_memory(response, intent_result.name, message)

        # ÉTAPE 7: Adaptation du ton selon le sentiment
        final_response = self.adapt_response_ton(response_with_memory, sentiment_data["sentiment"])

        # ÉTAPE 8: Mise à jour de la mémoire
        self._update_conversation_memory(message, final_response, intent_result.name, sentiment_data["sentiment"])

        # ÉTAPE 9: Sauvegarde CORRIGÉE
        self._save_interaction_with_sentiment(
            message=message,
            response=final_response,
            intent=intent_result.name,
            confidence=intent_result.confidence,
            sentiment_data=sentiment_data
        )

        return final_response

    def _recognize_intent_with_ml(self, message: str) -> Intent:
        """Reconnaît l'intention en combinant règles et ML"""
        # D'abord utiliser le système basé sur les règles
        rule_result = self.intent_recognizer.recognize(message)

        # Si ML disponible et entraîné, combiner avec prédiction ML
        if self.ml_classifier and self.ml_classifier.is_trained:
            ml_intent, ml_confidence = self.ml_classifier.predict(message)
            self.logger.info(f"ML prediction: {ml_intent} (confiance: {ml_confidence:.2f})")

            # Combiner les résultats - ML a priorité si confiance élevée
            if ml_confidence > 0.7 and ml_confidence > rule_result.confidence:
                final_intent = ml_intent
                final_confidence = ml_confidence
                method = "ml"
            else:
                final_intent = rule_result.name
                final_confidence = rule_result.confidence
                method = "rules"
        else:
            # Utiliser uniquement les règles
            final_intent = rule_result.name
            final_confidence = rule_result.confidence
            method = "rules"

        self.logger.info(f"Intention finale: {final_intent} (confiance: {final_confidence:.2f}, méthode: {method})")

        # Extraire les entités (toujours avec le système règles)
        entities = self._extract_entities(message, final_intent)

        return Intent(
            name=final_intent,
            confidence=final_confidence,
            entities=entities,
            skill=self._get_skill_for_intent(final_intent)
        )

    def _extract_entities(self, text: str, intent: str) -> Dict[str, Any]:
        """Extrait les entités pour une intention donnée"""
        # Utiliser la méthode d'extraction du recognizer existant
        return self.intent_recognizer._extract_entities(text, intent)

    def _get_skill_for_intent(self, intent: str) -> str:
        """Retourne la compétence associée à une intention"""
        skill_mapping = {
            "greeting": "greeting",
            "calculation": "calculator",
            "time": "time_skill",
            "task_add": "task_manager",
            "task_list": "task_manager",
            "file_operation": "file_manager",
            "system_info": "system_info",
            "web_search": "web_search",
            "personal": "personal",
            "farewell": "farewell",
            "thanks": "thanks",
            "unknown": "fallback"
        }
        return skill_mapping.get(intent, "fallback")

    def _handle_with_skill(self, intent_result, message: str) -> Optional[str]:
        """Traite avec une compétence - ORDRE AMÉLIORÉ"""
        # Pour les recherches web, utiliser knowledge en premier (avec fallback web intégré)
        if intent_result.name == "web_search" and intent_result.entities.get("search_query"):
            if "knowledge" in self.skills:
                knowledge_result = self.skills["knowledge"].execute(
                    intent=intent_result.name,
                    message=message,
                    entities=intent_result.entities
                )
                if knowledge_result.success and knowledge_result.message:
                    return knowledge_result.message

        # Ensuite la compétence spécifique
        if intent_result.skill in self.skills:
            skill = self.skills[intent_result.skill]
            try:
                result = skill.execute(
                    intent=intent_result.name,
                    message=message,
                    entities=intent_result.entities
                )
                if result.success:
                    return result.message
            except Exception as e:
                self.logger.error(f"Erreur compétence {intent_result.skill}: {e}")

        # Enfin les autres compétences
        for skill_name, skill in self.skills.items():
            if (skill_name != intent_result.skill and
                    skill_name != "knowledge" and  # Éviter de refaire knowledge
                    skill.can_handle(intent_result.name, intent_result.entities)):
                try:
                    result = skill.execute(
                        intent=intent_result.name,
                        message=message,
                        entities=intent_result.entities
                    )
                    if result.success:
                        return result.message
                except Exception as e:
                    self.logger.error(f"Erreur compétence {skill_name}: {e}")

        return None

    def _get_default_response(self, intent_result) -> str:
        """Réponse par défaut améliorée"""
        default_responses = {
            "greeting": [
                f"Bonjour ! Je suis {self.name}, votre assistant IA.",
                f"Salut ! Comment puis-je vous aider ?",
                f"Hello ! {self.name} à votre service.",
                f"Bonjour ! Je suis là pour vous assister."
            ],
            "farewell": [
                "Au revoir ! À bientôt !",
                "Bonne journée !",
                "À la prochaine !",
                "Salut ! À très vite !"
            ],
            "thanks": [
                "Je vous en prie ! 😊",
                "Avec plaisir ! 👍",
                "Tout le plaisir est pour moi ! 🌟",
                "De rien ! N'hésitez pas si vous avez d'autres questions. 💫"
            ],
            "unknown": [
                "Je ne suis pas sûr de comprendre. Pouvez-vous reformuler ?",
                "Désolé, je n'ai pas saisi votre demande.",
                "Pouvez-vous préciser ce que vous voulez dire ?",
                "Je n'ai pas compris. Essayez avec d'autres mots ou tapez 'aide' pour voir mes capacités.",
                "Je n'ai pas bien compris. Pouvez-vous reformuler votre question ?"
            ]
        }

        responses = default_responses.get(intent_result.name, default_responses["unknown"])
        return random.choice(responses)

    def provide_feedback(self, user_message: str, predicted_intent: str, correct_intent: str):
        """Permet de fournir du feedback pour améliorer le ML"""
        try:
            # Ajouter aux données d'entraînement ML
            if self.ml_classifier and hasattr(self.ml_classifier, 'add_training_example'):
                self.ml_classifier.add_training_example(user_message, correct_intent)

            # Enregistrer le feedback
            if self.feedback_system:
                self.feedback_system.add_feedback(
                    user_message, predicted_intent, correct_intent, 0.0
                )

            # Si correction, lancer l'auto-amélioration en arrière-plan
            if predicted_intent != correct_intent and self.self_improvement:
                self.logger.info(f"🔧 Correction détectée, auto-amélioration pour {correct_intent}")

                def auto_improve_background():
                    try:
                        result = self.auto_improve_intent(correct_intent)
                        if result.success:
                            self.logger.info(f"✅ Auto-amélioration réussie pour {correct_intent}")
                    except Exception as e:
                        self.logger.error(f"❌ Erreur auto-amélioration: {e}")

                # Lancer en arrière-plan
                thread = threading.Thread(target=auto_improve_background, daemon=True)
                thread.start()

            self.logger.info(f"✅ Feedback enregistré: {predicted_intent} -> {correct_intent}")

        except Exception as e:
            self.logger.error(f"❌ Erreur enregistrement feedback: {e}")

    def get_conversation_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de conversation"""
        if not self.conversation_context:
            return {"message_count": 0, "session_id": self.current_session_id}

        # Analyser le contexte de conversation
        intent_counts = {}
        sentiment_counts = {}

        for entry in self.conversation_context:
            intent = entry["intent"]
            sentiment = entry.get("sentiment", "neutral")

            intent_counts[intent] = intent_counts.get(intent, 0) + 1
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1

        return {
            "session_id": self.current_session_id,
            "message_count": len(self.conversation_context),
            "intent_distribution": intent_counts,
            "sentiment_distribution": sentiment_counts,
            "user_interests": self.user_facts["interests"],
            "topics_discussed": len(self.user_facts["conversation_topics"])
        }

    def get_ml_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du système ML"""
        if self.ml_classifier and self.feedback_system:
            try:
                model_info = self.ml_classifier.get_model_info()
                feedback_stats = self.feedback_system.get_feedback_stats()

                return {
                    "ml_enabled": True,
                    "model": model_info,
                    "feedback": feedback_stats
                }
            except Exception as e:
                self.logger.error(f"Erreur récupération stats ML: {e}")
                return {"ml_enabled": False, "error": str(e)}
        else:
            return {"ml_enabled": False}

    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques complètes"""
        base_stats = {
            "agent_name": self.name,
            "skills_loaded": list(self.skills.keys()),
            "config": {
                "language": self.config.get('agent.language'),
                "version": self.config.get('agent.version')
            },
            "self_improvement": SELF_IMPROVEMENT_AVAILABLE
        }

        # Ajouter les stats ML si disponible
        ml_stats = self.get_ml_stats()
        base_stats["ml"] = ml_stats

        return base_stats

    def get_enhanced_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques complètes avec mémoire et sentiment"""
        base_stats = self.get_stats()

        # Ajouter les nouvelles métriques
        base_stats["sentiment_analysis"] = {
            "enabled": self.sentiment_available,
            "recent_analysis": self.sentiment_history[-5:] if self.sentiment_history else []
        }

        base_stats["conversation_memory"] = self.get_conversation_stats()

        return base_stats

    def start_new_conversation(self):
        """Démarre une nouvelle conversation (nouveau contexte)"""
        old_session = self.current_session_id
        self.current_session_id = self._generate_session_id()
        self.conversation_context = []

        self.logger.info(f"🔄 Nouvelle conversation: {old_session} → {self.current_session_id}")
        return self.current_session_id

    def get_conversation_history(self) -> List[Dict]:
        """Retourne l'historique complet pour l'UI"""
        return self.conversation_context

    def get_user_profile(self) -> Dict[str, Any]:
        """Retourne le profil utilisateur basé sur la mémoire"""
        top_interests = sorted(
            self.user_facts["interests"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]  # Top 3 intérêts

        return {
            "preferred_tone": self.user_facts["preferences"].get("tone_preference", "neutral"),
            "top_interests": [interest[0] for interest in top_interests],
            "conversation_count": len(self.conversation_context),
            "frequent_intents": list(set([ctx["intent"] for ctx in self.conversation_context]))
        }

    def retrain_ml_model(self):
        """Force le ré-entraînement du modèle ML"""
        if self.ml_classifier:
            try:
                self.ml_classifier.train()
                self.logger.info("✅ Modèle ML ré-entraîné")
                return True
            except Exception as e:
                self.logger.error(f"❌ Erreur ré-entraînement ML: {e}")
                return False
        return False