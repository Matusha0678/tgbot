import time
import os
import logging
import requests
import json
from datetime import datetime, timedelta

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

# Bot token from environment variable
BOT_TOKEN = os.getenv('BOT_TOKEN', '8169528152:AAHNdw-NZADGn-C8I_HzRFKAROu0xle_oi0')

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}/"
        self.offset = 0

    def send_message(self, chat_id, text, parse_mode=None):
        """Send a message to a chat."""
        url = f"{self.base_url}sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text
        }
        if parse_mode:
            data['parse_mode'] = parse_mode
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")
            return None

    def get_updates(self):
        """Get updates from Telegram."""
        url = f"{self.base_url}getUpdates"
        params = {'offset': self.offset + 1, 'timeout': 30}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['ok'] and data['result']:
                self.offset = data['result'][-1]['update_id']
                return data['result']
            return []
        except Exception as e:
            logger.error(f"Error getting updates: {e}")
            return []

    def handle_message(self, update):
        """Handle incoming messages."""
        if 'message' not in update:
            return
        
        message = update['message']
        chat_id = message['chat']['id']
        text = message.get('text', '')
        
        if text.startswith('/'):
            command = text[1:].lower()
            
            if command == 'start':
                self.send_message(chat_id, 
                    "Привет! Я бот для уведомлений о праздниках.\n\n"
                    "Я буду предупреждать вас о праздниках за один день до них.\n"
                    "Используйте /addme чтобы добавить себя в список уведомлений.")
            
            elif command == 'addme':
                if chat_id not in USER_CHAT_IDS:
                    USER_CHAT_IDS.append(chat_id)
                    self.send_message(chat_id, "Вы добавлены в список уведомлений о праздниках!")
                else:
                    self.send_message(chat_id, "Вы уже в списке уведомлений.")
            
            elif command == 'removeme':
                if chat_id in USER_CHAT_IDS:
                    USER_CHAT_IDS.remove(chat_id)
                    self.send_message(chat_id, "Вы удалены из списка уведомлений о праздниках.")
                else:
                    self.send_message(chat_id, "Вас нет в списке уведомлений.")
            
            elif command == 'holidays':
                holiday_list = "📅 Список всех праздников:\n\n"
                for date_str, name in sorted(HOLIDAYS.items()):
                    month, day = date_str.split('-')
                    holiday_list += f"📆 {day}.{month}: {name}\n"
                self.send_message(chat_id, holiday_list)

def check_holidays(bot):
    """Check for holidays tomorrow and send notifications."""
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_key = f"{tomorrow.month:02d}-{tomorrow.day:02d}"
    
    if tomorrow_key in HOLIDAYS:
        holiday_name = HOLIDAYS[tomorrow_key]
        message = f"🎉 *Завтра праздник!*\n\n📅 {tomorrow.day:02d}.{tomorrow.month:02d}: {holiday_name}"
        
        for chat_id in USER_CHAT_IDS:
            bot.send_message(chat_id, message, parse_mode='Markdown')
            logger.info(f"Sent holiday notification to {chat_id}")

def daily_checker(bot):
    """Daily task to check for upcoming holidays."""
    while True:
        try:
            check_holidays(bot)
            # Check once every 24 hours
            time.sleep(86400)  # 24 hours in seconds
        except Exception as e:
            logger.error(f"Error in daily checker: {e}")
            time.sleep(3600)  # Wait 1 hour before retrying

def main():
    """Start the bot."""
    bot = TelegramBot(BOT_TOKEN)
    
    print("Starting holiday notification bot...")
    
    # Main loop to handle messages
    while True:
        try:
            # Check for holidays before processing messages
            check_holidays(bot)
            
            updates = bot.get_updates()
            for update in updates:
                bot.handle_message(update)
            
            # Check once per hour for holidays
            time.sleep(3600)
        except KeyboardInterrupt:
            print("Bot stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(5)

if __name__ == '__main__':
    main()
