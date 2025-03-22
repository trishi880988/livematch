import requests
from bs4 import BeautifulSoup
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
import logging
import time

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Your Telegram bot token
TOKEN = "7754892338:AAHkHR-su65KeFkyU7vsu1kkkO38f4IkQio"

# Users set
users = set()
last_update = None

# Function to fetch live score
def get_live_score():
    url = "https://www.cricbuzz.com/live-cricket-scores/114960/kkr-vs-rcb-1st-match-indian-premier-league-2025"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    try:
        # Match title
        match_title = soup.find("h1", class_="cb-nav-hdr cb-font-18 line-ht24").get_text(strip=True)

        # Score and over
        score_section = soup.find("div", class_="cb-col cb-col-100 cb-min-txt")
        over = score_section.find("span", class_="cb-col cb-col-8 text-bold text-black text-right").get_text(strip=True)
        score = score_section.find("span", class_="cb-col cb-col-8 text-bold text-black").get_text(strip=True)

        # Batsmen info
        batsmen = soup.find_all("div", class_="cb-col cb-col-50")
        batsman_info = []
        for batsman in batsmen[:2]:
            name = batsman.find("div", class_="cb-col cb-col-33").get_text(strip=True)
            stats = batsman.find_all("div", class_="cb-col cb-col-33 text-right")
            runs = stats[0].get_text(strip=True)
            balls = stats[1].get_text(strip=True)
            batsman_info.append(f"{name} {runs}({balls})")

        # Bowler info (placeholder if not found)
        bowler_section = soup.find("div", class_="cb-col cb-col-100 cb-min-bowl")
        if bowler_section:
            bowler_name = bowler_section.find("a").get_text(strip=True)
            bowler_stats = bowler_section.find_all("div", class_="cb-col cb-col-33 text-right")
            bowler_overs = bowler_stats[0].get_text(strip=True)
            bowler_runs = bowler_stats[1].get_text(strip=True)
            bowler_wickets = bowler_stats[2].get_text(strip=True)
        else:
            bowler_name = "N/A"
            bowler_overs = "0"
            bowler_runs = "0"
            bowler_wickets = "0"

        # Last ball commentary
        commentary_section = soup.find("div", class_="cb-col cb-col-100 cb-com-ln")
        last_ball = commentary_section.find("div", class_="cb-col cb-col-100 cb-com-ln-text").get_text(strip=True)

        message = (
            f"🏏 *{match_title}*\n\n"
            f"🕒 *{over}*\n"
            f"⚡️ {last_ball}\n\n"
            f"*बल्लेबाज:*\n"
            f"{batsman_info[0]}\n"
            f"{batsman_info[1]}\n\n"
            f"*गेंदबाज:*\n"
            f"{bowler_name} - {bowler_wickets}/{bowler_runs} ({bowler_overs} ओवर)\n\n"
            f"*स्कोर:*\n"
            f"{score}"
        )

        return message

    except Exception as e:
        logging.error(f"Error fetching live score: {e}")
        return None

# /start handler
def start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    users.add(chat_id)
    context.bot.send_message(chat_id=chat_id, text="✅ लाइव IPL अपडेट्स शुरू! /stop भेजकर बंद करें।")

# /stop handler
def stop(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    users.discard(chat_id)
    context.bot.send_message(chat_id=chat_id, text="🛑 लाइव अपडेट्स बंद कर दिए गए हैं।")

# Send updates
def live_updates(context: CallbackContext):
    global last_update
    message = get_live_score()
    if message and message != last_update:
        last_update = message
        for user in users:
            context.bot.send_message(chat_id=user, text=message, parse_mode='Markdown')

# Main function
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))

    updater.job_queue.run_repeating(live_updates, interval=30, first=0)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
