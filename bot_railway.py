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
                welcome_msg = """╔══════════════════════════════════════╗
║     𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 𝙃𝙤𝙡𝙞𝙙𝙖𝙮 𝘽𝙤𝙩!                                                ║
╚══════════════════════════════════════╝

⟨⟨⟨ 𝙄'𝙢 𝙮𝙤𝙪𝙧 𝙥𝙚𝙧𝙨𝙤𝙣𝙖𝙡 𝙝𝙤𝙡𝙞𝙙𝙖𝙮 𝙩𝙧𝙖𝙘𝙠𝙚𝙧! ⟩⟩⟩

┌─── 𝙒𝙝𝙖𝙩 𝙄 𝙘𝙖𝙣 𝙙𝙩 ───┐
│ • 𝙉𝙤𝙩𝙞𝙛𝙮 𝙮𝙤𝙪 𝙤𝙛 𝙝𝙤𝙡𝙞𝙙𝙖𝙮𝙨 𝙤𝙣𝙚 𝙙𝙖𝙮 𝙞𝙣 𝙖𝙙𝙫𝙖𝙣𝙘𝙚
│ • 𝙎𝙝𝙤𝙬 𝙖𝙡𝙡 𝙝𝙤𝙡𝙞𝙙𝙖𝙮𝙨
│ • 𝙏𝙚𝙡𝙡 𝙮𝙤𝙪 𝙖𝙗𝙤𝙪𝙩 𝙝𝙤𝙡𝙞𝙙𝙖𝙮𝙨 𝙩𝙝𝙞𝙨 𝙢𝙤𝙣𝙩𝙝
│ • 𝙃𝙞𝙜𝙝𝙡𝙞𝙜𝙝𝙩 𝙩𝙝𝙚 𝙣𝙚𝙭𝙩 𝙝𝙤𝙡𝙞𝙙𝙖𝙮
└─────────────────────────────────┘

╔══════════════════════════════════════╗
║              𝘾𝙤𝙢𝙢𝙖𝙣𝙙𝙨              ║
╚══════════════════════════════════════╝
/start - 𝙎𝙝𝙤𝙬 𝙩𝙝𝙞𝙨 𝙢𝙚𝙨𝙨𝙖𝙜𝙚
/addme - 𝙎𝙪𝙗𝙨𝙘𝙧𝙞𝙗𝙚 𝙩𝙤 𝙣𝙤𝙩𝙞𝙛𝙞𝙘𝙖𝙩𝙞𝙤𝙣𝙨
/removeme - 𝙐𝙣𝙨𝙪𝙗𝙨𝙘𝙧𝙞𝙗𝙚 𝙛𝙧𝙤𝙢 𝙣𝙤𝙩𝙞𝙛𝙞𝙘𝙖𝙩𝙞𝙤𝙣𝙨
/holidays - 𝘼𝙡𝙡 𝙝𝙤𝙡𝙞𝙙𝙖𝙮𝙨
/month - 𝙃𝙤𝙡𝙞𝙙𝙖𝙮𝙨 𝙩𝙝𝙞𝙨 𝙢𝙤𝙣𝙩𝙝
/next - 𝙉𝙚𝙭𝙩 𝙝𝙤𝙡𝙞𝙙𝙖𝙮
/today - 𝙃𝙤𝙡𝙞𝙙𝙖𝙮𝙨 𝙩𝙤𝙙𝙖𝙮
/help - 𝙃𝙚𝙡𝙥

* 𝙎𝙩𝙖𝙧𝙩 𝙬𝙞𝙩𝙝 /addme 𝙩𝙤 𝙜𝙚𝙩 𝙣𝙤𝙩𝙞𝙛𝙞𝙘𝙖𝙩𝙞𝙤𝙣𝙨! *"""
                self.send_message(chat_id, welcome_msg)
            
            elif command == 'help':
                help_msg = """╔══════════════════════════════════════╗
║              𝙃𝙚𝙡𝙥 𝙘𝙤𝙢𝙢𝙖𝙣𝙙𝙨!                                      ║
╚══════════════════════════════════════╝

┌─────────────────────────────────────┐
│ /start  - 𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙢𝙚𝙨𝙨𝙖𝙜𝙚 𝙖𝙣𝙙 𝙞𝙣𝙛𝙤 │
│ /addme  - 𝙎𝙪𝙗𝙨𝙘𝙧𝙞𝙗𝙚 𝙩𝙤 𝙝𝙤𝙡𝙞𝙙𝙖𝙮 𝙣𝙤𝙩𝙞𝙛𝙞𝙘𝙖𝙩𝙞𝙤𝙣𝙨 │
│ /removeme - 𝙐𝙣𝙨𝙪𝙗𝙨𝙘𝙧𝙞𝙗𝙚 𝙛𝙧𝙤𝙢 𝙣𝙤𝙩𝙞𝙛𝙞𝙘𝙖𝙩𝙞𝙤𝙣𝙨 │
│ /holidays - 𝙎𝙝𝙤𝙬 𝙛𝙪𝙡𝙡 𝙡𝙞𝙨𝙩 𝙤𝙛 𝙖𝙡𝙡 𝙝𝙤𝙡𝙞𝙙𝙖𝙮𝙨 │
│ /month - 𝙃𝙤𝙡𝙞𝙙𝙖𝙮𝙨 𝙞𝙣 𝙘𝙪𝙧𝙧𝙚𝙣𝙩 𝙢𝙤𝙣𝙩𝙝 │
│ /next   - 𝙉𝙚𝙭𝙩 𝙪𝙥𝙘𝙤𝙢𝙞𝙣𝙜 𝙝𝙤𝙡𝙞𝙙𝙖𝙮 │
│ /today  - 𝙃𝙤𝙡𝙞𝙙𝙖𝙮𝙨 𝙩𝙤𝙙𝙖𝙮 (𝙞𝙛 𝙖𝙣𝙮) │
│ /help   - 𝙏𝙝𝙞𝙨 𝙝𝙚𝙡𝙥 𝙢𝙚𝙨𝙨𝙖𝙜𝙚 │
└─────────────────────────────────────┘

* 𝙉𝙤𝙩𝙞𝙛𝙞𝙘𝙖𝙩𝙞𝙤𝙣𝙨 𝙘𝙤𝙢𝙚 24 𝙝𝙤𝙪𝙧𝙨 𝙗𝙚𝙛𝙤𝙧𝙚 𝙝𝙤𝙡𝙞𝙙𝙖𝙮𝙨! *"""
                self.send_message(chat_id, help_msg)
            
            elif command == 'addme':
                if chat_id not in USER_CHAT_IDS:
                    USER_CHAT_IDS.append(chat_id)
                    msg = """╔══════════════════════════════════════╗
║              * SUCCESS! *                                         ║
╚══════════════════════════════════════╝

⟨⟨⟨ PERFECT! YOU'RE ADDED TO THE NOTIFICATION LIST! ⟩⟩⟩

┌─── WHAT HAPPENS NOW ───┐
│ NOW I'LL INFORM YOU ABOUT │
│ HOLIDAYS ONE DAY BEFORE │
│ THEIR ARRIVAL! │
└─────────────────────────────┘

* TO UNSUBSCRIBE: /removeme *"""
                else:
                    msg = """╔══════════════════════════════════════╗
║              ! INFO !                                             ║
╚══════════════════════════════════════╝

⟨⟨⟨ YOU'RE ALREADY SUBSCRIBED! ⟩⟩⟩

┌─── YOUR STATUS ───┐
│ YOU'RE ALREADY RECEIVING │
│ HOLIDAY NOTIFICATIONS │
│ ONE DAY IN ADVANCE! │
└─────────────────────┘

* TO UNSUBSCRIBE: /removeme *"""
                self.send_message(chat_id, msg)
            
            elif command == 'removeme':
                if chat_id in USER_CHAT_IDS:
                    USER_CHAT_IDS.remove(chat_id)
                    msg = """╔══════════════════════════════════════╗
║             + UNSUBSCRIBED +                                      ║
╚══════════════════════════════════════╝

⟨⟨⟨ YOU'VE UNSUBSCRIBED FROM HOLIDAY NOTIFICATIONS ⟩⟩⟩

┌─── SORRY TO SEE YOU GO ───┐
│ YOU WON'T RECEIVE │
│ HOLIDAY NOTIFICATIONS │
│ ANYMORE! │
└───────────────────────┘

* TO SUBSCRIBE AGAIN: /addme *"""
                else:
                    msg = """╔══════════════════════════════════════╗
║              X ERROR X                                            ║
╚══════════════════════════════════════╝

⟨⟨⟨ YOU'RE NOT SUBSCRIBED TO NOTIFICATIONS ⟩⟩⟩

┌─── YOUR CURRENT STATUS ───┐
│ YOU'RE NOT RECEIVING │
│ ANY HOLIDAY NOTIFICATIONS │
│ RIGHT NOW │
└───────────────────────────┘

* TO SUBSCRIBE: /addme *"""
                self.send_message(chat_id, msg)
            
            elif command == 'holidays':
                holiday_list = """╔══════════════════════════════════════╗
║           𝙁𝙪𝙡𝙡 𝙡𝙞𝙨𝙩 𝙤𝙛 𝙝𝙤𝙡𝙞𝙙𝙖𝙮𝙨                                          ║
╚══════════════════════════════════════╝

"""
                months = {
                    '01': '𝙅𝙖𝙣𝙪𝙖𝙧𝙮', '02': '𝙁𝙚𝙗𝙧𝙪𝙖𝙧𝙮', '03': '𝙈𝙖𝙧𝙘𝙝',
                    '04': '𝘼𝙥𝙧𝙞𝙡', '05': '𝙈𝙖𝙮', '06': '𝙅𝙪𝙣𝙚',
                    '07': '𝙅𝙪𝙡𝙮', '08': '𝘼𝙪𝙜𝙪𝙨𝙩', '09': '𝙎𝙚𝙥𝙩𝙚𝙢𝙗𝙚𝙧',
                    '10': '𝙊𝙘𝙩𝙤𝙗𝙚𝙧', '11': '𝙉𝙤𝙫𝙚𝙢𝙗𝙚𝙧', '12': '𝘿𝙚𝙘𝙚𝙢𝙗𝙚𝙧'
                }
                
                for date_str, name in sorted(HOLIDAYS.items()):
                    month, day = date_str.split('-')
                    month_name = months.get(month, month)
                    holiday_list += f"┌───── DATE {day} {month_name} ─────┐\n"
                    holiday_list += f"│ {name} │\n"
                    holiday_list += f"└─────────────────────────┘\n\n"
                
                self.send_message(chat_id, holiday_list)
            
            elif command == 'month':
                current_month = datetime.now().strftime('%m')
                current_year = datetime.now().year
                months = {
                    '01': '𝙅𝙖𝙣𝙪𝙖𝙧𝙮', '02': '𝙁𝙚𝙗𝙧𝙪𝙖𝙧𝙮', '03': '𝙈𝙖𝙧𝙘𝙝',
                    '04': '𝘼𝙥𝙧𝙞𝙡', '05': '𝙈𝙖𝙮', '06': '𝙅𝙪𝙣𝙚',
                    '07': '𝙅𝙪𝙡𝙮', '08': '𝘼𝙪𝙜𝙪𝙨𝙩', '09': '𝙎𝙚𝙥𝙩𝙚𝙢𝙗𝙚𝙧',
                    '10': '𝙊𝙘𝙩𝙤𝙗𝙚𝙧', '11': '𝙉𝙤𝙫𝙚𝙢𝙗𝙚𝙧', '12': '𝘿𝙚𝙘𝙚𝙢𝙗𝙚𝙧'
                }
                
                month_holidays = []
                for date_str, name in HOLIDAYS.items():
                    month, day = date_str.split('-')
                    if month == current_month:
                        month_holidays.append((day, name))
                
                month_name = months[current_month]
                if month_holidays:
                    msg = f"""╔══════════════════════════════════════╗
║     𝙃𝙤𝙡𝙞𝙙𝙖𝙮𝙨 𝙞𝙣 {month_name} {current_year}                        ║
╚══════════════════════════════════════╝

"""
                    for day, name in sorted(month_holidays, key=lambda x: int(x[0])):
                        msg += f"┌───── DATE {day} {month_name} ─────┐\n"
                        msg += f"│ {name} │\n"
                        msg += f"└─────────────────────────┘\n\n"
                    msg += f"┌─── STATS ───┐\n"
                    msg += f"│ TOTAL HOLIDAYS: {len(month_holidays)} │\n"
                    msg += f"└─────────────────────┘"
                else:
                    msg = f"""╔══════════════════════════════════════╗
║         𝙉𝙤 𝙝𝙤𝙡𝙞𝙙𝙖𝙮𝙨 𝙞𝙣 {month_name} {current_year}                 ║
╚══════════════════════════════════════╝

┌─── CALENDAR ───┐
│ THIS MONTH IS │
│ HOLIDAY-FREE! │
└─────────────────┘"""
                
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
                        '01': '𝙅𝙖𝙣𝙪𝙖𝙧𝙮', '02': '𝙁𝙚𝙗𝙧𝙪𝙖𝙧𝙮', '03': '𝙈𝙖𝙧𝙘𝙝',
                        '04': '𝘼𝙥𝙧𝙞𝙡', '05': '𝙈𝙖𝙮', '06': '𝙅𝙪𝙣𝙚',
                        '07': '𝙅𝙪𝙡𝙮', '08': '𝘼𝙪𝙜𝙪𝙨𝙩', '09': '𝙎𝙚𝙥𝙩𝙚𝙢𝙗𝙚𝙧',
                        '10': '𝙊𝙘𝙩𝙤𝙗𝙚𝙧', '11': '𝙉𝙤𝙫𝙚𝙢𝙗𝙚𝙧', '12': '𝘿𝙚𝙘𝙚𝙢𝙗𝙚𝙧'
                    }
                    
                    msg = f"""╔══════════════════════════════════════╗
║                 𝙉𝙚𝙭𝙩 𝙝𝙤𝙡𝙞𝙙𝙖𝙮                                      ║
╚══════════════════════════════════════╝

┌───── STAR ─────┐
│ {next_holiday} │
└─────────────────┘

┌─── DATE ───┐
│ {next_date.day} {months[f"{next_date.month:02d}"]} {next_date.year} │
└───────────────┘

┌─── COUNTDOWN ───┐
│ IN {days_until} {'DAY' if days_until == 1 else 'DAYS'} │
└─────────────────┘

* DONT MISS IT! NOTIFICATION COMES ONE DAY BEFORE! *"""
                else:
                    msg = """╔══════════════════════════════════════╗
║            𝙉𝙤 𝙝𝙤𝙡𝙞𝙙𝙖𝙮𝙨 𝙛𝙤𝙪𝙣𝙙                                     ║
╚══════════════════════════════════════╝

┌─── CALENDAR ───┐
│ NO HOLIDAYS │
│ IN THE NEXT │
│ YEAR! │
└─────────────────┘"""
                
                self.send_message(chat_id, msg)
            
            elif command == 'today':
                today = datetime.now()
                date_key = f"{today.month:02d}-{today.day:02d}"
                
                if date_key in HOLIDAYS:
                    holiday_name = HOLIDAYS[date_key]
                    msg = f"""╔══════════════════════════════════════╗
║                HOLIDAY!                                            ║
╚══════════════════════════════════════╝

┌───── STAR ─────┐
│ {holiday_name} │
└─────────────────┘

┌─── DATE ───┐
│ {today.day} {today.strftime('%B')} {today.year} │
└───────────────┘

┌─── WISHES ───┐
│ HAPPY HOLIDAY! │
│ ENJOY THE │
│ CELEBRATION! │
└─────────────────┘"""
                else:
                    msg = """╔══════════════════════════════════════╗
║           NO HOLIDAYS TODAY                                       ║
╚══════════════════════════════════════╝

┌─── CALENDAR ───┐
│ REGULAR DAY │
│ NO HOLIDAYS │
│ TODAY │
└─────────────────┘

┌─── WHAT YOU CAN CHECK ───┐
│ /next - NEXT HOLIDAY │
│ /month - HOLIDAYS THIS MONTH │
│ /holidays - ALL HOLIDAYS │
└───────────────────────────┘"""
                
                self.send_message(chat_id, msg)

def check_holidays(bot):
    """Check for holidays tomorrow and send notifications."""
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_key = f"{tomorrow.month:02d}-{tomorrow.day:02d}"
    
    if tomorrow_key in HOLIDAYS:
        holiday_name = HOLIDAYS[tomorrow_key]
        message = f"""╔══════════════════════════════════════╗
║            BELL HOLIDAY ALERT!                             ║
╚══════════════════════════════════════╝

┌───── LIGHTNING ─────┐
│ HOLIDAY TOMORROW! │
└─────────────────────┘

┌───── STAR ─────┐
│ {holiday_name} │
└─────────────────┘

┌─── DATE ───┐
│ {tomorrow.day} {tomorrow.strftime('%B')} {tomorrow.year} │
└───────────────┘

┌─── LIGHTNING ───┐
│ DONT MISS IT! │
│ HAPPY ADVANCE! │
│ BE PREPARED! │
└─────────────────┘"""
        
        for chat_id in USER_CHAT_IDS:
            bot.send_message(chat_id, message)
            logger.info(f"Sent holiday notification to {chat_id}")
    else:
        pass

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
