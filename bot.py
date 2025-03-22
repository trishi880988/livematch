import requests
from bs4 import BeautifulSoup
from telegram.ext import Updater, CommandHandler
import logging
import time

# लॉगिंग सेटअप
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# आपका टेलीग्राम बॉट टोकन
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# उपयोगकर्ताओं की सूची जो अपडेट प्राप्त करेंगे
users = set()
last_update = None

# लाइव स्कोर प्राप्त करने का फंक्शन
def get_live_score():
    url = "https://www.cricbuzz.com/live-cricket-scores/114960/kkr-vs-rcb-1st-match-indian-premier-league-2025"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    try:
        # मैच शीर्षक
        match_title = soup.find("h1", class_="cb-nav-hdr cb-font-18 line-ht24").get_text(strip=True)

        # ओवर और स्कोर
        score_section = soup.find("div", class_="cb-min-bat-rw")
        over = score_section.find("span", class_="text-gray").get_text(strip=True)
        score = score_section.find("span", class_="cb-font-20 text-bold").get_text(strip=True)

        # बल्लेबाज और गेंदबाज की जानकारी
        batsmen = soup.find_all("div", class_="cb-min-itm-rw")
        batsman_info = []
        for batsman in batsmen:
            name = batsman.find("a").get_text(strip=True)
            runs = batsman.find_all("div")[2].get_text(strip=True)
            balls = batsman.find_all("div")[3].get_text(strip=True)
            batsman_info.append(f"{name} {runs}({balls})")

        bowler_section = soup.find("div", class_="cb-min-itm-rw", id="bowler")
        bowler_name = bowler_section.find("a").get_text(strip=True)
        bowler_overs = bowler_section.find_all("div")[1].get_text(strip=True)
        bowler_runs = bowler_section.find_all("div")[2].get_text(strip=True)
        bowler_wickets = bowler_section.find_all("div")[3].get_text(strip=True)

        # अंतिम गेंद की जानकारी
        commentary_section = soup.find("div", class_="cb-col cb-col-100 cb-ltst-wgt-hdr")
        last_ball = commentary_section.find("div", class_="cb-col cb-col-100 cb-min-itm-rw").get_text(strip=True)

        # संदेश का प्रारूपण
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

# /start कमांड हैंडलर
def start(update, context):
    chat_id = update.message.chat_id
    users.add(chat_id)
    context.bot.send_message(chat_id=chat_id, text="✅ लाइव IPL अपडेट्स शुरू हो गए हैं! बंद करने के लिए /stop टाइप करें।")

# /stop कमांड हैंडलर
def stop(update, context):
    chat_id = update.message.chat_id
    if chat_id in users:
        users.remove(chat_id)
        context.bot.send_message(chat_id=chat_id, text="🛑 लाइव अपडेट्स बंद कर दिए गए हैं।")
    else:
        context.bot.send_message(chat_id=chat_id, text="❌ आपने अभी तक अपडेट्स शुरू नहीं किए हैं।")

# लाइव अपडेट्स भेजने का फंक्शन
def live_updates(context):
    global last_update
    message = get_live_score()
    if message and message != last_update:
        last_update = message
        for user in users:
            context.bot.send_message(chat_id=user, text=message, parse_mode='Markdown')

# मुख्य फंक्शन
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))

    job_queue = updater.job_queue
    job_queue.run_repeating(live_updates, interval=30, first=0)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
