import requests
from bs4 import BeautifulSoup
from telegram import Bot, Update
from telegram.ext import CommandHandler, Updater, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
import logging

logging.basicConfig(level=logging.INFO)

TOKEN = '7754892338:AAHkHR-su65KeFkyU7vsu1kkkO38f4IkQio'
URL = 'https://www.cricbuzz.com/live-cricket-scores/114960/kkr-vs-rcb-1st-match-indian-premier-league-2025'

bot = Bot(token=TOKEN)
scheduler = BackgroundScheduler()
subscribed_users = set()

def fetch_live_score():
    try:
        response = requests.get(URL, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')

        # Live score summary
        score_section = soup.find('div', class_='cb-min-inf cb-col-100 cb-col cb-com-ln')
        live_score = score_section.get_text(strip=True) if score_section else 'Live score not found'

        # Current batsman & bowler info
        batsmen = soup.find_all('div', class_='cb-col cb-col-100 cb-scrd-itms')
        batsman_info = ''
        for batsman in batsmen[:2]:
            batsman_info += batsman.get_text(strip=True) + '\n'

        # Latest ball commentary
        commentary_section = soup.find('div', class_='cb-col cb-col-100 cb-com-ln')
        commentary = commentary_section.get_text(strip=True) if commentary_section else 'Commentary not found'

        message = f'🏏 *Live IPL Score Update* 🏏\n\n*{live_score}*\n\n{batsman_info}\n🎙️ {commentary}'

        for user_id in subscribed_users:
            bot.send_message(chat_id=user_id, text=message, parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Error fetching live score: {e}")

def start(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    subscribed_users.add(user_id)
    update.message.reply_text('You are now subscribed to Live IPL updates! ✅')

updater = Updater(token=TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler('start', start))

scheduler.add_job(fetch_live_score, 'interval', seconds=30, id='live_updates')
scheduler.start()

updater.start_polling()
updater.idle()
