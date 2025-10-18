# setup_nltk.py
"""Script pour télécharger les données NLTK nécessaires"""
import nltk
import os

def download_nltk_data():
    """Télécharge les données NLTK nécessaires pour sumy"""
    print("📥 Téléchargement des données NLTK...")
    
    try:
        # Données nécessaires pour le tokenizer français
        nltk.download('punkt', quiet=False)
        nltk.download('stopwords', quiet=False)
        
        # Télécharger les données pour le français
        nltk.download('punkt_tab', quiet=False)
        
        print("✅ Données NLTK téléchargées avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur téléchargement NLTK: {e}")
        print("⚠️  Les résumés automatiques pourraient ne pas fonctionner correctement.")

if __name__ == "__main__":
    download_nltk_data()