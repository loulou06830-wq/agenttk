# ml/intent_classifier.py
import json
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Any
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd


class MLIntentClassifier:
    """Classificateur d'intentions par apprentissage automatique"""

    def __init__(self, model_path: Path, data_path: Path, logger: logging.Logger = None):
        self.model_path = Path(model_path)
        self.data_path = Path(data_path)
        self.logger = logger or logging.getLogger(__name__)

        self.vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False
        self.intents = []

        self._load_model()

    def _load_model(self):
        """Charge le modèle existant ou en initialise un nouveau"""
        try:
            if self.model_path.exists():
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)

                self.vectorizer = model_data['vectorizer']
                self.classifier = model_data['classifier']
                self.intents = model_data['intents']
                self.is_trained = model_data['is_trained']

                if self.logger:
                    self.logger.info(f"✅ Modèle ML chargé depuis {self.model_path}")
                    self.logger.info(f"📊 {len(self.intents)} intentions disponibles")
            else:
                if self.logger:
                    self.logger.info("🆕 Nouveau modèle ML initialisé")

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur chargement modèle: {e}")
            self.is_trained = False

    def _save_model(self):
        """Sauvegarde le modèle entraîné"""
        try:
            model_data = {
                'vectorizer': self.vectorizer,
                'classifier': self.classifier,
                'intents': self.intents,
                'is_trained': self.is_trained
            }

            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)

            if self.logger:
                self.logger.info(f"💾 Modèle ML sauvegardé dans {self.model_path}")

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur sauvegarde modèle: {e}")

    def _load_training_data(self) -> Tuple[List[str], List[str]]:
        """Charge les données d'entraînement"""
        texts, labels = [], []

        try:
            if self.data_path.exists():
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Vérifier la structure des données
                if isinstance(data, dict) and 'intents' in data:
                    for intent_name, intent_data in data['intents'].items():
                        if isinstance(intent_data, dict) and 'patterns' in intent_data:
                            for pattern in intent_data['patterns']:
                                if isinstance(pattern, str):
                                    texts.append(pattern)
                                    labels.append(intent_name)

                if self.logger:
                    self.logger.info(f"📚 {len(texts)} exemples d'entraînement chargés")
            else:
                if self.logger:
                    self.logger.warning("📂 Aucun fichier de données d'entraînement trouvé")
                self._create_default_data()

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur chargement données: {e}")
            # Créer une structure vide si le fichier est corrompu
            self._create_default_data()

        return texts, labels

    def _create_default_data(self):
        """Crée une structure de données par défaut"""
        try:
            default_data = {
                "intents": {
                    "greeting": {
                        "patterns": ["bonjour", "salut", "hello", "coucou", "hey", "bonsoir"],
                        "responses": ["Bonjour !", "Salut !", "Hello !", "Coucou !"]
                    },
                    "thanks": {
                        "patterns": ["merci", "merci beaucoup", "thanks", "merci bien"],
                        "responses": ["De rien !", "Je vous en prie !", "Avec plaisir !"]
                    },
                    "web_search": {
                        "patterns": ["cherche", "recherche", "trouve", "c'est quoi", "qui est"],
                        "responses": []
                    }
                }
            }

            self.data_path.parent.mkdir(exist_ok=True)
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=2)

            if self.logger:
                self.logger.info("📝 Données par défaut créées")

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur création données par défaut: {e}")

    def train(self) -> bool:
        """Entraîne le modèle avec les données disponibles"""
        try:
            texts, labels = self._load_training_data()

            if len(texts) < 5:
                if self.logger:
                    self.logger.warning(f"⚠️  Données insuffisantes: {len(texts)} exemples")
                self.is_trained = False
                return False

            # Préparer les données
            self.intents = list(set(labels))

            if len(self.intents) < 2:
                if self.logger:
                    self.logger.warning("⚠️  Pas assez d'intentions différentes")
                self.is_trained = False
                return False

            # Vectoriser les textes
            X = self.vectorizer.fit_transform(texts)
            y = labels

            # Diviser en train/test
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )

            # Entraîner le modèle
            self.classifier.fit(X_train, y_train)

            # Évaluer
            y_pred = self.classifier.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)

            self.is_trained = True
            self._save_model()

            if self.logger:
                self.logger.info(f"🎯 Modèle entraîné - Précision: {accuracy:.2%}")
                self.logger.info(f"📊 Intentions: {len(self.intents)}")
                self.logger.info(f"📈 Exemples: {len(texts)}")

            return True

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur entraînement: {e}")
            self.is_trained = False
            return False

    def predict(self, text: str) -> Tuple[str, float]:
        """Prédit l'intention d'un texte"""
        if not self.is_trained:
            return "unknown", 0.0

        try:
            # Vectoriser le texte
            X = self.vectorizer.transform([text])

            # Prédire
            probabilities = self.classifier.predict_proba(X)[0]
            predicted_index = np.argmax(probabilities)
            confidence = probabilities[predicted_index]

            # Récupérer le nom de l'intention
            intent_name = self.classifier.classes_[predicted_index]

            # Seuil de confiance
            if confidence < 0.3:
                return "unknown", confidence

            return intent_name, confidence

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur prédiction: {e}")
            return "unknown", 0.0

    def add_training_example(self, text: str, intent: str, entities: List[Dict] = None) -> bool:
        """Ajoute un exemple d'entraînement au dataset"""
        try:
            # Charger les données existantes
            if self.data_path.exists():
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {"intents": {}}

            # Vérifier la structure
            if not isinstance(data, dict):
                data = {"intents": {}}
            if "intents" not in data:
                data["intents"] = {}

            # Ajouter l'exemple
            if intent not in data["intents"]:
                data["intents"][intent] = {"patterns": [], "responses": []}

            # Vérifier si c'est un dict valide
            if not isinstance(data["intents"][intent], dict):
                data["intents"][intent] = {"patterns": [], "responses": []}
            if "patterns" not in data["intents"][intent]:
                data["intents"][intent]["patterns"] = []

            # Vérifier si le pattern n'existe pas déjà
            if text not in data["intents"][intent]["patterns"]:
                data["intents"][intent]["patterns"].append(text)

                # Sauvegarder
                self.data_path.parent.mkdir(exist_ok=True)
                with open(self.data_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                if self.logger:
                    self.logger.info(f"➕ Exemple ajouté: '{text}' → {intent}")

                # Réentraîner le modèle
                self.train()
                return True
            else:
                if self.logger:
                    self.logger.info(f"ℹ️  Exemple déjà existant: '{text}'")
                return False

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur ajout exemple: {e}")
            return False

    def add_feedback(self, text: str, correct_intent: str):
        """Alias pour add_training_example (compatibilité)"""
        return self.add_training_example(text, correct_intent)

    def get_model_info(self) -> Dict[str, Any]:
        """Retourne les informations du modèle"""
        texts, labels = self._load_training_data()

        # Compter les exemples par intention
        intents_count = {}
        for intent in set(labels):
            intents_count[intent] = labels.count(intent)

        return {
            "is_trained": self.is_trained,
            "training_examples": len(texts),
            "intents_count": intents_count,
            "available_intents": self.intents
        }

    def _train_model(self):
        """Alias pour train (compatibilité)"""
        return self.train()