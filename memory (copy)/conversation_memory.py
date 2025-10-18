# memory/conversation_memory.py
"""
Mémoire conversationnelle avec contexte long terme
"""
import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging


class ConversationMemory:
    """Gestionnaire de mémoire conversationnelle"""
    
    def __init__(self, db_path: Path, logger: Optional[logging.Logger] = None):
        self.db_path = db_path
        self.logger = logger or logging.getLogger(__name__)
        self._init_database()
        
        # Cache en mémoire pour performance
        self.conversation_cache = {}
        self.cache_ttl = 300  # 5 minutes

    def _init_database(self):
        """Initialise la base de données de mémoire"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table des sessions de conversation
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversation_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    context_summary TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des messages avec contexte
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversation_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    message_type TEXT,  -- 'user' or 'agent'
                    content TEXT,
                    intent TEXT,
                    entities TEXT,  -- JSON
                    sentiment TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES conversation_sessions (session_id)
                )
            ''')
            
            # Table des faits utilisateur (mémoire long terme)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    fact_type TEXT,  -- 'preference', 'personal_info', 'habit'
                    fact_key TEXT,
                    fact_value TEXT,
                    confidence REAL DEFAULT 1.0,
                    source_message_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()

    def create_session(self, user_id: str = "default") -> str:
        """Crée une nouvelle session de conversation"""
        import uuid
        session_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO conversation_sessions (session_id, user_id, context_summary)
                VALUES (?, ?, ?)
            ''', (session_id, user_id, "Nouvelle conversation"))
            conn.commit()
            
        self.conversation_cache[session_id] = {
            "messages": [],
            "context": {},
            "last_updated": datetime.now()
        }
        
        return session_id

    def add_message(self, session_id: str, message_type: str, content: str, 
                   intent: str = "", entities: Dict = None, sentiment: str = ""):
        """Ajoute un message à la mémoire"""
        entities_json = json.dumps(entities or {})
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO conversation_messages 
                (session_id, message_type, content, intent, entities, sentiment)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (session_id, message_type, content, intent, entities_json, sentiment))
            
            # Mettre à jour le timestamp de la session
            cursor.execute('''
                UPDATE conversation_sessions 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE session_id = ?
            ''', (session_id,))
            
            conn.commit()
        
        # Mettre à jour le cache
        if session_id in self.conversation_cache:
            self.conversation_cache[session_id]["messages"].append({
                "type": message_type,
                "content": content,
                "intent": intent,
                "timestamp": datetime.now()
            })
            self.conversation_cache[session_id]["last_updated"] = datetime.now()

    def get_recent_context(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Récupère le contexte récent de la conversation"""
        # Vérifier le cache d'abord
        if (session_id in self.conversation_cache and 
            (datetime.now() - self.conversation_cache[session_id]["last_updated"]).seconds < self.cache_ttl):
            return self.conversation_cache[session_id]["messages"][-limit:]
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT message_type, content, intent, entities, timestamp
                FROM conversation_messages
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (session_id, limit))
            
            messages = [dict(row) for row in cursor.fetchall()]
            messages.reverse()  # Remettre dans l'ordre chronologique
            
            # Mettre à jour le cache
            if session_id not in self.conversation_cache:
                self.conversation_cache[session_id] = {"messages": [], "context": {}}
            self.conversation_cache[session_id]["messages"] = messages
            self.conversation_cache[session_id]["last_updated"] = datetime.now()
            
            return messages

    def extract_user_facts(self, session_id: str, message: str, intent: str, entities: Dict):
        """Extrait et stocke des faits utilisateur de la conversation"""
        facts = []
        
        # Extraire des préférences personnelles
        if intent == "personal" and "nom" in message.lower():
            facts.append({
                "type": "personal_info",
                "key": "name_mentioned",
                "value": "user_mentioned_name",
                "confidence": 0.8
            })
        
        # Extraire des intérêts des recherches web
        if intent == "web_search" and entities.get("search_query"):
            facts.append({
                "type": "interest",
                "key": "search_topic",
                "value": entities["search_query"],
                "confidence": 0.7
            })
        
        # Stocker les faits
        for fact in facts:
            self._store_user_fact(session_id, fact)

    def _store_user_fact(self, session_id: str, fact: Dict):
        """Stocke un fait utilisateur"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Récupérer user_id depuis la session
            cursor.execute('SELECT user_id FROM conversation_sessions WHERE session_id = ?', (session_id,))
            result = cursor.fetchone()
            user_id = result[0] if result else "default"
            
            # Vérifier si le fait existe déjà
            cursor.execute('''
                SELECT id FROM user_facts 
                WHERE user_id = ? AND fact_type = ? AND fact_key = ?
            ''', (user_id, fact["type"], fact["key"]))
            
            existing = cursor.fetchone()
            
            if existing:
                # Mettre à jour le fait existant
                cursor.execute('''
                    UPDATE user_facts 
                    SET fact_value = ?, confidence = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (fact["value"], fact["confidence"], existing[0]))
            else:
                # Insérer un nouveau fait
                cursor.execute('''
                    INSERT INTO user_facts (user_id, fact_type, fact_key, fact_value, confidence)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, fact["type"], fact["key"], fact["value"], fact["confidence"]))
            
            conn.commit()

    def get_conversation_summary(self, session_id: str) -> str:
        """Génère un résumé du contexte de conversation"""
        recent_messages = self.get_recent_context(session_id, 5)
        
        if not recent_messages:
            return "Aucun historique récent."
        
        summary = "**Contexte de la conversation:**\n"
        for msg in recent_messages[-3:]:  # Derniers 3 messages
            speaker = "Utilisateur" if msg["message_type"] == "user" else "Assistant"
            summary += f"- {speaker}: {msg['content'][:100]}...\n"
        
        return summary