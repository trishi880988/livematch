from telegram.ext import Updater, CommandHandler
import logging
import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

TOKEN = "7754892338:AAHkHR-su65KeFkyU7vsu1kkkO38f4IkQio"
users = []

def start(update, context):
    chat_id = update.effective_chat.id
    if chat_id not in users:
        users.append(chat_id)
    update.message.reply_text("✅ You will now receive live IPL updates!")

def scrape_live_score():
    url = 'https://www.cricbuzz.com/live-cricket-scores/114960/kkr-vs-rcb-1st-match-indian-premier-league-2025'
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.content, 'html.parser')
    try:
        title = soup.find('h1', class_='cb-nav-hdr cb-font-16 line-ht24').get_text(strip=True)
        status = soup.find('div', class_='cb-text-inprogress').get_text(strip=True)
        score = soup.find('div', class_='cb-col cb-col-67 cb-scrs-wrp').get_text(strip=True)
        batsman = soup.find_all('div', class_='cb-col cb-col-100 cb-scrd-itms')[0].get_text(strip=True)
        bowler = soup.find_all('div', class_='cb-col cb-col-100 cb-scrd-itms')[2].get_text(strip=True)
        return f'''🏏 *Live Score Update!*
*Match:* {title}
*Status:* {status}
*Score:* {score}
*Batsman:* {batsman}
*Bowler:* {bowler}'''
    except:
        return None

def send_updates(context):
    message = scrape_live_score()
    if message:
        for user in users:
            context.bot.send_message(chat_id=user, text=message, parse_mode="Markdown")

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))

scheduler = BackgroundScheduler(timezone=pytz.utc)
scheduler.add_job(send_updates, 'interval', seconds=30, args=[updater.bot])
scheduler.start()

updater.start_polling()
updater.idle()
