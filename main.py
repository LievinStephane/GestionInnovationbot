import os
import json
import time
import unicodedata
import re
from flask import Flask
from multiprocessing import Process
from telegram import Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.error import NetworkError

# ✅ Récupération du token Telegram
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("❌ Erreur : La variable d'environnement 'TOKEN' est vide. Ajoutez votre token dans Replit.")

# ✅ Création du bot
bot = Bot(TOKEN)

try:
    bot.get_me()
    print("✅ Token valide, le bot fonctionne !")
except Exception as e:
    raise ValueError(f"❌ Erreur : Token invalide ! {e}")

# ✅ Chemin du dossier contenant les fichiers JSON
JSON_DIR = "/mnt/data/"

# ✅ Fonction pour charger un fichier JSON en toute sécurité
def load_json(filename):
    file_path = os.path.join(JSON_DIR, filename)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        print(f"⚠️ Fichier manquant : {file_path}")
        return None  # Retourne None si le fichier est absent

# ✅ Liste des fichiers JSON nécessaires
json_files = [
    "introduction.json", "conception_innovante.json", "approche_ck.json",
    "organisation_innovation.json", "innovation_sobriete.json", "valeur_et_innovation.json",
    "conclusion.json", "annexe.json", "bibliographie.json", "sitographie.json"
]

# ✅ Vérification des fichiers JSON avant lancement
compte_rendu = {}
for json_file in json_files:
    data = load_json(json_file)
    if data:
        compte_rendu.update(data)  # Fusionner les contenus des fichiers JSON

# ✅ Création du serveur Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Le bot Telegram est actif !"

# ✅ Fonction pour nettoyer les noms des commandes
def clean_command_name(section_name):
    section_clean = section_name.lower()
    section_clean = ''.join(c for c in unicodedata.normalize('NFD', section_clean) if unicodedata.category(c) != 'Mn')
    section_clean = re.sub(r'[^a-z0-9]', '_', section_clean)  # Remplacer tout caractère non alphanumérique par "_"
    section_clean = re.sub(r'_+', '_', section_clean).strip('_')  # Supprimer les multiples "_"
    return section_clean[:32]  # Limite de 32 caractères pour les commandes Telegram

# ✅ Fonction pour découper et envoyer un long texte
def envoyer_texte_long(update, texte):
    max_length = 4000  # ⚠️ Limite de Telegram
    paragraphs = texte.split("\n")

    message_chunk = ""
    for para in paragraphs:
        if len(message_chunk) + len(para) + 1 < max_length:
            message_chunk += para + "\n"
        else:
            update.message.reply_text(message_chunk)
            message_chunk = para + "\n"

    if message_chunk:
        update.message.reply_text(message_chunk)

# ✅ Commande /start : Image → Menu → Audio
def start(update, context):
    chat_id = update.message.chat_id

    # 🖼️ Envoi de l'image
    try:
        context.bot.send_photo(chat_id=chat_id, photo=open(os.path.join(JSON_DIR, "Image1.png"), "rb"))
        time.sleep(1)
    except Exception:
        update.message.reply_text("⚠️ Impossible d'envoyer l'image. Vérifiez que 'Image1.png' est bien dans le dossier.")

    # 📌 Affichage du menu
    menu_text = (
        "😃 Bonjour !\n\n"
        "Je suis votre assistant pour consulter le dossier sur les innovations chez **Team for The Planet**.\n"
        "**📌 Commandes disponibles :**\n"
    )
    for section in compte_rendu.keys():
        command = clean_command_name(section)
        menu_text += f"🔹 /{command} - Voir {section}\n"

    menu_text += (
        "\n📹 **Vidéos disponibles :**\n"
        "🎬 /videointro - Voir l'introduction en vidéo.\n"
        "🎥 /video - Voir une vidéo sur un projet soutenu par TftP.\n"
    )
    update.message.reply_text(menu_text)

    # 🎵 Envoi du fichier audio
    try:
        time.sleep(2)
        context.bot.send_audio(chat_id=chat_id, audio=open(os.path.join(JSON_DIR, "accueil.wav"), "rb"))
        update.message.reply_text("🎵 Message en cours de lecture...")
    except Exception:
        update.message.reply_text("⚠️ Impossible d'envoyer l'audio. Vérifiez que 'accueil.wav' est bien dans le dossier.")

# ✅ Commande /aide : liste les sections disponibles
def aide(update, context):
    menu_text = "**📌 Commandes disponibles :**\n"
    for section in compte_rendu.keys():
        command = clean_command_name(section)
        menu_text += f"🔹 /{command} - Voir {section}\n"

    menu_text += (
        "\n📹 **Vidéos disponibles :**\n"
        "🎬 /videointro - Voir l'introduction en vidéo.\n"
        "🎥 /video - Voir une vidéo sur un projet soutenu par TftP.\n"
    )
    update.message.reply_text(menu_text)

# ✅ Fonction pour afficher une section du compte rendu
def afficher_section(update, context: CallbackContext):
    raw_command = update.message.text[1:]  # Supprime le "/"
    for section in compte_rendu.keys():
        if clean_command_name(section) == raw_command:
            texte_complet = f"📌 **{section}** :\n\n{compte_rendu[section]}"
            envoyer_texte_long(update, texte_complet)
            return
    update.message.reply_text("⚠️ Cette section n'existe pas dans le compte rendu.")

# ✅ Commande /video : envoie le lien YouTube
def envoyer_video(update, context):
    update.message.reply_text("🎥 Voici une vidéo sur Midipile Mobility :")
    update.message.reply_text("https://www.youtube.com/watch?v=6pvfuFFDLzc")

# ✅ Commande /videointro : envoie la vidéo locale
def envoyer_videointro(update, context):
    chat_id = update.message.chat_id
    try:
        context.bot.send_video(chat_id=chat_id, video=open(os.path.join(JSON_DIR, "VideoIntro.mp4"), "rb"))
        update.message.reply_text("🎬 Voici l'introduction en vidéo.")
    except Exception:
        update.message.reply_text("⚠️ Impossible d'envoyer la vidéo. Vérifiez que 'VideoIntro.mp4' est bien dans le dossier.")

# ✅ Fonction principale du bot
def run_bot():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("aide", aide))
    dp.add_handler(CommandHandler("video", envoyer_video))
    dp.add_handler(CommandHandler("videointro", envoyer_videointro))

    for section in compte_rendu.keys():
        command = clean_command_name(section)
        print(f"🔹 Ajout de la commande : /{command}")
        dp.add_handler(CommandHandler(command, afficher_section))

    updater.start_polling()
    updater.idle()

# ✅ Lancement du serveur Flask et du bot
if __name__ == "__main__":
    Process(target=app.run, kwargs={"host": "0.0.0.0", "port": 8080}).start()
    run_bot()
