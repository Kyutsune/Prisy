import json
import os

STATS_MUSIQUE_FILE = os.path.join(os.path.dirname(__file__), "stats_musique.json")
STATS_CONTRIBUTER_FILE = os.path.join(os.path.dirname(__file__), "stats_contributeur.json")

def load_stats_musique():
    if not os.path.exists(STATS_MUSIQUE_FILE):
        return {}
    with open(STATS_MUSIQUE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_stats_contributeur():
    if not os.path.exists(STATS_CONTRIBUTER_FILE):
        return {}
    with open(STATS_CONTRIBUTER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_stats_musique(stats):
    with open(STATS_MUSIQUE_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=4)

def save_stats_contributeur(stats):
    with open(STATS_CONTRIBUTER_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=4)

def increment_play_count(title: str, member: str):
    print(f"[increment_play_count] Incrémentation du compteur de lecture pour : {title}")
    stats_musique = load_stats_musique()
    stats_musique[title] = stats_musique.get(title, 0) + 1

    stats_contributeur = load_stats_contributeur()
    stats_contributeur[member] = stats_contributeur.get(member, 0) + 1
    save_stats_contributeur(stats_contributeur)
    save_stats_musique(stats_musique)
