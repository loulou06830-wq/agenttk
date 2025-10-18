# memory/database.py
"""
Gestionnaire de base de données
"""
import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import contextlib


class DatabaseManager:
    """Gestionnaire de base de données SQLite"""

    def __init__(self, db_path: Path, logger: Optional[logging.Logger] = None):
        self.db_path = db_path
        self.logger = logger or logging.getLogger(__name__)
        self._init_database()

    def _init_database(self):
        """Initialise la base de données"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Table des conversations
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations
                (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_message TEXT NOT NULL,
                    agent_response TEXT NOT NULL,
                    intent TEXT,
                    confidence REAL,
                    ml_used BOOLEAN DEFAULT FALSE  -- AJOUT de cette colonne
                )
            ''')

            # Table des tâches
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks
                (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()

        self.logger.info(f"Base de données initialisée: {self.db_path}")

    @contextlib.contextmanager
    def _get_connection(self):
        """Context manager pour connexions DB"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def save_interaction(self, user_message: str, agent_response: str,
                         intent: str = "", confidence: float = 0.0,
                         ml_used: bool = False):  # AJOUT du paramètre ml_used
        """Sauvegarde une interaction"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO conversations (user_message, agent_response, intent, confidence, ml_used)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_message, agent_response, intent, confidence, ml_used))
            conn.commit()

    def add_task(self, title: str, description: str = "") -> int:
        """Ajoute une tâche"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tasks (title, description)
                VALUES (?, ?)
            ''', (title, description))
            conn.commit()
            return cursor.lastrowid

    def get_pending_tasks(self) -> List[Dict]:
        """Récupère les tâches en attente"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, title, description
                FROM tasks
                WHERE status = 'pending'
                ORDER BY created_at
            ''')
            return [dict(row) for row in cursor.fetchall()]

    def complete_task(self, task_id: int) -> bool:
        """Termine une tâche"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE tasks
                SET status = 'completed'
                WHERE id = ?
            ''', (task_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_conversation_history(self, limit: int = 10) -> List[Dict]:
        """Récupère l'historique"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_message, agent_response, timestamp, intent, confidence, ml_used
                FROM conversations
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
