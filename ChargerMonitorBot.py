import asyncio
import requests
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = "8273880304:AAGeX9L0bLef17Lav5ZGxqPGSZ-BKa68TYU"

CHARGING_STATIONS = {
    "station 1": "THE_URL_THAT_RETURNS_JSON_DATA_FOR_STATION_1",
    "station 2": "THE_URL_THAT_RETURNS_JSON_DATA_FOR_STATION_2"
}

CHECK_INTERVAL_SECONDS = 300
SUBSCRIBERS_FILE = "subscribers.txt"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

subscribers = set()
last_known_slots = {}

def load_subscribers():
    """Loads subscriber IDs from a file into memory."""
    global subscribers
    try:
        if os.path.exists(SUBSCRIBERS_FILE):
            with open(SUBSCRIBERS_FILE, "r") as f:
                subscribers = {int(line.strip()) for line in f if line.strip()}
            logger.info(f"Loaded {len(subscribers)} subscribers.")            
    except Exception as e:
        logger.error(f"Error loading subscribers: {e}")

def save_subscribers():
    """Saves subscriber IDs from memory to a file."""
    with open(SUBSCRIBERS_FILE, "w") as f:
        for user_id in subscribers:
            f.write(str(user_id) + "\n")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /start command. Adds the user to subscribers."""
    chat_id = update.message.chat_id
    if chat_id not in subscribers:
        subscribers.add(chat_id)
        save_subscribers()
        await update.message.reply_text(
            "Hello! 👋 You have subscribed to notifications about available charging stations.\n"
            "To unsubscribe, use the /stop command.\n"
            "To check the status now, use /status."
        )
        logger.info(f"New subscriber: {chat_id}")
    else:
        await update.message.reply_text("You are already subscribed! To check the status, use /status.")
    # Send the current status immediately after subscribing
    await status(update, context)

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /stop command. Removes the user from subscribers."""
    chat_id = update.message.chat_id
    if chat_id in subscribers:
        subscribers.remove(chat_id)
        save_subscribers()
        await update.message.reply_text("You have successfully unsubscribed from notifications. Goodbye!")
        logger.info(f"User unsubscribed: {chat_id}")
    else:
        await update.message.reply_text("You were not subscribed.")

def get_station_status(name, url):
    """Gets the status of a single station. Returns a formatted string."""
    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            return f"🔌 {name}: Error (status {response.status_code})"

        data = response.json()
        items = data.get("response", {}).get("content", {}).get("items", [])
        if not items: return f"🔌 {name}: Invalid API response"

        connectors = items[0].get("pool", {}).get("charging_connectors", [])
        if not connectors: return f"🔌 {name}: No connector data available"

        info = connectors[0]
        available = info.get("available_count", 0)
        total = info.get("count", 0)
        
        icon = "✅" if available > 0 else "❌"
        return f"{icon} {name}: available {available} of {total}"

    except requests.RequestException:
        return f"🔌 {name}: Network error"
    except Exception:
        return f"🔌 {name}: Unknown error"

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends the current status of all stations upon request."""
    await update.message.reply_text("Checking station status, please wait...")
    status_messages = [get_station_status(name, url) for name, url in CHARGING_STATIONS.items()]
    await update.message.reply_text("\n".join(status_messages))

async def check_stations_job(context: ContextTypes.DEFAULT_TYPE):
    """Periodic task that checks stations and sends notifications."""
    logger.info("Running scheduled station check...")
    for name, url in CHARGING_STATIONS.items():
        try:
            response = requests.get(url, timeout=15)
            if response.status_code != 200: continue
            
            data = response.json()
            items = data.get("response", {}).get("content", {}).get("items", [])
            if not items: continue
            
            connectors = items[0].get("pool", {}).get("charging_connectors", [])
            if not connectors: continue
            
            info = connectors[0]
            available_count = info.get("available_count", 0)
            total_count = info.get("count", 0)

            previous_slots = last_known_slots.get(name, 0)

            if available_count > 0 and previous_slots == 0:
                message = f"✅ Charger '{name}' is now available!\nAvailable: {available_count} of {total_count}"
                logger.info(f"Change detected for '{name}', sending notifications...")
                for user_id in subscribers:
                    try:
                        await context.bot.send_message(chat_id=user_id, text=message)
                    except Exception as e:
                        logger.error(f"Failed to send message to {user_id}: {e}")
            
            last_known_slots[name] = available_count
        except Exception as e:
            logger.error(f"Error checking station '{name}': {e}")


def main():
    """Main function to start the bot."""
    load_subscribers()

    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("status", status))

    job_queue = application.job_queue
    job_queue.run_repeating(check_stations_job, interval=CHECK_INTERVAL_SECONDS, first=10)

    logger.info("Bot started and ready to work!")
    application.run_polling()

if __name__ == "__main__":
    main()