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

* Python 3.11 ou 3.12
* `ffmpeg` installé et accessible via le terminal (`ffmpeg -version`)
* Un fichier `.env` à la racine avec :

```
DISCORD_TOKEN=token_bot
GUILD_ID=id_serveur
```

---

## 🏐 Structure du projet

```
Prisy/
├── bot/
│   ├── cogs/              # Commandes slash (music.py, utility.py…)
│   ├── config.py          # TOKEN, GUILD_ID, options globales
│   ├── main.py            # Point d’entrée du bot
│   ├── services/          # Extraction audio (yt_dlp), ffmpeg config
│   └── stats/             # Gestion des fichiers stats JSON
│       ├── stats_musique.json
│       ├── stats_contributeur.json
│       └── stats.py
├── .env                   # Variables d’environnement (token)
├── requirements.txt
└── README.md
```

---

## 🚀 Lancement

Créer un environnement virtuel (recommandé) :

```bash
python -m venv venv
source venv/bin/activate  # ou .\venv\Scripts\activate sous Windows
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

Lancer le bot normalement :

```bash
python -m bot.main
```

---

## 🧠 Détails techniques

* **yt\_dlp** est utilisé pour extraire les flux audio YouTube (pas de téléchargement)
* **FFmpegOpusAudio** est utilisé pour un encodage Opus performant
* Lecture **asynchrone non bloquante** via `vc.play(..., after=...)`
* La file d’attente et les accès concurrents sont gérés avec :

  * `self.queues[guild_id]` → file par guilde
  * `self.locks[guild_id]` → verrou par guilde
* Les stats sont stockées en local dans des fichiers `.json`

---

## 🦖 Commandes à tester

```bash
/play never gonna give you up
/queue
/skip
/leave
```

---

## ✅ Bonnes pratiques de développement

* Ajouter de nouvelles commandes via `@app_commands.command(...)` dans un `Cog`
* Toujours les restreindre à la guilde (`@app_commands.guilds(...)`)
* Éviter toute utilisation de `asyncio.sleep()` dans la lecture audio

---

## 👨‍💻 Développement

Projet développé par \Papailles & Kyutsune

TODO : 

* Ajouter de nouvelles commandes
* Améliorer les stats (classement, top 10…)
* Créer une interface web ou dashboard plus visuel (si on est chauds)
