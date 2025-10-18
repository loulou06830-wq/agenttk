# ui/tkinter_ui.py
"""
Interface utilisateur Tkinter avec Avatar Animé et Auto-Amélioration
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from pathlib import Path
import sys
from datetime import datetime
import json

# Ajouter le chemin parent
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_core.agent import Agent
from ui.avatar_2d_widget import Avatar2DWidget, AvatarCustomizationPanel


class AgentTKUI:
    """Interface graphique pour AgentTK avec Avatar Animé"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AgentTK v1.2.0 - Avatar Animé")
        self.root.geometry("900x700")  # Augmenté pour l'avatar
        self.root.configure(bg='#2b2b2b')

        # Variables
        self.agent = None
        self.is_running = False
        self.typing_var = tk.StringVar(value="")
        self.chat_log = []
        self.improvement_in_progress = False
        self.avatar = None  # Widget avatar

        self.setup_ui()
        self.setup_agent()

    def setup_ui(self):
        """Configure l'interface avec avatar"""
        # Style
        style = ttk.Style()
        style.theme_use('clam')

        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header avec avatar
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        # AVATAR À GAUCHE
        avatar_container = ttk.Frame(header_frame)
        avatar_container.pack(side=tk.LEFT, padx=(0, 15))
        
        self.avatar = Avatar2DWidget(avatar_container, size=200)
        self.avatar.pack()
        custom_panel = AvatarCustomizationPanel(main_frame, self.avatar)
        custom_panel.pack(fill=tk.X, pady=10)

        # Titre et infos
        info_frame = ttk.Frame(header_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(
            info_frame,
            text="🤖 AgentTK v1.2.0",
            font=('Arial', 16, 'bold'),
            foreground='#4CAF50'
        ).pack(anchor=tk.W)

        # Status
        self.status_var = tk.StringVar(value="🟡 Initialisation...")
        ttk.Label(
            info_frame,
            textvariable=self.status_var,
            font=('Arial', 10),
            foreground='#FF9800'
        ).pack(anchor=tk.W, pady=(5, 0))

        # Indicateur de frappe
        typing_label = ttk.Label(
            info_frame,
            textvariable=self.typing_var,
            font=('Arial', 9, 'italic'),
            foreground='#888'
        )
        typing_label.pack(anchor=tk.W)

        # Zone de conversation
        conv_frame = ttk.LabelFrame(main_frame, text="Conversation", padding=10)
        conv_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Historique des messages
        self.chat_history = scrolledtext.ScrolledText(
            conv_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            bg='#1e1e1e',
            fg='white',
            insertbackground='white',
            font=('Arial', 10)
        )
        self.chat_history.pack(fill=tk.BOTH, expand=True)
        self.chat_history.config(state=tk.DISABLED)

        # Configuration des tags
        self.chat_history.tag_config("user", foreground='#4CAF50', font=('Arial', 10, 'bold'))
        self.chat_history.tag_config("agent", foreground='#2196F3', font=('Arial', 10, 'bold'))
        self.chat_history.tag_config("system", foreground='#FF9800', font=('Arial', 10, 'bold'))
        self.chat_history.tag_config("improvement", foreground='#FF5722', font=('Arial', 10, 'bold'))
        self.chat_history.tag_config("bold", font=('Arial', 10, 'bold'))
        self.chat_history.tag_config("italic", font=('Arial', 10, 'italic'))

        # Zone de saisie
        input_frame = ttk.Frame(conv_frame)
        input_frame.pack(fill=tk.X, pady=(10, 0))

        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(
            input_frame,
            textvariable=self.input_var,
            font=('Arial', 11)
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.input_entry.bind('<Return>', self.send_message)

        ttk.Button(
            input_frame,
            text="Envoyer",
            command=self.send_message
        ).pack(side=tk.RIGHT)

        # Panel d'actions
        actions_frame = ttk.Frame(main_frame)
        actions_frame.pack(fill=tk.X)

        # Boutons d'actions
        ttk.Button(
            actions_frame,
            text="🔧 Auto-Améliore",
            command=self.show_auto_improvement_dialog
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            actions_frame,
            text="💡 Feedback",
            command=self.show_feedback_dialog
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            actions_frame,
            text="📊 Stats ML",
            command=self.show_ml_stats
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            actions_frame,
            text="🌐 Recherche",
            command=self.show_web_search
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            actions_frame,
            text="📋 Tâches",
            command=self.show_tasks
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            actions_frame,
            text="🧮 Calculatrice",
            command=self.show_calculator
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            actions_frame,
            text="🕐 Heure",
            command=self.show_time
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            actions_frame,
            text="📁 Fichiers",
            command=self.show_files
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            actions_frame,
            text="🗑️ Effacer",
            command=self.clear_chat
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            actions_frame,
            text="💡 Aide",
            command=self.show_help
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            actions_frame,
            text="❌ Quitter",
            command=self.quit_app
        ).pack(side=tk.RIGHT, padx=2)

    def setup_agent(self):
        """Initialise l'agent avec animation avatar"""
        def init_agent():
            try:
                self.status_var.set("🟡 Démarrage de l'agent...")
                self.avatar.start_thinking()
                
                self.agent = Agent("AgentTK", "config.yaml")
                self.is_running = True
                
                self.avatar.stop_thinking()
                self.avatar.show_emotion("happy", 2000)
                self.status_var.set("🟢 Agent prêt")
                
                self.add_message("🤖 AgentTK",
                                 "Bonjour ! Je suis votre assistant IA avec avatar animé. Tapez 'aide' pour voir mes capacités.")
            except Exception as e:
                self.avatar.stop_thinking()
                self.avatar.show_emotion("error", 3000)
                self.status_var.set("🔴 Erreur de démarrage")
                messagebox.showerror("Erreur", f"Impossible de démarrer l'agent: {e}")

        threading.Thread(target=init_agent, daemon=True).start()

    def send_message(self, event=None):
        """Envoie un message avec animations avatar"""
        message = self.input_var.get().strip()
        if not message or not self.is_running:
            return

        # Animation : l'utilisateur parle
        self.avatar.set_expression("neutral")
        
        # Ajouter le message utilisateur
        self.add_message("👤 Vous", message)
        self.input_var.set("")
        
        # Animation : l'agent réfléchit
        self.typing_var.set("🤖 AgentTK réfléchit...")
        self.avatar.start_thinking()

        # Traiter en arrière-plan
        def process_message():
            try:
                response = self.agent.process_message(message)
                
                # Animation : l'agent répond
                self.avatar.stop_thinking()
                self.avatar.start_speaking()
                self.typing_var.set("🤖 AgentTK répond...")
                
                self.add_message("🤖 AgentTK", response)
                
                # Arrêter l'animation après la réponse
                self.root.after(1000, self.avatar.stop_speaking)
                self.typing_var.set("")
                
            except Exception as e:
                self.avatar.stop_thinking()
                self.avatar.show_emotion("error", 2000)
                self.typing_var.set("")
                self.add_message("🤖 Erreur", f"Désolé, une erreur est survenue: {e}")

        threading.Thread(target=process_message, daemon=True).start()

    def show_auto_improvement_dialog(self):
        """Dialogue d'auto-amélioration avec feedback avatar"""
        if not self.is_running:
            messagebox.showwarning("Auto-Amélioration", "L'agent n'est pas encore prêt.")
            return

        improvement_window = tk.Toplevel(self.root)
        improvement_window.title("🔧 Auto-Amélioration par Recherche Web")
        improvement_window.geometry("500x350")
        improvement_window.transient(self.root)
        improvement_window.grab_set()

        main_frame = ttk.Frame(improvement_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="🔧 Auto-Amélioration Intelligente",
                  font=('Arial', 14, 'bold'), foreground='#FF9800').pack(pady=(0, 15))

        ttk.Label(main_frame, text="Améliorez la reconnaissance d'intentions via Google",
                  font=('Arial', 10)).pack(pady=(0, 20))

        # Sélection d'intention
        ttk.Label(main_frame, text="Intention à améliorer:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        intent_var = tk.StringVar()
        intents = ["greeting", "web_search", "calculation", "time", "task_add", "task_list", "file_operation"]
        intent_combo = ttk.Combobox(main_frame, textvariable=intent_var, values=intents, state="readonly")
        intent_combo.pack(fill=tk.X, pady=10)
        intent_combo.set("web_search")

        status_var = tk.StringVar(value="Prêt à améliorer...")
        status_label = ttk.Label(main_frame, textvariable=status_var, foreground='#666', font=('Arial', 9))
        status_label.pack(pady=10)

        improvement_button = ttk.Button(
            main_frame,
            text="🚀 Lancer l'Auto-Amélioration",
            command=lambda: None
        )
        improvement_button.pack(pady=20)

        def start_improvement():
            if self.improvement_in_progress:
                return

            intent = intent_var.get()
            if not intent:
                messagebox.showwarning("Erreur", "Veuillez sélectionner une intention")
                return

            self.improvement_in_progress = True
            status_var.set("🔍 Recherche sur Google...")
            improvement_button.config(state=tk.DISABLED)
            self.avatar.start_speaking()

            def improve():
                try:
                    self.add_message("🔧 Système", f"Lancement de l'auto-amélioration pour '{intent}'...")
                    result = self.agent.auto_improve_intent(intent)

                    def update_ui():
                        if result.success:
                            status_var.set("✅ Amélioration terminée!")
                            self.avatar.stop_speaking()
                            self.avatar.set_expression("happy")
                            
                            self.add_message("🔧 Auto-Amélioration", result.message, "improvement")

                            details = f"**Détails de l'amélioration:**\n"
                            if result.patterns_added:
                                details += f"• Patterns ajoutés: {len(result.patterns_added)}\n"
                                for pattern in result.patterns_added[:3]:
                                    details += f"  - {pattern}\n"
                            if result.examples_added:
                                details += f"• Exemples ajoutés: {len(result.examples_added)}\n"

                            self.add_message("🔧 Détails", details)

                        else:
                            status_var.set("❌ Échec de l'amélioration")
                            self.avatar.stop_thinking()
                            self.avatar.show_emotion("error", 2000)
                            self.add_message("🔧 Erreur", result.message)

                        improvement_button.config(state=tk.NORMAL)
                        self.improvement_in_progress = False
                        self.show_ml_stats()

                    self.root.after(0, update_ui)

                except Exception as e:
                    def show_error():
                        status_var.set("❌ Erreur lors de l'amélioration")
                        self.avatar.stop_thinking()
                        self.avatar.show_emotion("error", 2000)
                        self.add_message("🔧 Erreur", f"Erreur d'auto-amélioration: {e}")
                        improvement_button.config(state=tk.NORMAL)
                        self.improvement_in_progress = False

                    self.root.after(0, show_error)

            threading.Thread(target=improve, daemon=True).start()

        improvement_button.config(command=start_improvement)

        ttk.Button(
            main_frame,
            text="❌ Fermer",
            command=improvement_window.destroy
        ).pack()

        # Gérer la fermeture de la fenêtre
        def on_closing():
            if not self.improvement_in_progress:
                improvement_window.destroy()

        improvement_window.protocol("WM_DELETE_WINDOW", on_closing)

    def show_feedback_dialog(self):
        """Affiche la boîte de dialogue de feedback"""
        if not self.is_running:
            messagebox.showwarning("Feedback", "L'agent n'est pas encore prêt.")
            return

        # Créer une fenêtre de dialogue
        feedback_window = tk.Toplevel(self.root)
        feedback_window.title("💡 Feedback - Améliorer AgentTK")
        feedback_window.geometry("500x400")
        feedback_window.transient(self.root)
        feedback_window.grab_set()

        # Frame principal
        main_frame = ttk.Frame(feedback_window, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Titre
        ttk.Label(
            main_frame,
            text="Aidez-moi à mieux comprendre !",
            font=('Arial', 14, 'bold'),
            foreground='#4CAF50'
        ).pack(pady=(0, 15))

        # Historique des messages récents
        ttk.Label(main_frame, text="Messages récents :", font=('Arial', 10, 'bold')).pack(anchor=tk.W)

        recent_messages_frame = ttk.Frame(main_frame)
        recent_messages_frame.pack(fill=tk.X, pady=5)

        self.recent_message_var = tk.StringVar()
        recent_messages_combo = ttk.Combobox(
            recent_messages_frame,
            textvariable=self.recent_message_var,
            values=self._get_recent_user_messages(),
            state="readonly",
            width=50
        )
        recent_messages_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        recent_messages_combo.bind('<<ComboboxSelected>>', self._on_message_selected)

        # Intention prédite
        ttk.Label(main_frame, text="Intention prédite :", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 0))

        self.predicted_intent_var = tk.StringVar(value="Sélectionnez un message")
        predicted_intent_label = ttk.Label(
            main_frame,
            textvariable=self.predicted_intent_var,
            foreground='#2196F3',
            font=('Arial', 9)
        )
        predicted_intent_label.pack(anchor=tk.W)

        # Intention correcte
        ttk.Label(main_frame, text="Intention correcte :", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 0))

        intent_frame = ttk.Frame(main_frame)
        intent_frame.pack(fill=tk.X, pady=5)

        self.correct_intent_var = tk.StringVar()
        intents = ["greeting", "calculation", "time", "web_search", "task_add", "task_list", "file_operation",
                   "system_info", "personal", "thanks", "farewell", "unknown"]

        intent_combo = ttk.Combobox(
            intent_frame,
            textvariable=self.correct_intent_var,
            values=intents,
            state="readonly"
        )
        intent_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Commentaire
        ttk.Label(main_frame, text="Commentaire (optionnel) :", font=('Arial', 10, 'bold')).pack(anchor=tk.W,
                                                                                                 pady=(10, 0))

        self.comment_var = tk.StringVar()
        comment_entry = ttk.Entry(
            main_frame,
            textvariable=self.comment_var,
            width=50
        )
        comment_entry.pack(fill=tk.X, pady=5)

        # Boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)

        ttk.Button(
            button_frame,
            text="✅ Envoyer Feedback",
            command=lambda: self._submit_feedback(feedback_window)
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            button_frame,
            text="❌ Annuler",
            command=feedback_window.destroy
        ).pack(side=tk.RIGHT)

    def _get_recent_user_messages(self):
        """Récupère les messages utilisateur récents"""
        recent_messages = []
        for entry in self.chat_log[-10:]:  # 10 derniers messages
            if entry['sender'].startswith("👤"):
                recent_messages.append(entry['message'])
        return list(reversed(recent_messages))  # Du plus récent au plus ancien

    def _on_message_selected(self, event):
        """Quand un message est sélectionné dans la liste"""
        selected_message = self.recent_message_var.get()
        if selected_message and self.agent:
            # Simuler le traitement pour obtenir l'intention prédite
            try:
                # Utiliser la reconnaissance d'intention pour obtenir la prédiction
                intent_result = self.agent._recognize_intent_with_ml(selected_message)
                self.predicted_intent_var.set(f"{intent_result.name} (confiance: {intent_result.confidence:.2f})")

                # Pré-remplir l'intention correcte avec la prédiction
                self.correct_intent_var.set(intent_result.name)

            except Exception as e:
                self.predicted_intent_var.set("Erreur de prédiction")

    def _submit_feedback(self, window):
        """Soumet le feedback à l'agent et lance l'auto-amélioration si nécessaire"""
        user_message = self.recent_message_var.get()
        correct_intent = self.correct_intent_var.get()
        comment = self.comment_var.get()

        if not user_message:
            messagebox.showwarning("Feedback", "Veuillez sélectionner un message.")
            return

        if not correct_intent:
            messagebox.showwarning("Feedback", "Veuillez sélectionner l'intention correcte.")
            return

        try:
            # Obtenir l'intention prédite originale
            intent_result = self.agent._recognize_intent_with_ml(user_message)
            predicted_intent = intent_result.name

            # Envoyer le feedback à l'agent
            self.agent.provide_feedback(user_message, predicted_intent, correct_intent)

            # Ajouter un message de confirmation dans le chat
            feedback_msg = f"✅ Feedback enregistré : '{user_message}' → {correct_intent}"
            if comment:
                feedback_msg += f"\n💬 Commentaire : {comment}"

            self.add_message("💡 Système", feedback_msg)

            # Si correction détectée, lancer l'auto-amélioration automatique
            if predicted_intent != correct_intent:
                self.add_message("🔧 Système", "Correction détectée, lancement de l'auto-amélioration...")

                def auto_improve():
                    try:
                        result = self.agent.auto_improve_intent(correct_intent)
                        if result.success:
                            self.add_message("🔧 Auto-Amélioration",
                                             f"✅ Système amélioré pour '{correct_intent}'!\n" +
                                             f"• {len(result.patterns_added)} patterns ajoutés\n" +
                                             f"• {len(result.examples_added)} exemples d'entraînement",
                                             "improvement")
                    except Exception as e:
                        self.add_message("🔧 Erreur", f"Auto-amélioration échouée: {e}")

                threading.Thread(target=auto_improve, daemon=True).start()

            # Fermer la fenêtre
            window.destroy()

            # Mettre à jour les stats ML
            self.show_ml_stats()

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'envoyer le feedback : {e}")

    def show_ml_stats(self):
        """Affiche les statistiques ML"""
        if not self.is_running:
            return

        def get_stats():
            try:
                stats = self.agent.get_ml_stats()
                if stats.get("ml_enabled"):
                    model_info = stats["model"]
                    feedback_stats = stats["feedback"]

                    response = "🤖 **Statistiques Apprentissage Automatique**\n\n"
                    response += f"📊 **Modèle :**\n"
                    response += f"• Entraîné : {'✅' if model_info['is_trained'] else '❌'}\n"
                    response += f"• Exemples d'entraînement : {model_info['training_examples']}\n"

                    if model_info['intents_count']:
                        response += f"• Intentions reconnues : {len(model_info['intents_count'])}\n"

                    response += f"\n📈 **Performance :**\n"
                    response += f"• Précision : {feedback_stats.get('accuracy', 0):.1%}\n"
                    response += f"• Feedback total : {feedback_stats.get('total_feedback', 0)}\n"

                    self.add_message("📊 Stats ML", response)
                else:
                    self.add_message("📊 Stats ML", "🤖 Système ML désactivé")

            except Exception as e:
                self.add_message("📊 Erreur", f"Impossible de récupérer les stats ML: {e}")

        threading.Thread(target=get_stats, daemon=True).start()

    def clear_chat(self):
        """Efface l'historique de chat"""
        if messagebox.askyesno("Effacer", "Voulez-vous effacer l'historique de conversation ?"):
            self.chat_history.config(state=tk.NORMAL)
            self.chat_history.delete(1.0, tk.END)
            self.chat_history.config(state=tk.DISABLED)
            self.add_message("🤖 AgentTK", "Historique effacé. Comment puis-je vous aider ?")

    def setup_agent(self):
        """Initialise l'agent"""

        def init_agent():
            try:
                self.status_var.set("🟡 Démarrage de l'agent...")
                self.agent = Agent("AgentTK", "config.yaml")
                self.is_running = True
                self.status_var.set("🟢 Agent prêt")
                self.add_message("🤖 AgentTK",
                                 "Bonjour ! Je suis votre assistant IA avec auto-amélioration. Tapez 'aide' pour voir mes capacités.")
            except Exception as e:
                self.status_var.set("🔴 Erreur de démarrage")
                messagebox.showerror("Erreur", f"Impossible de démarrer l'agent: {e}")

        threading.Thread(target=init_agent, daemon=True).start()

    def send_message(self, event=None):
        """Envoie un message à l'agent"""
        message = self.input_var.get().strip()
        if not message or not self.is_running:
            return

        # Ajouter le message utilisateur
        self.add_message("👤 Vous", message)
        self.input_var.set("")
        self.typing_var.set("🤖 AgentTK réfléchit...")

        # Traiter en arrière-plan
        def process_message():
            try:
                response = self.agent.process_message(message)
                self.typing_var.set("")
                self.add_message("🤖 AgentTK", response)
            except Exception as e:
                self.typing_var.set("")
                self.add_message("🤖 Erreur", f"Désolé, une erreur est survenue: {e}")

        threading.Thread(target=process_message, daemon=True).start()

    def add_message(self, sender: str, message: str, tag_override: str = None):
        """Ajoute un message à l'historique avec formatage amélioré"""
        self.chat_history.config(state=tk.NORMAL)

        # Sauvegarder dans le log
        self.chat_log.append({
            'sender': sender,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })

        # Sauvegarder périodiquement
        if len(self.chat_log) % 10 == 0:
            self.save_chat_history()

        # Déterminer le tag selon l'expéditeur ou override
        if tag_override:
            tag = tag_override
        elif sender.startswith("👤"):
            tag = "user"
        elif sender.startswith("🤖"):
            tag = "agent"
        else:
            tag = "system"

        # Ajouter le message avec formatage basique
        self.chat_history.insert(tk.END, f"{sender}: ", tag)

        # Formatage simple pour le markdown
        lines = message.split('\n')
        for i, line in enumerate(lines):
            if line.startswith("**") and line.endswith("**"):
                # Texte en gras
                clean_line = line.strip('*')
                self.chat_history.insert(tk.END, clean_line, "bold")
            elif line.startswith("* ") or line.startswith("• "):
                # Liste à puces
                self.chat_history.insert(tk.END, line)
            else:
                # Texte normal
                self.chat_history.insert(tk.END, line)

            if i < len(lines) - 1:
                self.chat_history.insert(tk.END, '\n')

        self.chat_history.insert(tk.END, "\n\n")
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.see(tk.END)

    def save_chat_history(self):
        """Sauvegarde l'historique de chat"""
        try:
            with open('chat_history.json', 'w', encoding='utf-8') as f:
                json.dump(self.chat_log, f, ensure_ascii=False, indent=2)
        except Exception:
            pass  # Ignorer les erreurs de sauvegarde

    def show_tasks(self):
        """Affiche les tâches"""
        if not self.is_running:
            return

        def get_tasks():
            try:
                if "task_manager" in self.agent.skills:
                    result = self.agent.skills["task_manager"].execute(intent="task_list")
                    if result.success:
                        self.add_message("📋 Tâches", result.message)
                    else:
                        self.add_message("📋 Tâches", "Aucune tâche en attente")
                else:
                    self.add_message("📋 Tâches", "Compétence tâches non disponible")
            except Exception as e:
                self.add_message("📋 Erreur", f"Impossible de récupérer les tâches: {e}")

        threading.Thread(target=get_tasks, daemon=True).start()

    def show_calculator(self):
        """Ouvre la calculatrice"""
        if not self.is_running:
            return

        self.add_message("🧮 Calculatrice", "Tapez une expression mathématique comme 'calcule 5 + 3'")

    def show_time(self):
        """Affiche l'heure"""
        if not self.is_running:
            return

        def get_time():
            try:
                if "time_skill" in self.agent.skills:
                    result = self.agent.skills["time_skill"].execute(intent="time")
                    if result.success:
                        self.add_message("🕐 Heure", result.message)
                else:
                    self.add_message("🕐 Heure", "Compétence temps non disponible")
            except Exception as e:
                self.add_message("🕐 Erreur", f"Impossible de récupérer l'heure: {e}")

        threading.Thread(target=get_time, daemon=True).start()

    def show_files(self):
        """Affiche les fichiers"""
        if not self.is_running:
            return

        def get_files():
            try:
                if "file_manager" in self.agent.skills:
                    result = self.agent.skills["file_manager"].execute(intent="file_operation",
                                                                       message="liste les fichiers")
                    if result.success:
                        self.add_message("📁 Fichiers", result.message)
                    else:
                        self.add_message("📁 Fichiers", "Impossible de lister les fichiers")
                else:
                    self.add_message("📁 Fichiers", "Compétence fichiers non disponible")
            except Exception as e:
                self.add_message("📁 Erreur", f"Impossible de lister les fichiers: {e}")

        threading.Thread(target=get_files, daemon=True).start()

    def show_help(self):
        """Affiche l'aide"""
        help_text = """
**Commandes disponibles:**

**TÂCHES**
• 'ajoute une tâche [description]'
• 'liste les tâches'

**CALCULS** 
• 'calcule [expression]'
• 'combien fait [expression]'

**TEMPS**
• 'quelle heure est-il ?'
• 'quelle date sommes-nous ?'

**FICHIERS**
• 'crée un dossier [nom]'
• 'liste les fichiers'

**RECHERCHE**
• 'recherche [sujet]'
• 'cherche [sujet]'
• 'c'est quoi [sujet]'
• 'qui est [personne]'
• 'résume moi [sujet]'

**SYSTÈME**
• 'info système'
• 'aide'

**NOUVEAU : Auto-Amélioration**
• Utilisez le bouton "🔧 Auto-Améliore" pour améliorer la reconnaissance
• Le système s'améliore automatiquement après les feedbacks
• Recherche Google automatique pour trouver de nouvelles phrases

Utilisez les boutons pour un accès rapide !
"""
        self.add_message("💡 Aide", help_text)

    def show_web_search(self):
        """Ouvre la recherche web"""
        if not self.is_running:
            return

        self.add_message("🌐 Recherche Web",
                         "Tapez 'recherche [votre requête]' pour chercher sur le web. Exemple: 'recherche intelligence artificielle'")

    def quit_app(self):
        """Quitte l'application"""
        if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter AgentTK ?"):
            self.root.quit()
            self.root.destroy()

    def run(self):
        """Lance l'interface"""
        self.root.mainloop()


def main():
    """Point d'entrée de l'UI"""
    try:
        app = AgentTKUI()
        app.run()
    except Exception as e:
        print(f"Erreur lors du démarrage de l'UI: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
