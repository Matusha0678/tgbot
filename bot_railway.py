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
                welcome_msg = """🎉 *Добро пожаловать в Holiday Bot!*

Я ваш персональный помощник для отслеживания праздников! 

📅 *Что я умею:*
• Предупреждаю о праздниках за день до них
• Показываю список всех праздников
• Рассказываю о праздниках в текущем месяце
• Отмечаю ближайший праздник

🚀 *Команды:*
/start - Показать это сообщение
/addme - Подписаться на уведомления
/removeme - Отписаться от уведомлений
/holidays - Все праздники
/month - Праздники этого месяца
/next - Ближайший праздник
/today - Праздники сегодня
/help - Помощь

✨ Начните с команды /addme чтобы получать уведомления!"""
                self.send_message(chat_id, welcome_msg, parse_mode='Markdown')
            
            elif command == 'help':
                help_msg = """📚 *Справка по командам:*

/start - Приветствие и информация о боте
/addme - Подписаться на уведомления о праздниках
/removeme - Отписаться от уведомлений
/holidays - Показать полный список всех праздников
/month - Праздники в текущем месяце
/next - Ближайший предстоящий праздник
/today - Праздники на сегодня (если есть)
/help - Эта справка

⏰ Уведомления приходят за 24 часа до праздника!"""
                self.send_message(chat_id, help_msg, parse_mode='Markdown')
            
            elif command == 'addme':
                if chat_id not in USER_CHAT_IDS:
                    USER_CHAT_IDS.append(chat_id)
                    msg = """✅ *Отлично!* Вы добавлены в список уведомлений!

Теперь я буду сообщать вам о праздниках за день до их наступления.

🔔 Чтобы отписаться: /removeme"""
                else:
                    msg = """📱 *Вы уже подписаны!* 

Вы уже получаете уведомления о праздниках.

🔔 Чтобы отписаться: /removeme"""
                self.send_message(chat_id, msg, parse_mode='Markdown')
            
            elif command == 'removeme':
                if chat_id in USER_CHAT_IDS:
                    USER_CHAT_IDS.remove(chat_id)
                    msg = """❌ *Вы отписались* от уведомлений о праздниках.

Чтобы снова подписаться: /addme"""
                else:
                    msg = """📱 *Вы не подписаны* на уведомления.

Чтобы подписаться: /addme"""
                self.send_message(chat_id, msg, parse_mode='Markdown')
            
            elif command == 'holidays':
                holiday_list = "📅 *Полный список праздников:*\n\n"
                months = {
                    '01': 'Январь', '02': 'Февраль', '03': 'Март',
                    '04': 'Апрель', '05': 'Май', '06': 'Июнь',
                    '07': 'Июль', '08': 'Август', '09': 'Сентябрь',
                    '10': 'Октябрь', '11': 'Ноябрь', '12': 'Декабрь'
                }
                
                for date_str, name in sorted(HOLIDAYS.items()):
                    month, day = date_str.split('-')
                    month_name = months.get(month, month)
                    holiday_list += f"📆 {day} {month_name}: {name}\n"
                
                self.send_message(chat_id, holiday_list, parse_mode='Markdown')
            
            elif command == 'month':
                current_month = datetime.now().strftime('%m')
                current_year = datetime.now().year
                months = {
                    '01': 'Январь', '02': 'Февраль', '03': 'Март',
                    '04': 'Апрель', '05': 'Май', '06': 'Июнь',
                    '07': 'Июль', '08': 'Август', '09': 'Сентябрь',
                    '10': 'Октябрь', '11': 'Ноябрь', '12': 'Декабрь'
                }
                
                month_holidays = []
                for date_str, name in HOLIDAYS.items():
                    month, day = date_str.split('-')
                    if month == current_month:
                        month_holidays.append((day, name))
                
                month_name = months[current_month]
                if month_holidays:
                    msg = f"📅 *Праздники в {month_name} {current_year}:*\n\n"
                    for day, name in sorted(month_holidays, key=lambda x: int(x[0])):
                        msg += f"🎊 {day} {month_name}: {name}\n"
                    msg += f"\n📊 Всего праздников: {len(month_holidays)}"
                else:
                    msg = f"📅 *В {month_name} {current_year} нет праздников.*"
                
                self.send_message(chat_id, msg, parse_mode='Markdown')
            
            elif command == 'next':
                today = datetime.now()
                next_holiday = None
                next_date = None
                
                # Check next 365 days
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
                        '01': 'Января', '02': 'Февраля', '03': 'Марта',
                        '04': 'Апреля', '05': 'Мая', '06': 'Июня',
                        '07': 'Июля', '08': 'Августа', '09': 'Сентября',
                        '10': 'Октября', '11': 'Ноября', '12': 'Декабря'
                    }
                    
                    msg = f"""🎯 *Ближайший праздник:*

🎊 {next_holiday}
📅 {next_date.day} {months[f"{next_date.month:02d}"]} {next_date.year}
⏰ Через {days_until} {'день' if days_until == 1 else 'дней' if days_until < 5 else 'дней'}

🔔 Не пропустите! Уведомление придет за день до праздника."""
                else:
                    msg = "📅 *В ближайшем году праздников не найдено.*"
                
                self.send_message(chat_id, msg, parse_mode='Markdown')
            
            elif command == 'today':
                today = datetime.now()
                date_key = f"{today.month:02d}-{today.day:02d}"
                
                if date_key in HOLIDAYS:
                    holiday_name = HOLIDAYS[date_key]
                    msg = f"""🎉 *Сегодня праздник!*

🎊 {holiday_name}
📅 {today.day} {today.strftime('%B')} {today.year}

🎈 Поздравляю с праздником!"""
                else:
                    msg = """📅 *Сегодня праздников нет.*

Но вы можете посмотреть:
📆 /next - Ближайший праздник
📊 /month - Праздники этого месяца
📋 /holidays - Все праздники"""
                
                self.send_message(chat_id, msg, parse_mode='Markdown')

def check_holidays(bot):
    """Check for holidays tomorrow and send notifications."""
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_key = f"{tomorrow.month:02d}-{tomorrow.day:02d}"
    
    if tomorrow_key in HOLIDAYS:
        holiday_name = HOLIDAYS[tomorrow_key]
        message = f"""🎉 *Завтра праздник!*

🎊 {holiday_name}
📅 {tomorrow.day} {tomorrow.strftime('%B')} {tomorrow.year}

⏰ Не пропустите! С наступающим!"""
        
        for chat_id in USER_CHAT_IDS:
            bot.send_message(chat_id, message, parse_mode='Markdown')
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
