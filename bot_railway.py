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
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")
            return None

    def get_updates(self):
        """Get updates from Telegram."""
        url = f"{self.base_url}getUpdates"
        params = {'offset': self.offset + 1, 'timeout': 10}
        
        try:
            response = requests.get(url, params=params, timeout=15)
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
                welcome_msg = """ⲇⲟⲃⲣⲟ ⲡⲟⲇⲁⲗⲁⲩⲓⲧⲉ ⲃ Holiday Bot!

Ⲱ ⲃⲁⲛ ⲡⲉⲣⲥⲟⲛⲁⲗⲅⲛⲩⲓ ⲡⲟⲙⲟⲱⲛⲓⲕ ⲇⲗⲟ ⲟⲧⲥⳑⲉⳑⲉⲅⲓⲃⲁⲛⲓⲟ ⲡⲣⲁⲍⲇⲛⲓⲕⲟⲃ!

Ⲥⲧⲟ ⲙⲟⲅⲩ ⲩⲙⲉⲭ:
• Ⲡⲣⲉⲇⲩⲡⲣⲉⳑⲁⲇⲁⲩ ⲟ ⲡⲣⲁⲇⲇⲛⲓⲕⲁⲭ ⲇⲁ ⲇⲉⲛⲅ ⲇⲟ ⲛⲓⲭ
• Ⲡⲟⲕⲁⲍⲩⲃⲁⲩ ⲥⲡⲓⲥⲟⲕ ⲃⲥⲉⲭ ⲡⲣⲁⲇⲇⲛⲓⲕⲟⲃ
• Ⲙⲁⲥⲕⲁⲇⲁⲩ ⲟ ⲡⲣⲁⲇⲇⲛⲓⲕⲁⲭ ⲃ ⲧⲉⲕⲩⲱⲉⲓ ⲍⲉⲥⲱⲉ
• Ⲟⲧⲙⲱⲁⲩ ⲃⲗⲓⳑⲁⲓⲥⲓⲓ ⲡⲣⲁⲇⲇⲛⲓⲕ

Ⲕⲟⲙⲁⲛⲇⲩ:
/start - Ⲡⲟⲕⲁⲍⲁⲧⲇ ⲟⲧⲟ ⲥⲟⲟⲱⲱⲉⲛⲓⲉ
/addme - Ⲡⲟⲇⲡⲓⲥⲁⲧⲁⲥⲟ ⲛⲁ ⲩⲃⲉⲇⲟⲙⲗⲉⲛⲓⲟ
/removeme - Ⲟⲧⲡⲓⲥⲁⲧⲁⲥⲟ ⲟⲧ ⲩⲃⲉⲇⲟⲙⲗⲉⲛⲓⲓ
/holidays - Ⲃⲥⲉ ⲡⲣⲁⲇⲇⲛⲓⲕⲓ
/month - Ⲡⲣⲁⲇⲇⲛⲓⲕⲓ ⲟⲧⲟⳘⲟ ⲍⲉⲥⲱⲉ
/next - Ⲃⲗⲓⳑⲁⲓⲱⲓⲓ ⲡⲣⲁⲇⲇⲛⲓⲕ
/today - Ⲡⲣⲁⲇⲇⲛⲓⲕⲓ ⲥⲉⳑⲟⲇⲛⲟ
/help - Ⲡⲟⲙⲟⲱⲧⲅ

Ⲛⲁⲭⲛⲓⲧⲉ ⲥ ⲕⲟⲙⲁⲛⲇⲩ /addme ⲭⲧⲟⲃⲩ ⲡⲟⲗⲩⲭⲁⲧⲇ ⲩⲃⲉⲇⲟⲙⲗⲉⲛⲓⲟ!"""
                self.send_message(chat_id, welcome_msg)
            
            elif command == 'help':
                help_msg = """Ⲥⲡⲣⲁⲃⲕⲁ ⲡⲟ ⲕⲟⲙⲁⲛⲇⲁⲙ:

/start - Ⲡⲣⲓⲃⲉⲧⲥⲧⲃⲓⲉ ⲉ ⲓⲛⲇⲟⲣⲙⲁⲕⲓⲟ ⲟ ⲃⲟⲧⲉ
/addme - Ⲡⲟⲇⲡⲓⲥⲁⲧⲁⲥⲟ ⲛⲁ ⲩⲃⲉⲇⲟⲙⲗⲉⲛⲓⲟ ⲟ ⲡⲣⲁⲇⲇⲛⲓⲕⲁⲭ
/removeme - Ⲟⲧⲡⲓⲥⲁⲧⲁⲥⲟ ⲟⲧ ⲩⲃⲉⲇⲟⲙⲗⲉⲛⲓⲓ
/holidays - Ⲡⲟⲕⲁⲍⲁⲧⲇ ⲡⲟⲗⲛⲩⲓ ⲥⲡⲓⲥⲟⲕ ⲃⲥⲉⲭ ⲡⲣⲁⲇⲇⲛⲓⲕⲟⲃ
/month - Ⲡⲣⲁⲇⲇⲛⲓⲕⲓ ⲃ ⲧⲉⲕⲩⲱⲉⲓ ⲍⲉⲥⲱⲉ
/next - Ⲃⲗⲓⳑⲁⲓⲱⲓⲓ ⲡⲣⲉⲇⲥⲧⲟⲩⲱⲓⲓ ⲡⲣⲁⲇⲇⲛⲓⲕ
/today - Ⲡⲣⲁⲇⲇⲛⲓⲕⲓ ⲛⲁ ⲥⲉⳑⲟⲇⲛⲟ (ⲉⲥⲗⲓ ⲉⲥⲧⲇ)
/help - Ⲉⲧⲁ ⲥⲡⲣⲁⲃⲕⲁ

Ⲩⲃⲉⲇⲟⲙⲗⲉⲛⲓⲟ ⲡⲣⲓⲭⲟⲇⲁⲧ ⲍⲁ 24 ⲭⲁⲥⲁ ⲇⲟ ⲡⲣⲁⲇⲇⲛⲓⲕⲁ!"""
                self.send_message(chat_id, help_msg)
            
            elif command == 'addme':
                if chat_id not in USER_CHAT_IDS:
                    USER_CHAT_IDS.append(chat_id)
                    msg = """Ⲟⲧⲗⲓⲭⲛⲟ! Ⲃⲩ ⲇⲟⲃⲁⲃⲗⲉⲛⲩ ⲃ ⲥⲡⲓⲥⲟⲕ ⲩⲃⲉⲇⲟⲙⲗⲉⲛⲓⲓ!

Ⲧⲉⲡⲉⲣⲇ ⲫ ⲃⲩⲇⲩ ⲥⲟⲟⲱⲱⲁⲧⲇ ⲃⲁⲙ ⲟ ⲡⲣⲁⲇⲇⲛⲓⲕⲁⲭ ⲇⲁ ⲇⲉⲛⲅ ⲇⲟ ⲛⲓⲭ ⲓⲭ ⲛⲁⲥⲧⲩⲡⲗⲉⲛⲓⲟ.

Ⲩⲧⲟⲃⲩ ⲟⲧⲡⲓⲥⲁⲧⲁⲥⲟ: /removeme"""
                else:
                    msg = """Ⲃⲩ ⲩⳑⲉ ⲡⲟⲇⲡⲓⲥⲁⲛⲩ! 

Ⲃⲩ ⲩⳑⲉ ⲡⲟⲗⲩⲭⲁⲧⲉ ⲩⲃⲉⲇⲟⲙⲗⲉⲛⲓⲟ ⲟ ⲡⲣⲁⲇⲇⲛⲓⲕⲁⲭ.

Ⲩⲧⲟⲃⲩ ⲟⲧⲡⲓⲥⲁⲧⲁⲥⲟ: /removeme"""
                self.send_message(chat_id, msg)
            
            elif command == 'removeme':
                if chat_id in USER_CHAT_IDS:
                    USER_CHAT_IDS.remove(chat_id)
                    msg = """Ⲃⲩ ⲟⲧⲡⲓⲥⲁⲗⲓⲥⲩ ⲟⲧ ⲩⲃⲉⲇⲟⲙⲗⲉⲛⲓⲓ ⲟ ⲡⲣⲁⲇⲇⲛⲓⲕⲁⲭ.

Ⲩⲧⲟⲃⲩ ⲥⲛⲟⲃⲁ ⲡⲟⲇⲡⲓⲥⲁⲧⲁⲥⲟ: /addme"""
                else:
                    msg = """Ⲃⲩ ⲛⲉ ⲡⲟⲇⲡⲓⲥⲁⲛⲩ ⲛⲁ ⲩⲃⲉⲇⲟⲙⲗⲉⲛⲓⲟ.

Ⲩⲧⲟⲃⲩ ⲡⲟⲇⲡⲓⲥⲁⲧⲁⲥⲟ: /addme"""
                self.send_message(chat_id, msg)
            
            elif command == 'holidays':
                holiday_list = "Ⲡⲟⲗⲛⲩⲓ ⥀ⲡⲓⲥⲟⲕ ⲡⲣⲁⲇⲇⲛⲓⲕⲟⲃ:\n\n"
                months = {
                    '01': 'Ⲱⲛⲁⲣⲓ', '02': 'Ⲑⲉⲃⲣⲁⲗⲓ', '03': 'Ⲙⲁⲣⲧ',
                    '04': 'Ⲁⲡⲣⲉⲗⲓ', '05': 'Ⲙⲁⲓ', '06': 'Ⲓⲩⲛⲓ',
                    '07': 'Ⲓⲩⲗⲓ', '08': 'Ⲁⲃⲅⲩⲥⲧ', '09': 'Ⲥⲉⲛⲧⲁⲃⲣⲓ',
                    '10': 'Ⲟⲕⲧⲁⲃⲣⲓ', '11': 'Ⲛⲟⲁⲃⲣⲓ', '12': 'Ⲑⲉⲕⲁⲃⲣⲓ'
                }
                
                for date_str, name in sorted(HOLIDAYS.items()):
                    month, day = date_str.split('-')
                    month_name = months.get(month, month)
                    holiday_list += f"Ⲕ {day} {month_name}: {name}\n"
                
                self.send_message(chat_id, holiday_list)
            
            elif command == 'month':
                current_month = datetime.now().strftime('%m')
                current_year = datetime.now().year
                months = {
                    '01': 'Ⲱⲛⲁⲣⲓ', '02': 'Ⲑⲉⲃⲣⲁⲗⲓ', '03': 'Ⲙⲁⲣⲧ',
                    '04': 'Ⲁⲡⲣⲉⲗⲓ', '05': 'Ⲙⲁⲓ', '06': 'Ⲓⲩⲛⲓ',
                    '07': 'Ⲓⲩⲗⲓ', '08': 'Ⲁⲃⲅⲩⲥⲧ', '09': 'Ⲥⲉⲛⲧⲁⲃⲣⲓ',
                    '10': 'Ⲟⲕⲧⲁⲃⲣⲓ', '11': 'Ⲛⲟⲁⲃⲣⲓ', '12': 'Ⲑⲉⲕⲁⲃⲣⲓ'
                }
                
                month_holidays = []
                for date_str, name in HOLIDAYS.items():
                    month, day = date_str.split('-')
                    if month == current_month:
                        month_holidays.append((day, name))
                
                month_name = months[current_month]
                if month_holidays:
                    msg = f"Ⲡⲣⲁⲇⲇⲛⲓⲕⲓ ⲃ {month_name} {current_year}:\n\n"
                    for day, name in sorted(month_holidays, key=lambda x: int(x[0])):
                        msg += f"Ⲕ {day} {month_name}: {name}\n"
                    msg += f"\nⲤⲥⲟⲅⲟ ⲡⲣⲁⲇⲇⲛⲓⲕⲟⲃ: {len(month_holidays)}"
                else:
                    msg = f"Ⲃ {month_name} {current_year} ⲛⲉⲧ ⲡⲣⲁⲇⲇⲛⲓⲕⲟⲃ."
                
                self.send_message(chat_id, msg)
            
            elif command == 'next':
                today = datetime.now()
                next_holiday = None
                next_date = None
                
                for i in range(1, 366):
                    check_date = today + timedelta(days=i)
                    date_key = f"{check_date.month:02d}-{check_date.day:02d}"
                    
                    if date_key in HOLIDAYS:
                        next_holiday = HOLIDAYS[date_key]
                        next_date = check_date
                        break
                
                if next_holiday:
                    days_until = (next_date - today).days
                    months = {
                        '01': 'Ⲱⲛⲁⲣⲁ', '02': 'Ⲑⲉⲃⲣⲁⲗⲁ', '03': 'Ⲙⲁⲣⲧⲁ',
                        '04': 'Ⲁⲡⲣⲉⲗⲁ', '05': 'Ⲙⲁⲁ', '06': 'Ⲓⲩⲛⲁ',
                        '07': 'Ⲓⲩⲗⲁ', '08': 'Ⲁⲃⲅⲩⲥⲧⲁ', '09': 'Ⲥⲉⲛⲧⲁⲃⲣⲁ',
                        '10': 'Ⲟⲕⲧⲁⲃⲣⲁ', '11': 'Ⲛⲟⲁⲃⲣⲁ', '12': 'Ⲑⲉⲕⲁⲃⲣⲁ'
                    }
                    
                    msg = f"""Ⲃⲗⲓⳑⲁⲓⲱⲓⲓ ⲡⲣⲁⲇⲇⲛⲓⲕ:

{next_holiday}
Ⲕ {next_date.day} {months[f"{next_date.month:02d}"]} {next_date.year}
Ⲥⲉⲣⲉⲇ {days_until} {'ⲇⲉⲛⲇ' if days_until == 1 else 'ⲇⲛⲉⲓ' if days_until < 5 else 'ⲇⲛⲉⲓ'}

Ⲛⲉ ⲡⲣⲟⲡⲩⲥⲧⲓⲧⲉ! Ⲩⲃⲉⲇⲟⲙⲗⲉⲛⲓⲉ ⲡⲣⲓⲭⲟⲇⲁⲧ ⲍⲁ ⲇⲉⲛⲅ ⲇⲟ ⲡⲣⲁⲇⲇⲛⲓⲕⲁ."""
                else:
                    msg = "Ⲃ ⲃⲗⲓⳑⲁⲓⲱⲓⲉⲙ ⲅⲟⲇⲩ ⲡⲣⲁⲇⲇⲛⲓⲕⲟⲃ ⲛⲉ ⲛⲁⲓⲇⲉⲛⲟ."
                
                self.send_message(chat_id, msg)
            
            elif command == 'today':
                today = datetime.now()
                date_key = f"{today.month:02d}-{today.day:02d}"
                
                if date_key in HOLIDAYS:
                    holiday_name = HOLIDAYS[date_key]
                    msg = f"""Ⲥⲉⳑⲟⲇⲛⲁ ⲡⲣⲁⲇⲇⲛⲓⲕ!

{holiday_name}
Ⲕ {today.day} {today.strftime('%B')} {today.year}

Ⲡⲟⲍⲇⲣⲁⲃⲗⲁⲩ ⲥ ⲡⲣⲁⲇⲇⲛⲓⲕⲟⲙ!"""
                else:
                    msg = """Ⲥⲉⳑⲟⲇⲛⲁ ⲡⲣⲁⲇⲇⲛⲓⲕⲟⲃ ⲛⲉⲧ.

Ⲛⲟ ⲃⲩ ⲙⲟⳑⲉⲧⲉ ⲡⲟⲥⲙⲟⲧⲣⲉⲧⲇ:
Ⲕ /next - Ⲃⲗⲓⳑⲁⲓⲱⲓⲓ ⲡⲣⲁⲇⲇⲛⲓⲕ
Ⲥ /month - Ⲡⲣⲁⲇⲇⲛⲓⲕⲓ ⲟⲧⲟⳘⲟ ⲍⲉⲥⲱⲉ
Ⲩ /holidays - Ⲃⲥⲉ ⲡⲣⲁⲇⲇⲛⲓⲕⲓ"""
                
                self.send_message(chat_id, msg)

def check_holidays(bot):
    """Check for holidays tomorrow and send notifications."""
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_key = f"{tomorrow.month:02d}-{tomorrow.day:02d}"
    
    if tomorrow_key in HOLIDAYS:
        holiday_name = HOLIDAYS[tomorrow_key]
        message = f"""Ⲥⲁⲃⲧⲣⲁ ⲡⲣⲁⲇⲇⲛⲓⲕ!

{holiday_name}
Ⲕ {tomorrow.day} {tomorrow.strftime('%B')} {tomorrow.year}

Ⲛⲉ ⲡⲣⲟⲡⲩⲥⲧⲓⲧⲉ! Ⲥ ⲛⲁⲥⲧⲩⲡⲁⲱⲱⲓⲉⲙ!"""
        
        for chat_id in USER_CHAT_IDS:
            bot.send_message(chat_id, message)
            logger.info(f"Sent holiday notification to {chat_id}")

def main():
    """Start the bot."""
    bot = TelegramBot(BOT_TOKEN)
    
    print("Starting holiday notification bot...")
    
    # Check holidays immediately on start
    check_holidays(bot)
    last_holiday_check = time.time()
    
    # Main loop to handle messages
    while True:
        try:
            current_time = time.time()
            
            # Check for holidays every 30 minutes
            if current_time - last_holiday_check >= 1800:  # 30 minutes
                check_holidays(bot)
                last_holiday_check = current_time
            
            updates = bot.get_updates()
            for update in updates:
                bot.handle_message(update)
            
            # Small delay between update checks
            time.sleep(5)
        except KeyboardInterrupt:
            print("Bot stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(30)

if __name__ == '__main__':
    main()
