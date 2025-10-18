# nlp/intent_recognizer.py
import re
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class IntentResult:
    name: str
    confidence: float
    entities: Dict[str, Any]


class IntentRecognizer:
    """Système de reconnaissance d'intentions basé sur les règles"""

    def __init__(self, config: Dict[str, Any], logger: logging.Logger = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.patterns = self._load_patterns()
        self.threshold = config.get('confidence_threshold', 0.6)

    def _load_patterns(self) -> Dict[str, List[str]]:
        """Charge les patterns de reconnaissance d'intentions"""
        patterns = {
            "greeting": [
                r"bonjour",
                r"salut",
                r"coucou",
                r"hello",
                r"hey",
                r"bonsoir",
                r"yo"
            ],
            "calculation": [
                r"calcule (.+)",
                r"combien fait (.+)",
                r"calculer (.+)",
                r"résous (.+)",
                r"additionne (.+)",
                r"soustrais (.+)",
                r"multiplie (.+)",
                r"divise (.+)"
            ],
            "time": [
                r"quelle heure",
                r"l'heure",
                r"quelle date",
                r"on est quel jour",
                r"temps qu'il fait"
            ],
            "web_search": [
                r"cherche (.+)",
                r"recherche (.+)",
                r"trouve (.+)",
                r"c'est quoi (.+)",
                r"qui est (.+)",
                r"donne moi des infos sur (.+)",
                r"information sur (.+)"
            ],
            "task_add": [
                r"ajoute une tâche (.+)",
                r"nouvelle tâche (.+)",
                r"crée une tâche (.+)",
                r"rappelle moi de (.+)",
                r"n'oublie pas (.+)"
            ],
            "task_list": [
                r"liste des tâches",
                r"affiche les tâches",
                r"quelles sont mes tâches",
                r"tâches en cours"
            ],
            "file_operation": [
                r"liste les fichiers",
                r"crée un dossier (.+)",
                r"supprime le fichier (.+)",
                r"affiche le contenu de (.+)"
            ],
            "system_info": [
                r"info système",
                r"statut du système",
                r"état de l'agent",
                r"version d'agenttk"
            ],
            "personal": [
                r"comment tu t'appelles",
                r"quel est ton nom",
                r"qui es-tu",
                r"tu es qui"
            ],
            "thanks": [
                r"merci",
                r"merci beaucoup",
                r"thanks",
                r"je te remercie"
            ],
            "farewell": [
                r"au revoir",
                r"à bientôt",
                r"bonne journée",
                r"salut",
                r"ciao"
            ],
            "sentiment_analysis": [
                r"comment je me sens",
                r"ton de ma voix",
                r"analyse ce sentiment",
                r"comment je semble",
                r"quel est mon état d'esprit"
            ]
        }
        return patterns

    def add_pattern(self, intent_name: str, pattern: str):
        """Ajoute un pattern regex pour une intention"""
        try:
            if intent_name not in self.patterns:
                self.patterns[intent_name] = []

            # Vérifier si le pattern n'existe pas déjà
            if pattern not in self.patterns[intent_name]:
                self.patterns[intent_name].append(pattern)
                if self.logger:
                    self.logger.info(f"➕ Pattern ajouté pour {intent_name}: {pattern}")
                return True
            else:
                if self.logger:
                    self.logger.info(f"ℹ️  Pattern déjà existant pour {intent_name}")
                return False

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur ajout pattern: {e}")
            return False

    def recognize(self, text: str) -> IntentResult:
        """Reconnaît l'intention dans un texte"""
        text_lower = text.lower().strip()
        best_intent = "unknown"
        best_confidence = 0.0
        entities = {}

        if self.logger:
            self.logger.debug(f"Reconnaissance d'intention pour: '{text}'")

        for intent_name, intent_patterns in self.patterns.items():
            for pattern in intent_patterns:
                try:
                    match = re.search(pattern, text_lower)
                    if match:
                        confidence = self._calculate_confidence(text_lower, pattern, intent_name)

                        if self.logger:
                            self.logger.debug(f"Intent {intent_name}: confiance={confidence}")

                        if confidence > best_confidence:
                            best_confidence = confidence
                            best_intent = intent_name
                            entities = self._extract_entities(text_lower, intent_name)

                            # Si confiance maximale, retourner immédiatement
                            if confidence >= 0.9:
                                return IntentResult(best_intent, best_confidence, entities)
                except Exception as e:
                    if self.logger:
                        self.logger.warning(f"Erreur pattern {pattern}: {e}")
                    continue

        # Appliquer le seuil de confiance
        if best_confidence < self.threshold:
            best_intent = "unknown"
            best_confidence = 0.1

        return IntentResult(best_intent, best_confidence, entities)

    def _calculate_confidence(self, text: str, pattern: str, intent: str) -> float:
        """Calcule la confiance de la reconnaissance"""
        base_confidence = 0.7

        # Bonus pour les correspondances exactes
        if re.fullmatch(pattern, text):
            return 1.0

        # Bonus pour les intentions spécifiques
        if intent in ["greeting", "thanks", "farewell"]:
            base_confidence += 0.1

        # Bonus pour les patterns complexes
        if "(.+)" in pattern:
            base_confidence += 0.1

        # Pénalité pour les textes très courts
        if len(text) < 5:
            base_confidence -= 0.2

        return min(1.0, max(0.1, base_confidence))

    def _extract_entities(self, text: str, intent: str) -> Dict[str, Any]:
        """Extrait les entités du texte selon l'intention"""
        entities = {}

        if intent == "calculation":
            # Extraire l'expression mathématique
            math_patterns = [
                r"calcule (.+)",
                r"combien fait (.+)",
                r"calculer (.+)",
                r"résous (.+)"
            ]
            for pattern in math_patterns:
                match = re.search(pattern, text)
                if match:
                    entities["expression"] = match.group(1).strip()
                    break

        elif intent == "web_search":
            # Extraire la requête de recherche
            search_patterns = [
                r"cherche (.+)",
                r"recherche (.+)",
                r"trouve (.+)",
                r"c'est quoi (.+)",
                r"qui est (.+)",
                r"donne moi des infos sur (.+)",
                r"information sur (.+)",
                r"tu connais (.+)",  # NOUVEAU - devrait maintenant fonctionner
                r"parle moi de (.+)",  # NOUVEAU
                r"explique moi (.+)",  # NOUVEAU
                r"défini (.+)",  # NOUVEAU
                r"qu'est ce que (.+)",  # NOUVEAU
                r"résume moi (.+)",  # NOUVEAU
                r"donne moi la définition de (.+)",  # NOUVEAU
                r"je veux en savoir plus sur (.+)",  # NOUVEAU
                r"connais tu (.+)",  # NOUVEAU - variante
                r"sais tu ce qu'est (.+)",  # NOUVEAU - variante
            ]
            for pattern in search_patterns:
                match = re.search(pattern, text)
                if match:
                    entities["search_query"] = match.group(1).strip()
                    break

        elif intent == "task_add":
            # Extraire la description de la tâche
            task_patterns = [
                r"ajoute une tâche (.+)",
                r"nouvelle tâche (.+)",
                r"crée une tâche (.+)",
                r"rappelle moi de (.+)"
            ]
            for pattern in task_patterns:
                match = re.search(pattern, text)
                if match:
                    entities["task_description"] = match.group(1).strip()
                    break

        elif intent == "file_operation":
            # Extraire le nom de fichier/dossier
            file_patterns = [
                r"crée un dossier (.+)",
                r"supprime le fichier (.+)",
                r"affiche le contenu de (.+)"
            ]
            for pattern in file_patterns:
                match = re.search(pattern, text)
                if match:
                    entities["file_path"] = match.group(1).strip()
                    break

        return entities

    def get_intent_list(self) -> List[str]:
        """Retourne la liste des intentions reconnues"""
        return list(self.patterns.keys())