import json
import os

STATS_FILE = os.path.join(os.path.dirname(__file__), "stats.json")

def load_stats():
    if not os.path.exists(STATS_FILE):
        return {}
    with open(STATS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_stats(stats):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=4)

def increment_play_count(title: str):
    print(f"[increment_play_count] Incrémentation du compteur de lecture pour : {title}")
    stats = load_stats()
    stats[title] = stats.get(title, 0) + 1
    save_stats(stats)
