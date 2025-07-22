"""
bot/stats/stats.py
Statistiques du bot PrisyBot
Contient des fonctions pour charger, sauvegarder et incrémenter 
les statistiques de musique et de contributeurs.
"""
import json
from pathlib import Path
import threading

# Emplacement des fichiers de stats dans le dossier services
BASE = Path(__file__).parent
STATS_MUSIQUE_FILE = BASE / "stats_musique.json"
STATS_CONTRIBUTEUR_FILE = BASE / "stats_contributeur.json"

_lock = threading.Lock()  # pour éviter les collisions d'écriture

def load_stats_musique() -> dict[str,int]:
    """Charge les statistiques de musique depuis le fichier JSON.
    Si le fichier n'existe pas, retourne un dictionnaire vide."""
    if not STATS_MUSIQUE_FILE.exists():
        return {}
    return json.loads(STATS_MUSIQUE_FILE.read_text(encoding="utf-8"))

def load_stats_contributeur() -> dict[str,int]:
    """Charge les statistiques des contributeurs depuis le fichier JSON.
    Si le fichier n'existe pas, retourne un dictionnaire vide."""
    if not STATS_CONTRIBUTEUR_FILE.exists():
        return {}
    return json.loads(STATS_CONTRIBUTEUR_FILE.read_text(encoding="utf-8"))

def save_stats_musique(stats: dict[str,int]) -> None:
    """Sauvegarde les statistiques de musique dans le fichier JSON."""
    with _lock, STATS_MUSIQUE_FILE.open("w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=4)

def save_stats_contributeur(stats: dict[str,int]) -> None:
    """Sauvegarde les statistiques des contributeurs dans le fichier JSON."""
    with _lock, STATS_CONTRIBUTEUR_FILE.open("w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=4)

def increment_play_count(title: str, member_name: str) -> None:
    """
    Incrémente le compteur de la musique et celui du contributeur.
    """
    # Charge, modifie, sauve
    stats_musique = load_stats_musique()
    stats_musique[title] = stats_musique.get(title, 0) + 1
    save_stats_musique(stats_musique)

    stats_contrib = load_stats_contributeur()
    stats_contrib[member_name] = stats_contrib.get(member_name, 0) + 1
    save_stats_contributeur(stats_contrib)
