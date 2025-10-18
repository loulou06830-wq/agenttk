# skills/web_search.py
import requests
from bs4 import BeautifulSoup
import wikipedia
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from .base_skill import BaseSkill, SkillResponse
import logging


@dataclass
class SearchResult:
    title: str
    content: str
    url: str
    summary: str = ""


class WebSearchSkill(BaseSkill):
    """Compétence de recherche web avec Wikipedia et résumés automatiques"""

    def __init__(self, logger: logging.Logger = None):
        super().__init__(logger)
        self.search_url = "https://html.duckduckgo.com/html/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Configurer Wikipedia
        wikipedia.set_lang("fr")
        wikipedia.set_rate_limiting(True)

    def can_handle(self, intent: str, entities: Dict[str, Any]) -> bool:
        return intent == "web_search"

    def execute(self, intent: str, message: str, entities: Dict[str, Any]) -> SkillResponse:
        """Exécute une recherche web avec Wikipedia et résumés"""
        search_query = entities.get("search_query", "").strip()

        if not search_query:
            return SkillResponse(False, "Je n'ai pas compris ce que vous voulez rechercher.")

        if self.logger:
            self.logger.info(f"🔍 Recherche pour: '{search_query}'")

        try:
            # Essayer d'abord Wikipedia pour du contenu structuré
            wiki_result = self._search_wikipedia(search_query)
            if wiki_result and len(wiki_result.content) > 100:
                return SkillResponse(True, self._format_wikipedia_response(wiki_result))

            # Ensuite recherche web classique avec résumés
            web_results = self._search_web_with_summaries(search_query)
            if web_results:
                return SkillResponse(True, self._format_web_response(search_query, web_results))

            # Fallback vers recherche simple
            links = self._search_links(search_query)
            return SkillResponse(True, self._format_links_response(search_query, links))

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur recherche web: {e}")
            return SkillResponse(False, "Erreur lors de la recherche web.")

    def _search_wikipedia(self, query: str) -> Optional[SearchResult]:
        """Recherche sur Wikipedia avec résumé"""
        try:
            # Nettoyer la requête pour Wikipedia
            clean_query = self._clean_wikipedia_query(query)

            # Rechercher la page
            search_results = wikipedia.search(clean_query, results=1)
            if not search_results:
                return None

            page_title = search_results[0]
            try:
                page = wikipedia.page(page_title, auto_suggest=False)
            except wikipedia.DisambiguationError as e:
                # En cas d'ambiguïté, prendre la première suggestion
                page = wikipedia.page(e.options[0], auto_suggest=False)
            except wikipedia.PageError:
                return None

            # Créer un résumé intelligent
            summary = self._generate_summary(page.content[:2000])  # Limiter pour performance

            return SearchResult(
                title=page.title,
                content=page.summary,
                url=page.url,
                summary=summary
            )

        except Exception as e:
            if self.logger:
                self.logger.warning(f"⚠️  Erreur Wikipedia pour '{query}': {e}")
            return None

    def _clean_wikipedia_query(self, query: str) -> str:
        """Nettoie la requête pour Wikipedia"""
        # Supprimer les mots de recherche
        stop_words = ['cherche', 'recherche', 'trouve', 'c est quoi', 'qui est', 'qu est ce que', 'défini', 'explique',
                      'tu connais']
        clean_query = query.lower()

        for word in stop_words:
            clean_query = clean_query.replace(word, '')

        # Supprimer la ponctuation excessive
        clean_query = re.sub(r'[^\w\s]', ' ', clean_query)

        # Supprimer les espaces multiples
        clean_query = re.sub(r'\s+', ' ', clean_query).strip()

        # Capitaliser la première lettre
        return clean_query.capitalize()

    def _search_web_with_summaries(self, query: str, max_results: int = 3) -> List[SearchResult]:
        """Recherche web avec extraction de contenu et résumés"""
        try:
            # Recherche DuckDuckGo
            response = requests.post(
                self.search_url,
                data={'q': query},
                headers=self.headers,
                timeout=10
            )

            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.content, 'html.parser')
            results = []

            # Extraire les résultats
            for result in soup.find_all('div', class_='result')[:max_results]:
                try:
                    title_elem = result.find('a', class_='result__a')
                    snippet_elem = result.find('a', class_='result__snippet')

                    if not title_elem or not snippet_elem:
                        continue

                    title = title_elem.get_text().strip()
                    snippet = snippet_elem.get_text().strip()
                    url = title_elem.get('href', '')

                    # Nettoyer l'URL DuckDuckGo
                    if 'duckduckgo.com' in url:
                        continue

                    # Générer un résumé amélioré
                    content = self._extract_page_content(url)
                    if not content:
                        content = snippet

                    summary = self._generate_summary(content)

                    results.append(SearchResult(
                        title=title,
                        content=content[:500],  # Limiter la longueur
                        url=url,
                        summary=summary
                    ))

                except Exception as e:
                    if self.logger:
                        self.logger.debug(f"Erreur traitement résultat: {e}")
                    continue

            return results

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur recherche web: {e}")
            return []

    def _extract_page_content(self, url: str, max_length: int = 2000) -> str:
        """Extrait le contenu principal d'une page web"""
        try:
            response = requests.get(url, headers=self.headers, timeout=8)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Supprimer les éléments non désirés
            for element in soup(['script', 'style', 'nav', 'header', 'footer']):
                element.decompose()

            # Essayer de trouver le contenu principal
            content_selectors = [
                'main', 'article', '.content', '.post-content',
                '.entry-content', '.article-content', '[role="main"]'
            ]

            content_elem = None
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    break

            if not content_elem:
                # Fallback: prendre tout le body
                content_elem = soup.find('body')

            if content_elem:
                text = content_elem.get_text()
                # Nettoyer le texte
                text = re.sub(r'\s+', ' ', text).strip()
                return text[:max_length]

            return ""

        except Exception as e:
            if self.logger:
                self.logger.debug(f"❌ Erreur extraction contenu {url}: {e}")
            return ""

    def _generate_summary(self, text: str, sentences_count: int = 2) -> str:
        """Génère un résumé automatique du texte"""
        try:
            if len(text) < 100:
                return text

            # Utiliser sumy pour le résumé
            parser = PlaintextParser.from_string(text, Tokenizer("french"))
            summarizer = LsaSummarizer()

            summary_sentences = summarizer(parser.document, sentences_count)
            summary = " ".join(str(sentence) for sentence in summary_sentences)

            return summary.strip()

        except Exception as e:
            if self.logger:
                self.logger.debug(f"❌ Erreur génération résumé: {e}")
            # Fallback: prendre les premières phrases
            sentences = re.split(r'[.!?]+', text)
            return " ".join(sentences[:sentences_count]).strip()

    def _search_links(self, query: str) -> List[Dict[str, str]]:
        """Recherche classique avec liens seulement (fallback)"""
        try:
            response = requests.post(
                self.search_url,
                data={'q': query},
                headers=self.headers,
                timeout=10
            )

            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.content, 'html.parser')
            links = []

            for result in soup.find_all('div', class_='result')[:5]:
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')

                if title_elem and snippet_elem:
                    title = title_elem.get_text().strip()
                    snippet = snippet_elem.get_text().strip()
                    url = title_elem.get('href', '')

                    # Nettoyer l'URL DuckDuckGo
                    if 'duckduckgo.com' in url:
                        url_match = re.search(r'uddg=([^&]+)', url)
                        if url_match:
                            import urllib.parse
                            url = urllib.parse.unquote(url_match.group(1))

                    links.append({
                        'title': title,
                        'snippet': snippet,
                        'url': url
                    })

            return links

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Erreur recherche liens: {e}")
            return []

    def _format_wikipedia_response(self, result: SearchResult) -> str:
        """Formate la réponse Wikipedia"""
        response = f"📚 **Wikipedia: {result.title}**\n\n"

        if result.summary:
            response += f"**📖 Résumé :** {result.summary}\n\n"

        # Prendre les premiers paragraphes du contenu
        content_paragraphs = result.content.split('\n')
        main_content = ""
        for paragraph in content_paragraphs[:3]:  # Prendre les 3 premiers paragraphes
            if paragraph.strip() and len(paragraph) > 50:
                main_content += paragraph.strip() + "\n\n"

        if main_content:
            response += f"**📝 Contenu :**\n{main_content}"

        response += f"🌐 **Source :** {result.url}"

        return response

    def _format_web_response(self, query: str, results: List[SearchResult]) -> str:
        """Formate la réponse web avec résumés"""
        response = f"🔍 **Recherche web pour '{query}':**\n\n"

        for i, result in enumerate(results, 1):
            response += f"**{i}. {result.title}**\n"

            if result.summary:
                response += f"   📖 {result.summary}\n"
            elif result.content:
                # Utiliser le contenu si pas de résumé
                preview = result.content[:150] + "..." if len(result.content) > 150 else result.content
                response += f"   📝 {preview}\n"

            response += f"   🌐 {result.url}\n\n"

        return response

    def _format_links_response(self, query: str, links: List[Dict[str, str]]) -> str:
        """Formate la réponse avec liens seulement (fallback)"""
        response = f"🔍 **Recherche web pour '{query}':**\n\n"

        for i, link in enumerate(links, 1):
            response += f"**{i}. {link['title']}**\n"
            response += f"   📝 {link['snippet']}\n"
            response += f"   🌐 {link['url']}\n\n"

        response += "💡 *Pour des résultats plus détaillés, vérifiez votre connexion internet.*"
        return response