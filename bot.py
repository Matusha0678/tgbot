import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List

from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Holiday data extracted from the calendar
HOLIDAYS = {
    # Format: "MM-DD": "Holiday Name"
    "11-04": "ИЛ ПОЯ (ILL FULL MOON POYA DAY)",
    "12-03": "УНДУВАП ПОЯ (UNDUVAP FULL MOON POYA DAY)",
    "12-24": "РОЖДЕСТВО ХРИСТОВО",
    "01-01": "ДУРУТУ ПОЯ (DURUTHU POYA)",
    "01-13": "ТАЙ ПОНГАЛ (TAMIL THAI PONGAL) - ПРАЗДНИК УРОЖАЯ",
    "01-31": "НАВАМ ПОЯ (NAVAM POYA)",
    "02-03": "ДЕНЬ НЕЗАВИСИМОСТИ",
    "02-14": "МАХА ШИВАРАТИ (ВЕЛИКАЯ НОЧЬ ШИВЫ)",
    "03-02": "МЕДИН ПОЯ",
    "03-20": "РАМАДАН (ИД-УЛ-ФИТР)",
    "03-31": "БАК ПОЯ (BAK FULL MOON POYA DAY)",
    "04-30": "ВЕСАК ПОЯ (VESAK FULL MOON POYA DAY)",
    "05-01": "ВЕСАК ПОЯ (VESAK FULL MOON POYA DAY) - День 2",
    "05-29": "АДХИ ПОСОН ПОЯ (ADHI POSON FULL MOON POYA DAY)",
    "06-28": "ПОСОН ПОЯ (POSON FULL MOON POYA DAY)",
    "07-28": "ЭСАЛА ПОЯ (ESALA FULL MOON POYA DAY)",
    "08-26": "НИКИНИ ПОЯ (NIKINI FULL MOON POYA DAY)",
    "09-25": "БИНАРА ПОЯ (BINARA FULL MOON POYA DAY)",
}

# User chat IDs that will receive notifications (you'll need to add your chat ID)
USER_CHAT_IDS = []  # Add your chat ID(s) here

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        f"Привет {user.mention_html()}! Я бот для уведомлений о праздниках.\n\n"
        "Я буду предупреждать вас о праздниках за один день до них.\n"
        "Используйте /addme чтобы добавить себя в список уведомлений."
    )

async def add_me(update: Update, context: CallbackContext) -> None:
    """Add user to notification list."""
    chat_id = update.effective_chat.id
    if chat_id not in USER_CHAT_IDS:
        USER_CHAT_IDS.append(chat_id)
        await update.message.reply_text("Вы добавлены в список уведомлений о праздниках!")
    else:
        await update.message.reply_text("Вы уже в списке уведомлений.")

async def remove_me(update: Update, context: CallbackContext) -> None:
    """Remove user from notification list."""
    chat_id = update.effective_chat.id
    if chat_id in USER_CHAT_IDS:
        USER_CHAT_IDS.remove(chat_id)
        await update.message.reply_text("Вы удалены из списка уведомлений о праздниках.")
    else:
        await update.message.reply_text("Вас нет в списке уведомлений.")

async def list_holidays(update: Update, context: CallbackContext) -> None:
    """List all holidays."""
    holiday_list = "📅 Список всех праздников:\n\n"
    for date_str, name in sorted(HOLIDAYS.items()):
        month, day = date_str.split('-')
        holiday_list += f"📆 {day}.{month}: {name}\n"
    
    await update.message.reply_text(holiday_list)

async def check_holidays(bot: Bot) -> None:
    """Check for holidays tomorrow and send notifications."""
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_key = f"{tomorrow.month:02d}-{tomorrow.day:02d}"
    
    if tomorrow_key in HOLIDAYS:
        holiday_name = HOLIDAYS[tomorrow_key]
        message = f"🎉 **Завтра праздник!**\n\n📅 {tomorrow.day:02d}.{tomorrow.month:02d}: {holiday_name}"
        
        for chat_id in USER_CHAT_IDS:
            try:
                await bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
                logger.info(f"Sent holiday notification to {chat_id}")
            except Exception as e:
                logger.error(f"Failed to send message to {chat_id}: {e}")

async def daily_checker(updater: Updater) -> None:
    """Daily task to check for upcoming holidays."""
    while True:
        try:
            await check_holidays(updater.bot)
            # Check once every 24 hours
            await asyncio.sleep(86400)  # 24 hours in seconds
        except Exception as e:
            logger.error(f"Error in daily checker: {e}")
            await asyncio.sleep(3600)  # Wait 1 hour before retrying

async def post_init(updater: Updater) -> None:
    """Initialize daily checker after bot starts."""
    asyncio.create_task(daily_checker(updater))

def main() -> None:
    """Start the bot."""
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token
    bot_token = "8169528152:AAHNdw-NZADGn-C8I_HzRFKAROu0xle_oi0"
    
    if bot_token == "YOUR_BOT_TOKEN":
        print("Please replace 'YOUR_BOT_TOKEN' with your actual bot token!")
        return
    
    updater = Updater(token=bot_token, use_context=True)

    # Add command handlers
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("addme", add_me))
    updater.dispatcher.add_handler(CommandHandler("removeme", remove_me))
    updater.dispatcher.add_handler(CommandHandler("holidays", list_holidays))

    # Start the daily checker
    asyncio.create_task(post_init(updater))

    # Start the bot
    print("Starting holiday notification bot...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
