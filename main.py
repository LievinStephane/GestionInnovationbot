import os
import json
import time
import unicodedata
import re
from flask import Flask
from multiprocessing import Process
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.error import NetworkError, BadRequest

# Récupération du token Telegram
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("❌ Erreur : La variable d'environnement 'TOKEN' est vide. Ajoute ton token dans Replit.")

# Création du bot
bot = Bot(TOKEN)

try:
    bot.get_me()
    print("✅ Token valide, le bot fonctionne !")
except Exception as e:
    raise ValueError(f"❌ Erreur : Token invalide ! {e}")

# Définition du répertoire des fichiers JSON
JSON_DIR = "./"

# Création du serveur Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Le bot Telegram est actif !"

# Charger un fichier JSON
def load_json(filename):
    try:
        filepath = os.path.join(JSON_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"⚠️ Erreur de lecture du fichier JSON : {filename}")
        return None

# Nettoyer les noms des sections pour Telegram
def clean_command_name(section_name):
    section_clean = section_name.lower()
    section_clean = ''.join(c for c in unicodedata.normalize('NFD', section_clean) if unicodedata.category(c) != 'Mn')
    section_clean = re.sub(r'[^a-z0-9]', '_', section_clean)
    section_clean = re.sub(r'_+', '_', section_clean).strip('_')

    if not section_clean or not section_clean[0].isalpha():
        section_clean = f"section_{section_clean}"

    return section_clean[:32]  # Limite de 32 caractères imposée par Telegram

# Fonction pour envoyer un long texte
def envoyer_texte_long(update, texte):
    max_length = 4000  # Limite de Telegram
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

# Commande /start
def start(update, context):
    chat_id = update.message.chat_id

    # Envoi de l'image principale
    try:
        context.bot.send_photo(chat_id=chat_id, photo=open("Image1.png", "rb"))
        time.sleep(1)
    except Exception:
        update.message.reply_text("⚠️ Impossible d'envoyer l'image.")

    # Affichage du menu
    menu_text = (
        "😃 Bonjour Gilles !\n\n"
        "Je suis votre assistant pour consulter le dossier sur les innovations chez **Team for The Planet**.\n"
        "Travail réalisé par Carine, Pierre, David et Stéphane dans le cadre du GDN217 - Gestion de l'Innovation.\n\n"
        "**📌 Commandes disponibles :**\n"
        "🔹 /introduction - Voir l'introduction\n"
        "🔹 /approche_ck - Voir l'approche C-K\n"
        "🔹 /organisation_innovation - Voir l'organisation de l'innovation\n"
        "🔹 /conception_innovante - Voir la conception innovante\n"
        "🔹 /innovation_sobriete - Voir l'innovation de sobriété\n"
        "🔹 /valeur_et_innovation - Voir la valeur et innovation\n"
        "🔹 /conclusion - Voir la conclusion\n\n"
        "📚 **Ressources** :\n"
        "📖 /bibliographie - Voir la bibliographie\n"
        "🌐 /sitographie - Voir la sitographie\n\n"
        "📹 **Vidéos & Images** :\n"
        "🎬 /videointro - Voir l'introduction en vidéo\n"
        "🎥 /video - Voir une vidéo sur un projet soutenu par TftP\n"
        "🖼️ /approche_ck - Voir l'image Approche C-K\n\n"
        "🖼️ /annexe1 - Voir l'Annexe 1\n\n"
        "ℹ️ **Informations supplémentaires** :\n"
        "💡 /aide - Afficher ce récapitulatif des commandes\n"
    )

    update.message.reply_text(menu_text)

# ✅ Commande /aide : Afficher la liste des commandes disponibles
def afficher_aide(update, context):
    menu_text = (
        "📌 **Commandes disponibles :**\n\n"
        "📖 **Sections du dossier** :\n"
        "🔹 /introduction - Voir l'introduction\n"
        "🔹 /approche_ck - Voir l'approche C-K\n"
        "🔹 /organisation_innovation - Voir l'organisation de l'innovation\n"
        "🔹 /conception_innovante - Voir la conception innovante\n"
        "🔹 /innovation_sobriete - Voir l'innovation de sobriété\n"
        "🔹 /valeur_et_innovation - Voir la valeur et innovation\n"
        "🔹 /conclusion - Voir la conclusion\n\n"

        "📚 **Ressources** :\n"
        "📖 /bibliographie - Voir la bibliographie\n"
        "🌐 /sitographie - Voir la sitographie\n\n"

        "📹 **Vidéos & Images** :\n"
        "🎬 /videointro - Voir l'introduction en vidéo\n"
        "🎥 /video - Voir une vidéo sur un projet soutenu par TftP\n"
        "🖼️ /approche_ck - Voir l'image Approche C-K\n"
        "🖼️ /annexe1 - Voir l'Annexe 1\n\n"

        "ℹ️ **Informations supplémentaires** :\n"
        "💡 /aide - Afficher ce récapitulatif des commandes\n"
    )

    update.message.reply_text(menu_text)




# Commande pour afficher une section
def afficher_section(update, context):
    raw_command = update.message.text[1:]  
    data = load_json(f"{raw_command}.json")
    chat_id = update.message.chat_id

    if data:
        # ✅ Envoi de la vidéo pour l'introduction
        if raw_command == "introduction":
            try:
                context.bot.send_video(chat_id=chat_id, video=open("VideoIntro.mp4", "rb"))
                time.sleep(1)
            except Exception:
                update.message.reply_text("⚠️ Impossible d'envoyer la vidéo.")

        # ✅ Envoi de l'image pour Approche C-K
        elif raw_command == "approche_ck":
            try:
                context.bot.send_photo(chat_id=chat_id, photo=open("ApprocheCK.png", "rb"))
                time.sleep(1)
            except Exception:
                update.message.reply_text("⚠️ Impossible d'envoyer l'image.")

        texte_complet = f"📌 **{raw_command.replace('_', ' ').capitalize()}** :\n\n"

        if isinstance(data, dict):
            for key, value in data.items():
                texte_complet += f"🔹 {value}\n\n"

        envoyer_texte_long(update, texte_complet)
    else:
        update.message.reply_text(f"⚠️ Fichier introuvable pour la section : {raw_command}")

# ✅ Commande /video : envoie le lien YouTube
def envoyer_video(update, context):
    update.message.reply_text("🎥 Voici une vidéo sur Midipile Mobility :")
    update.message.reply_text("https://www.youtube.com/watch?v=6pvfuFFDLzc")

# ✅ Commande /videointro : envoie la vidéo locale
def envoyer_videointro(update, context):
    chat_id = update.message.chat_id
    try:
        context.bot.send_video(chat_id=chat_id, video=open("VideoIntro.mp4", "rb"))
        update.message.reply_text("🎬 Voici l'introduction en vidéo.")
    except Exception:
        update.message.reply_text("⚠️ Impossible d'envoyer la vidéo.")

# ✅ Commande / envoie bibliographie
def afficher_bibliographie(update: Update, context: CallbackContext):
    fichier = "bibliographie.json"
    try:
        with open(fichier, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "bibliographie" not in data:
            update.message.reply_text("⚠️ Aucun contenu trouvé pour la bibliographie.")
            return

        biblio_text = "📚 **Bibliographie** :\n\n"

        for entry in data["bibliographie"]:
            titre = entry.get("titre", "Titre inconnu")
            auteurs = entry.get("auteur", "Auteur inconnu")
            date = entry.get("date", "Date inconnue")
            editeur = entry.get("éditeur", "")
            source = entry.get("source", "")
            lien = entry.get("lien", "")

            # Formatage propre
            ref = f"🔹 **{titre}** ({date})"
            if auteurs:
                ref += f", {auteurs}"
            if editeur:
                ref += f", {editeur}"
            if source:
                ref += f". {source}"
            if lien:
                ref += f"\n  🔗 [Disponible ici]({lien})"

            ref += "\n\n"
            biblio_text += ref

        # Envoi en plusieurs morceaux si le texte est trop long
        envoyer_texte_long(update, biblio_text)

    except Exception as e:
        update.message.reply_text(f"⚠️ Erreur de lecture du fichier JSON : {fichier}")
        print("Erreur Bibliographie:", e)



#Commande sitographie

def afficher_sitographie(update: Update, context: CallbackContext):
    fichier = "sitographie.json"
    try:
        with open(fichier, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "sitographie" not in data:
            update.message.reply_text("⚠️ Aucun contenu trouvé pour la sitographie.")
            return

        sitographie_text = "🌍 **Sitographie** :\n\n"

        for entry in data["sitographie"]:
            auteur = entry.get("auteur", "Auteur inconnu")
            titre = entry.get("titre", "Titre inconnu")
            date = entry.get("date", "Date inconnue")
            consultation = entry.get("consultation", "Date inconnue")
            lien = entry.get("lien", "")

            ref = f"🔹 *{auteur}* ({date}). **{titre}**.\n  [Consulté le {consultation}]."
            if lien:
                ref += f"\n  🔗 [Disponible ici]({lien})"

            ref += "\n\n"
            sitographie_text += ref

        envoyer_texte_long(update, sitographie_text)

    except Exception as e:
        update.message.reply_text(f"⚠️ Erreur de lecture du fichier JSON : {fichier}")
        print("Erreur Sitographie:", e)
        
# Cmmande annexe1
def afficher_annexe1(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    try:
        context.bot.send_photo(chat_id=chat_id, photo=open("Annexe1.png", "rb"))
        update.message.reply_text("📄 **Voici l'Annexe 1.**")
    except Exception:
        update.message.reply_text("⚠️ Impossible d'envoyer l'image 'Annexe1.png'. Vérifiez qu'elle est bien dans le dossier.")



# Fonction pour exécuter le bot
def run_bot():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("aide", afficher_aide))
    dp.add_handler(CommandHandler("video", envoyer_video))
    dp.add_handler(CommandHandler("videointro", envoyer_videointro))
    dp.add_handler(CommandHandler("bibliographie", afficher_bibliographie))  # ✅ Correction ajout
    dp.add_handler(CommandHandler("sitographie", afficher_sitographie))  # ✅ Correction ajout
    dp.add_handler(CommandHandler("annexe1", afficher_annexe1))  # ✅ Ajout de la commande



    for section in ["introduction", "approche_ck", "organisation_innovation",
                    "conception_innovante", "innovation_sobriete", "valeur_et_innovation",
                    "conclusion"]:
        command = clean_command_name(section)
        dp.add_handler(CommandHandler(command, afficher_section))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    Process(target=app.run, kwargs={"host": "0.0.0.0", "port": 8080}).start()
    run_bot()
