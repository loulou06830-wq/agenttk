# skills/self_improvement.py
import re
import requests
from bs4 import BeautifulSoup
import time
from dataclasses import dataclass
from typing import List, Dict, Any
import json
import logging
from .base_skill import BaseSkill, SkillResponse


@dataclass
class ImprovementResult:
    success: bool
    patterns_added: List[str]
    examples_added: List[Dict[str, Any]]
    message: str


class SelfImprovementSkill(BaseSkill):
    """Compétence d'auto-amélioration par recherche web"""

    def __init__(self, name: str = "self_improvement", agent=None, logger: logging.Logger = None):
        super().__init__(name, agent, logger)
        self.search_url = "https://www.google.com/search"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.cache = {}
        self.request_delay = 2  # seconds between requests

    def can_handle(self, intent: str, entities: Dict[str, Any]) -> bool:
        """Détermine si la compétence peut gérer l'intention"""
        return intent == "self_improvement" or intent == "improve"

    def execute(self, intent: str, message: str, entities: Dict[str, Any]) -> SkillResponse:
        """Exécute la compétence d'auto-amélioration"""
        try:
            # Extraire l'intention cible du message
            target_intent = self._extract_target_intent(message)
            if not target_intent:
                return SkillResponse(
                    success=False,
                    message="Veuillez spécifier quelle intention améliorer (ex: 'améliore greeting')"
                )

            # Lancer l'auto-amélioration
            result = self.improve_intent_recognition(target_intent)

            if result.success:
                return SkillResponse(
                    success=True,
                    message=result.message,
                    data={
                        "patterns_added": result.patterns_added,
                        "examples_added": result.examples_added
                    }
                )
            else:
                return SkillResponse(
                    success=False,
                    message=result.message
                )

        except Exception as e:
            return SkillResponse(
                success=False,
                message=f"Erreur lors de l'auto-amélioration: {str(e)}"
            )

    def _extract_target_intent(self, message: str) -> str:
        """Extrait l'intention cible du message"""
        intent_keywords = {
            "greeting": ["salut", "bonjour", "coucou", "hello"],
            "web_search": ["recherche", "cherche", "trouve", "information"],
            "calculation": ["calcul", "calcule", "math", "combien"],
            "time": ["heure", "date", "temps"],
            "task_add": ["tâche", "todo", "ajoute", "liste"],
            "thanks": ["merci", "remercie"]
        }

        message_lower = message.lower()
        for intent, keywords in intent_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent

        # Essayer d'extraire directement
        words = message_lower.split()
        for word in words:
            if word in intent_keywords:
                return word

        return ""

    def search_common_phrases(self, intent: str, language: str = "fr") -> List[str]:
        """Recherche les phrases courantes pour une intention"""
        cache_key = f"{intent}_{language}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        queries = self._get_search_queries(intent)
        if not queries:
            return []

        phrases = []
        for query in queries:
            try:
                self._log('info', f"🔍 Recherche Google: {query}")
                response = requests.get(
                    f"{self.search_url}?q={query}&hl={language}",
                    headers=self.headers,
                    timeout=15
                )

                if response.status_code != 200:
                    self._log('warning', f"❌ Erreur HTTP {response.status_code} pour: {query}")
                    continue

                snippets = self._extract_snippets(response.content, intent)
                phrases.extend(snippets)

                time.sleep(self.request_delay)  # Respect rate limiting

            except requests.exceptions.Timeout:
                self._log('warning', f"⏰ Timeout pour: {query}")
                continue
            except Exception as e:
                self._log('error', f"❌ Erreur recherche pour '{query}': {e}")
                continue

        # Nettoyer et filtrer les phrases
        clean_phrases = self._clean_phrases(phrases)
        unique_phrases = list(set(clean_phrases))[:8]
        self.cache[cache_key] = unique_phrases

        self._log('info', f"✅ {len(unique_phrases)} phrases trouvées pour {intent}")
        return unique_phrases

    def _get_search_queries(self, intent: str) -> List[str]:
        """Retourne les requêtes de recherche pour une intention"""
        queries_map = {
            "greeting": [
                "façons de dire bonjour en français",
                "salutations courantes français",
                "comment dire bonjour différentes manières",
                "manières de saluer en français",
                "expressions pour dire bonjour"
            ],
            "web_search": [
                "comment demander une recherche internet",
                "façons de demander des informations web",
                "phrases pour chercher sur internet",
                "comment poser une question recherche web",
                "demander information internet phrases",
                "comment chercher information en ligne"
            ],
            "calculation": [
                "comment demander un calcul mathématique",
                "façons de demander un calcul",
                "phrases pour calculer quelque chose",
                "comment demander un calcul en français",
                "expressions pour demander un calcul"
            ],
            "time": [
                "comment demander l'heure en français",
                "façons de demander la date",
                "phrases pour connaître l'heure",
                "demander l'heure date français",
                "comment savoir l'heure maintenant"
            ],
            "task_add": [
                "comment ajouter une tâche liste",
                "phrases pour créer une tâche",
                "demander d'ajouter une tâche",
                "comment créer nouvelle tâche",
                "ajouter item liste tâches"
            ],
            "thanks": [
                "façons de remercier en français",
                "comment dire merci différentes manières",
                "expressions de gratitude français",
                "manières de remercier quelqu'un"
            ]
        }
        return queries_map.get(intent, [])

    def _extract_snippets(self, html_content: str, intent: str) -> List[str]:
        """Extrait les snippets des résultats Google"""
        soup = BeautifulSoup(html_content, 'html.parser')
        snippets = []

        # Sélecteurs pour les snippets Google
        selectors = [
            'div.VwiC3b', 'div.yDYNvb', 'div.lyLwlc',
            'span.hgKElc', 'div.BNeawe', 'span.ILfuVd',
            'div.s3v9rd', 'div.qtR3Y'
        ]

        for selector in selectors:
            for element in soup.select(selector):
                text = element.get_text().strip()
                if text and 10 < len(text) < 200 and self._is_relevant_phrase(text, intent):
                    snippets.append(text)

        # Phrases génériques de fallback
        if len(snippets) < 3:
            generic_phrases = self._get_generic_phrases(intent)
            snippets.extend(generic_phrases)

        return snippets

    def _clean_phrases(self, phrases: List[str]) -> List[str]:
        """Nettoie et filtre les phrases"""
        clean_phrases = []
        irrelevant_words = ['cookie', 'connexion', 'erreur', '404', 'javascript', 'cliquez']

        for phrase in phrases:
            clean_phrase = re.sub(r'\s+', ' ', phrase).strip()
            if (len(clean_phrase) > 10 and
                    len(clean_phrase) < 150 and
                    not any(word in clean_phrase.lower() for word in irrelevant_words)):
                clean_phrases.append(clean_phrase)

        return clean_phrases

    def _is_relevant_phrase(self, phrase: str, intent: str) -> bool:
        """Vérifie si une phrase est pertinente pour l'intention"""
        phrase_lower = phrase.lower()

        intent_keywords = {
            "greeting": ['bonjour', 'salut', 'coucou', 'hello', 'salutations', 'ça va', 'comment vas'],
            "web_search": ['cherche', 'recherche', 'trouve', 'information', 'quoi', 'qui', 'comment', 'pourquoi'],
            "calculation": ['calcule', 'calcul', 'combien', 'addition', 'soustraction', 'fois', 'divisé', 'math'],
            "time": ['heure', 'date', 'temps', 'jour', 'maintenant', 'aujourdhui'],
            "task_add": ['tâche', 'todo', 'ajoute', 'liste', 'faire', 'rappelle'],
            "thanks": ['merci', 'remercie', 'gratitude', ' reconnaiss', 'thanks']
        }

        keywords = intent_keywords.get(intent, [])
        return any(keyword in phrase_lower for keyword in keywords)

    def _get_generic_phrases(self, intent: str) -> List[str]:
        """Retourne des phrases génériques si la recherche échoue"""
        generic_phrases = {
            "greeting": [
                "Bonjour comment allez-vous aujourd'hui",
                "Salut ça va bien",
                "Hello bonjour à vous",
                "Coucou comment ça va",
                "Bonsoir comment allez-vous",
                "Hey comment tu vas",
                "Bonjour mon ami"
            ],
            "web_search": [
                "Je cherche des informations sur ce sujet",
                "Peux-tu me trouver des infos sur ce thème",
                "Donne-moi des informations concernant cela",
                "Je voudrais savoir à propos de ce topic",
                "Recherche des infos sur le sujet suivant",
                "Trouve moi des informations sur cette chose",
                "Cherche des détails sur ce concept"
            ],
            "calculation": [
                "Calcule cette expression mathématique pour moi",
                "Combien font ces nombres ensemble",
                "Peux-tu calculer ce calcul s'il te plaît",
                "Donne-moi le résultat de cette opération",
                "Effectue ce calcul mathématique maintenant",
                "Résous cette équation mathématique",
                "Calcule le total de ces chiffres"
            ],
            "time": [
                "Quelle heure est-il en ce moment",
                "Peux-tu me dire la date d'aujourd'hui",
                "Donne-moi l'heure actuelle s'il te plaît",
                "Quel jour sommes-nous aujourd'hui",
                "Quelle est la date du jour",
                "Peux-tu me dire l'heure qu'il est",
                "Quel est le jour de la semaine"
            ],
            "task_add": [
                "Ajoute une tâche à ma liste",
                "Nouvelle tâche à faire",
                "Rappelle-moi de faire cela",
                "Ajoute ceci à mes tâches",
                "Crée une nouvelle tâche pour moi"
            ],
            "thanks": [
                "Merci beaucoup pour ton aide",
                "Je te remercie pour cela",
                "Un grand merci à toi",
                "Merci infiniment pour ton assistance",
                "Je suis reconnaissant pour ton aide",
                "Merci bien pour ton soutien",
                "Thanks pour ton assistance"
            ]
        }
        return generic_phrases.get(intent, [])

    def extract_patterns_from_phrases(self, phrases: List[str], intent: str) -> List[str]:
        """Extrait des patterns regex à partir des phrases"""
        patterns = set()  # Utiliser un set pour éviter les doublons

        for phrase in phrases:
            clean_phrase = re.sub(r'[^\w\s]', '', phrase.lower()).strip()
            words = clean_phrase.split()

            if intent == "web_search":
                patterns.update(self._extract_web_search_patterns(clean_phrase, words))
            elif intent == "greeting":
                patterns.update(self._extract_greeting_patterns(clean_phrase, words))
            elif intent == "calculation":
                patterns.update(self._extract_calculation_patterns(clean_phrase, words))
            elif intent == "thanks":
                patterns.update(self._extract_thanks_patterns(clean_phrase, words))
            elif intent == "time":
                patterns.update(self._extract_time_patterns(clean_phrase, words))
            elif intent == "task_add":
                patterns.update(self._extract_task_patterns(clean_phrase, words))

        # Nettoyer et limiter les patterns
        clean_patterns = []
        for pattern in patterns:
            if len(pattern) > 8 and len(pattern) < 100:
                clean_patterns.append(pattern)

        return clean_patterns[:6]

    def _extract_web_search_patterns(self, clean_phrase: str, words: List[str]) -> List[str]:
        """Extrait les patterns pour la recherche web"""
        patterns = []
        search_keywords = ['cherche', 'recherche', 'trouve', 'information', 'quoi', 'qui', 'comment',
                           'connais', 'sais', 'explique', 'défini']

        if any(word in clean_phrase for word in search_keywords):
            if len(words) >= 2:
                key_words = [w for w in words if w in search_keywords]
                if key_words:
                    pattern = r"(?:" + "|".join(key_words) + r")\s+(.+)"
                    patterns.append(pattern)

        # Patterns pour questions
        question_patterns = [
            r"tu connais (.+)",
            r"connais tu (.+)",
            r"sais tu (.+)",
            r"qu'est ce que (.+)",
            r"c'est quoi (.+)",
            r"qui est (.+)"
        ]

        for q_pattern in question_patterns:
            if re.search(q_pattern.replace(r"(.+)", ""), clean_phrase):
                patterns.append(q_pattern)

        return patterns

    def _extract_greeting_patterns(self, clean_phrase: str, words: List[str]) -> List[str]:
        """Extrait les patterns pour les salutations"""
        patterns = []
        greeting_words = [w for w in words if w in ['bonjour', 'salut', 'coucou', 'hello', 'salutations', 'hey']]
        if greeting_words:
            pattern = r"(?:" + "|".join(greeting_words) + r")(?:\s+.+)?"
            patterns.append(pattern)
        return patterns

    def _extract_calculation_patterns(self, clean_phrase: str, words: List[str]) -> List[str]:
        """Extrait les patterns pour les calculs"""
        patterns = []
        if any(word in clean_phrase for word in ['calcule', 'calcul', 'combien', 'addition', 'soustraction', 'fois']):
            calc_words = [w for w in words if w in ['calcule', 'calculer', 'combien', 'fait', 'résous']]
            if calc_words:
                pattern = r"(?:" + "|".join(calc_words) + r")\s+(.+)"
                patterns.append(pattern)
        return patterns

    def _extract_thanks_patterns(self, clean_phrase: str, words: List[str]) -> List[str]:
        """Extrait les patterns pour les remerciements"""
        patterns = []
        thanks_words = [w for w in words if w in ['merci', 'remercie', 'thanks']]
        if thanks_words:
            pattern = r"(?:" + "|".join(thanks_words) + r")(?:\s+.+)?"
            patterns.append(pattern)
        return patterns

    def _extract_time_patterns(self, clean_phrase: str, words: List[str]) -> List[str]:
        """Extrait les patterns pour le temps"""
        patterns = []
        time_words = [w for w in words if w in ['heure', 'date', 'temps', 'jour', 'maintenant']]
        if time_words:
            pattern = r"(?:(?:quelle|donne).*)?(?:" + "|".join(time_words) + r").*"
            patterns.append(pattern)
        return patterns

    def _extract_task_patterns(self, clean_phrase: str, words: List[str]) -> List[str]:
        """Extrait les patterns pour les tâches"""
        patterns = []
        task_words = [w for w in words if w in ['tâche', 'ajoute', 'liste', 'rappelle', 'todo']]
        if task_words:
            pattern = r"(?:" + "|".join(task_words) + r")\s+(.+)"
            patterns.append(pattern)
        return patterns

    def improve_intent_recognition(self, intent: str) -> ImprovementResult:
        """Améliore la reconnaissance pour une intention spécifique"""
        try:
            self._log('info', f"🚀 Début auto-amélioration pour: {intent}")

            # Rechercher des phrases courantes
            phrases = self.search_common_phrases(intent)

            if not phrases:
                return ImprovementResult(
                    False, [], [],
                    f"❌ Aucune phrase trouvée pour '{intent}'"
                )

            self._log('info', f"📝 Phrases trouvées: {len(phrases)}")

            # Extraire des patterns UNIQUES
            new_patterns = self.extract_patterns_from_phrases(phrases, intent)

            # Générer des exemples d'entraînement UNIQUES
            training_examples = []
            seen_examples = set()

            for phrase in phrases[:6]:
                if phrase not in seen_examples:
                    training_examples.append({
                        "text": str(phrase),
                        "intent": str(intent),
                        "entities": []
                    })
                    seen_examples.add(phrase)

            message = (f"✅ Auto-amélioration réussie!\n"
                       f"• {len(new_patterns)} nouveaux patterns\n"
                       f"• {len(training_examples)} exemples d'entraînement\n"
                       f"• Intentions: {intent}")

            return ImprovementResult(
                success=True,
                patterns_added=new_patterns,
                examples_added=training_examples,
                message=message
            )

        except Exception as e:
            error_msg = f"❌ Erreur lors de l'auto-amélioration: {str(e)}"
            self._log('error', error_msg)
            return ImprovementResult(False, [], [], error_msg)