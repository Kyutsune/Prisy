# Prisy - Bot Discord de Musique 🎶

**Prisy** est un bot Discord développé en Python, qui permet de lire de la musique depuis YouTube à l’aide de **slash-commands** uniquement.
Il est conçu pour être **asynchrone**, stable (pas de déconnexion aléatoire), et facile à maintenir.

---

## 📦 Fonctionnalités principales

* `/play [titre|url]` — Recherche et joue une musique depuis YouTube
* `/queue` — Affiche la file d’attente dans un embed
* `/skip` — Passe à la piste suivante et affiche le titre suivant
* `/leave` — Fait quitter le salon vocal au bot
* 🎮 Lecture fluide grâce à FFmpeg + encodage Opus
* 📊 Statistiques locales :

  * Titres les plus joués (`stats_musique.json`)
  * Contributeurs les plus actifs (`stats_contributeur.json`)

---

## ⚙️ Pré-requis
* Un fichier `.env` à la racine avec :

```
DISCORD_TOKEN=token_bot
GUILD_ID=id_serveur
```

## 🚀 Lancement

Créer un environnement virtuel (recommandé) :

```bash
python -m venv venv
source venv/bin/activate  # ou .\venv\Scripts\activate sous Windows
```

Installer les dépendances :

```bash
pip install -r requirements.txt # ou pip install -r .\requirements.txt sous Windows
```

Lancer le bot normalement :

```bash
python3 -m bot.main
```

---

## ✅ Bonnes pratiques de développement

* Ajouter de nouvelles commandes via `@app_commands.command(...)` dans un `Cog`
* Toujours les restreindre à la guilde (`@app_commands.guilds(...)`)
* Éviter toute utilisation de `asyncio.sleep()` dans la lecture audio

---

## 👨‍💻 Développement

Projet développé par Papailles & Kyutsune

TODO : 

* Ajouter de nouvelles commandes
* Améliorer les stats (classement, top 10…)
* Créer une interface web ou dashboard plus visuel (si on est chauds)
