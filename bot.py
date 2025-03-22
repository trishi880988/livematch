import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz

# Telegram Bot Token
TOKEN = "7754892338:AAHkHR-su65KeFkyU7vsu1kkkO38f4IkQio"

# Logging setup
logging.basicConfig(level=logging.INFO)

# Users list to store chat IDs
users = []

# Scrape function
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
    except Exception as e:
        logging.error(f"Error fetching live score: {e}")
        return None

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in users:
        users.append(chat_id)
    await update.message.reply_text("✅ You will now receive live IPL updates!")

# Job to send live updates
async def live_updates():
    message = scrape_live_score()
    if message:
        for user_id in users:
            await app.bot.send_message(chat_id=user_id, text=message, parse_mode="Markdown")

# Main Application
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

# Scheduler Setup with pytz timezone
scheduler = AsyncIOScheduler(timezone=pytz.utc)
scheduler.add_job(live_updates, 'interval', seconds=30)
scheduler.start()

app.run_polling()
