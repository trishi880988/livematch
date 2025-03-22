import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc

# Bot Token
TOKEN = '7754892338:AAHkHR-su65KeFkyU7vsu1kkkO38f4IkQio'

# User list to store chat IDs
subscribed_users = []

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to scrape live data
def get_live_score():
    url = "https://www.cricbuzz.com/live-cricket-scores/114960/kkr-vs-rcb-1st-match-indian-premier-league-2025"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    try:
        score = soup.find('div', class_='cb-min-bat-rw').get_text(strip=True)
        batsmen = soup.find_all('div', class_='cb-col cb-col-100 cb-min-itm-rw')
        batsman_info = '\n'.join([b.get_text(strip=True) for b in batsmen])

        commentary = soup.find('div', class_='cb-col cb-col-100 cb-ltst-wgt-hdr').find('div', class_='cb-col cb-col-100 cb-min-txt').get_text(strip=True)

        return f'🏏 *Live Score:*
{score}

👥 *Batsmen Info:*
{batsman_info}

📝 *Commentary:*
{commentary}'
    except Exception as e:
        logger.error(f"Error fetching live score: {e}")
        return None

# Function to send updates to all users
async def live_updates():
    message = get_live_score()
    if message:
        for chat_id in subscribed_users:
            try:
                await bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
            except Exception as e:
                logger.error(f"Error sending message to {chat_id}: {e}")

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in subscribed_users:
        subscribed_users.append(chat_id)
        await update.message.reply_text("✅ You are subscribed for IPL live updates!")
    else:
        await update.message.reply_text("ℹ️ You are already subscribed!")

# Initialize bot and scheduler
bot = Bot(TOKEN)
app = ApplicationBuilder().token(TOKEN).build()
scheduler = AsyncIOScheduler(timezone=utc)
scheduler.add_job(live_updates, 'interval', seconds=30)
scheduler.start()

# Handlers
app.add_handler(CommandHandler("start", start))

# Run the bot
app.run_polling()
