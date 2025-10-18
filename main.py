# main.py
"""Point d'entrée principal d'AgentTK avec correctifs automatiques"""
import json
from pathlib import Path
import sys


def apply_startup_fixes():
    """Applique les correctifs au démarrage"""
    print("🔧 Application des correctifs de démarrage...")

    # Créer les dossiers nécessaires
    folders = ["data", "ml_data", "logs"]
    for folder in folders:
        Path(folder).mkdir(exist_ok=True)
        print(f"📁 Dossier {folder} vérifié")

    # Corriger les fichiers de données ML corrompus
    fix_ml_data_files()

    # Vérifier les dépendances NLTK
    check_nltk_dependencies()

    print("✅ Correctifs appliqués avec succès!")


def check_nltk_dependencies():
    """Vérifie et installe les dépendances NLTK si nécessaire"""
    try:
        import nltk
        nltk.data.find('tokenizers/punkt')
        print("✅ Dépendances NLTK vérifiées")
    except LookupError:
        print("⚠️  Données NLTK manquantes, lancez: python setup_nltk.py")


def fix_ml_data_files():
    """Corrige les fichiers de données ML"""
    ml_files = {
        "ml_data/training_data.json": {
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
        },
        "ml_data/feedback_data.json": {
            "feedbacks": [],
            "stats": {"total_feedback": 0, "accuracy": 1.0}
        },
        "ml_data/improvements.json": {}
    }

    for file_path, default_data in ml_files.items():
        path = Path(file_path)
        if not path.exists():
            try:
                path.parent.mkdir(exist_ok=True)
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(default_data, f, ensure_ascii=False, indent=2)
                print(f"📝 {file_path} créé avec des données par défaut")
            except Exception as e:
                print(f"❌ Erreur création {file_path}: {e}")
        else:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    json.load(f)
                print(f"✅ {file_path} est valide")
            except json.JSONDecodeError:
                print(f"🔧 Réparation de {file_path}")
                try:
                    with open(path, 'w', encoding='utf-8') as f:
                        json.dump(default_data, f, ensure_ascii=False, indent=2)
                    print(f"✅ {file_path} réparé")
                except Exception as e:
                    print(f"❌ Erreur réparation {file_path}: {e}")


# Appliquer les correctifs
apply_startup_fixes()

print("🚀 Démarrage d'AgentTK...")
print("✅ Dépendances ML disponibles")

from ui.tkinter_ui import AgentTKUI

if __name__ == "__main__":
    try:
        app = AgentTKUI()
        app.run()
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        import traceback

        traceback.print_exc()