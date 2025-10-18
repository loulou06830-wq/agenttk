# skills/knowledge_skill.py - VERSION CORRIGÉE
"""
Compétence de connaissances générales avec fallback web
"""
import logging
from typing import Dict, Any, Optional
from .base_skill import BaseSkill, SkillResponse


class KnowledgeSkill(BaseSkill):
    """Répond aux questions de connaissances générales avec fallback web"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        super().__init__("knowledge", "Connaissances générales")
        self.logger = logger or logging.getLogger(__name__)
        self.web_search_skill = None  # Référence à la compétence web_search
        
        # Base de connaissances améliorée
        self.knowledge_base = {
            # Géographie - CAPITALES
            "capitale de la france": "🇫🇷 La capitale de la France est **Paris**.",
            "capitale france": "🇫🇷 La capitale de la France est **Paris**.",
            "capitale de france": "🇫🇷 La capitale de la France est **Paris**.",
            "paris capitale": "🇫🇷 Oui, **Paris** est la capitale de la France.",
            
            "capitale de l'allemagne": "🇩🇪 La capitale de l'Allemagne est **Berlin**.",
            "capitale allemagne": "🇩🇪 La capitale de l'Allemagne est **Berlin**.", 
            "capitale de l'italie": "🇮🇹 La capitale de l'Italie est **Rome**.",
            "capitale italie": "🇮🇹 La capitale de l'Italie est **Rome**.",
            "capitale de l'espagne": "🇪🇸 La capitale de l'Espagne est **Madrid**.",
            "capitale espagne": "🇪🇸 La capitale de l'Espagne est **Madrid**.",
            "capitale du royaume uni": "🇬🇧 La capitale du Royaume-Uni est **Londres**.",
            "capitale angleterre": "🇬🇧 La capitale de l'Angleterre est **Londres**.",
            "capitale des états unis": "🇺🇸 La capitale des États-Unis est **Washington D.C.**.",
            "capitale états unis": "🇺🇸 La capitale des États-Unis est **Washington D.C.**.",
            "capitale usa": "🇺🇸 La capitale des États-Unis est **Washington D.C.**.",
            
            # Programmation
            "python": "🐍 **Python** est un langage de programmation interprété, de haut niveau et généraliste. Il est connu pour sa syntaxe claire et sa grande communauté.",
            "qu'est ce que python": "🐍 **Python** est un langage de programmation interprété, de haut niveau et généraliste. Il est connu pour sa syntaxe claire et sa grande communauté.",
            "langage python": "🐍 **Python** est un langage de programmation interprété, de haut niveau et généraliste.",
            
            "javascript": "📜 **JavaScript** est un langage de programmation principalement utilisé pour le développement web côté client.",
            "java": "☕ **Java** est un langage de programmation orienté objet multiplateforme.",
            
            # Sciences
            "planète la plus proche du soleil": "☀️ La planète la plus proche du Soleil est **Mercure**.",
            "plus grande planète du système solaire": "🪐 La plus grande planète du système solaire est **Jupiter**.",
            "planète rouge": "🔴 La planète rouge est **Mars**.",
            "satellite naturel de la terre": "🌙 Le satellite naturel de la Terre est **la Lune**.",
            
            # Histoire
            "premier président de la france": "👑 Le premier président de la France fut **Louis-Napoléon Bonaparte**.",
            "qui a découvert l'amérique": "⛵ **Christophe Colomb** a découvert l'Amérique en 1492.",
            "qui a peint la joconde": "🎨 **Léonard de Vinci** a peint la Joconde.",
            
            # Culture générale
            "créateur de microsoft": "💻 Le créateur de Microsoft est **Bill Gates**.",
            "créateur d'apple": "🍎 Le créateur d'Apple est **Steve Jobs**.",
            "créateur de facebook": "👤 Le créateur de Facebook est **Mark Zuckerberg**.",
            "langue la plus parlée au monde": "🗣️ La langue la plus parlée au monde est le **mandarin**.",
            
            # Définitions courantes
            "intelligence artificielle": "🧠 L'**intelligence artificielle** (IA) est la simulation de processus d'intelligence humaine par des machines.",
            "machine learning": "🤖 Le **machine learning** est un sous-domaine de l'IA qui permet aux machines d'apprendre à partir de données.",
            "ia": "🧠 L'**intelligence artificielle** (IA) est la simulation de processus d'intelligence humaine par des machines.",
            
            # Jeux vidéo
            "minecraft": "🎮 **Minecraft** est un jeu vidéo de type 'sandbox' développé par Mojang Studios, permettant aux joueurs de construire et d'explorer des mondes en 3D.",
            "qu'est ce que minecraft": "🎮 **Minecraft** est un jeu vidéo de type 'sandbox' développé par Mojang Studios.",
            "fortnite": "🎯 **Fortnite** est un jeu vidéo de battle royale développé par Epic Games.",
            "roblox": "🧩 **Roblox** est une plateforme de jeux en ligne qui permet aux utilisateurs de créer et jouer à des jeux créés par d'autres utilisateurs.",
            
            # Technologie
            "windows": "🪟 **Windows** est un système d'exploitation développé par Microsoft.",
            "linux": "🐧 **Linux** est un système d'exploitation open-source de type Unix.",
            "macos": "🍎 **macOS** est le système d'exploitation d'Apple pour les ordinateurs Mac.",
            
            # Vidéos et médias - AJOUT IMPORTANT
            "vidéo la plus vue": "🎬 La **vidéo la plus vue sur YouTube** est 'Baby Shark Dance' avec plus de 14 milliards de vues.",
            "vidéo la plus vue sur youtube": "🎬 La **vidéo la plus vue sur YouTube** est 'Baby Shark Dance' avec plus de 14 milliards de vues.",
            "video la plus vue": "🎬 La **vidéo la plus vue sur YouTube** est 'Baby Shark Dance' avec plus de 14 milliards de vues.",
            "chanson la plus écoutée": "🎵 La **chanson la plus écoutée** est 'Blinding Lights' de The Weeknd.",
            "film le plus vu": "🎞️ Le **film le plus vu** au monde est 'Avatar' de James Cameron.",
            
            # Présidents et politique
            "président de la france": "🇫🇷 Le président de la France est **Emmanuel Macron** (élu en 2017 et réélu en 2022).",
            "président france": "🇫🇷 Le président de la France est **Emmanuel Macron**.",
            "emmanuel macron": "🇫🇷 **Emmanuel Macron** est le président de la France depuis 2017.",
            "qui est le président de la france": "🇫🇷 Le président de la France est **Emmanuel Macron**.",
            "qui est président en france": "🇫🇷 Le président de la France est **Emmanuel Macron**.",
        }
    
    def set_web_search_skill(self, web_search_skill):
        """Définit la référence à la compétence web_search"""
        self.web_search_skill = web_search_skill
        self.logger.info("Compétence WebSearch liée à Knowledge")
    
    def execute(self, **kwargs) -> SkillResponse:
        """Répond aux questions de connaissances avec fallback web"""
        intent = kwargs.get('intent', '')
        message = kwargs.get('message', '')
        entities = kwargs.get('entities', {})
        
        query = entities.get("search_query", "").lower().strip()
        if not query:
            query = self._extract_question(message)
        
        self.logger.info(f"Recherche connaissance pour: '{query}'")
        
        # Chercher dans la base de connaissances
        answer = self._find_answer(query)
        
        if answer:
            return SkillResponse(
                success=True,
                message=answer,
                data={"query": query, "answer": answer, "source": "knowledge_base"}
            )
        else:
            # Si pas de réponse locale, utiliser web_search
            self.logger.info(f"Aucune réponse locale pour '{query}', recherche web...")
            return self._fallback_to_web_search(query, intent, entities)
    
    def _find_answer(self, query: str) -> str:
        """Trouve une réponse dans la base de connaissances"""
        # Nettoyer la requête
        clean_query = query.rstrip('?').strip()
        
        # Chercher une correspondance exacte
        if clean_query in self.knowledge_base:
            return self.knowledge_base[clean_query]
        
        # Chercher des correspondances partielles avec score
        best_match = None
        best_score = 0
        
        for knowledge_query, answer in self.knowledge_base.items():
            score = self._calculate_similarity(clean_query, knowledge_query)
            if score > best_score and score > 0.6:  # Seuil de similarité
                best_score = score
                best_match = answer
        
        if best_match:
            return best_match
        
        # Questions spécifiques avec logique
        if any(word in clean_query for word in ["capitale", "capital"]) and any(word in clean_query for word in ["france", "français"]):
            return "🇫🇷 La capitale de la France est **Paris**."
        
        if any(word in clean_query for word in ["capitale", "capital"]) and any(word in clean_query for word in ["italie", "italien"]):
            return "🇮🇹 La capitale de l'Italie est **Rome**."
        
        if any(word in clean_query for word in ["président", "president"]) and any(word in clean_query for word in ["france", "français"]):
            return "🇫🇷 Le président de la France est **Emmanuel Macron**."
        
        if any(word in clean_query for word in ["vidéo", "video"]) and "plus vue" in clean_query:
            return "🎬 La **vidéo la plus vue sur YouTube** est 'Baby Shark Dance' avec plus de 14 milliards de vues."
        
        if "python" in clean_query and any(word in clean_query for word in ["c'est", "est", "qu'est", "quel"]):
            return "🐍 **Python** est un langage de programmation interprété, de haut niveau et généraliste."
        
        return ""
    
    def _calculate_similarity(self, query: str, knowledge_query: str) -> float:
        """Calcule un score de similarité entre deux requêtes"""
        query_words = set(query.lower().split())
        knowledge_words = set(knowledge_query.lower().split())
        
        # Mots communs
        common_words = query_words.intersection(knowledge_words)
        
        # Score basé sur le pourcentage de mots en commun
        if not query_words or not knowledge_words:
            return 0.0
        
        score = len(common_words) / max(len(query_words), len(knowledge_words))
        
        # Bonus si l'ordre des mots est similaire
        query_list = query.lower().split()
        knowledge_list = knowledge_query.lower().split()
        
        # Vérifier si les premiers mots correspondent
        if query_list and knowledge_list and query_list[0] == knowledge_list[0]:
            score += 0.2
        
        return min(score, 1.0)
    
    def _fallback_to_web_search(self, query: str, intent: str, entities: Dict[str, Any]) -> SkillResponse:
        """Utilise web_search quand aucune réponse locale n'est trouvée"""
        if self.web_search_skill:
            self.logger.info(f"Recherche web automatique pour: '{query}'")
            web_result = self.web_search_skill.execute(
                intent=intent,
                message=query,
                entities={"search_query": query}
            )
            
            if web_result.success:
                # Ajouter un préfixe pour indiquer que c'est une recherche web
                web_message = f"🔍 **Recherche web pour '{query}':**\n\n{web_result.message}"
                return SkillResponse(
                    success=True,
                    message=web_message,
                    data={"query": query, "source": "web_search", "web_data": web_result.data}
                )
        
        # Si web_search n'est pas disponible ou échoue
        return SkillResponse(
            success=False,
            message="",  # Laisse les autres compétences essayer
            data={"query": query, "found": False}
        )
    
    def _extract_question(self, message: str) -> str:
        """Extrait la question du message"""
        question_words = [
            'quelle est', 'qu\'elle est', 'qu\'est ce que', 'qu est ce que', 
            'c\'est quoi', 'quel est', 'que est', 'qui est', 'qui a'
        ]
        
        for word in question_words:
            if word in message.lower():
                return message.lower().split(word, 1)[1].strip().rstrip('?')
        
        return message.strip()
    
    def can_handle(self, intent: str, entities: Dict[str, Any]) -> bool:
        """Gère les questions de connaissances"""
        return intent == "web_search" and entities.get("search_query")
