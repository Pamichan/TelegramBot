import telebot
import os
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, BotCommand

import threading
from flask import Flask

# یک وب‌سرور کوچک برای فریب دادن رندر و رایگان ماندن سرویس
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_web():
    app.run(host='0.0.0.0', port=10000)

# روشن کردن وب‌سرور در یک مسیر موازی
threading.Thread(target=run_web).daemon = True

# ==========================================
# تنظیمات اصلی ربات (حتما پر کنید)
# ==========================================
# --- تنظیمات اولیه ---
TOKEN = '8828297545:AAEiHJBkQ1pZjn3FQVkMeHGe2Bk6ptZpybo'
ADMIN_ID = 6100214954
GROUP_ID = -1004497215117
TOPIC_ID = 4

bot = telebot.TeleBot(TOKEN)

# ==========================================
# حافظه موقت و دیتابیس کاربران
# ==========================================
user_languages = {}
user_states = {}  
message_map = {} 
all_users = set()
active_admin_chat = {} # حافظه برای قفل چت هوشمند ادمین

if os.path.exists('users.txt'):
    with open('users.txt', 'r') as f:
        for line in f:
            if line.strip().isdigit():
                all_users.add(int(line.strip()))

def save_user(chat_id):
    if chat_id not in [ADMIN_ID, GROUP_ID] and chat_id not in all_users:
        all_users.add(chat_id)
        with open('users.txt', 'a') as f:
            f.write(f"{chat_id}\n")

# --- دیکشنری متن‌های دو زبانه ---
TEXTS = {
    'fa': {
        'welcome': 'بسیار خب! چطور می‌تونم کمکتون کنم؟ 🌸\nلطفاً از منوی پایین یک گزینه رو انتخاب کنید:',
        
        # دکمه‌های منو
        'contact': '📞 چت و ارتباط با من',
        'collab': '🤝 درخواست همکاری',
        'socials': '🌐 شبکه‌های اجتماعی من',
        'faq': '❓ سوالات متداول',
        'change_lang': 'تغییر زبان 🇬🇧',
        'exit_mode': '🔙 خروج و بازگشت',

        # پیام‌های داخل حالت‌ها
        'chat_mode_on': 'وارد بخش چت شدید 💬\nهر پیام، فایل، عکس یا حتی گیفی که دوست دارید بفرستید؛ مستقیم به دست خودم می‌رسه.\n\n(هر وقت حرف‌هامون تموم شد، می‌تونید دکمه «خروج» رو بزنید)',
        'collab_mode_on': 'به بخش همکاری خیلی خوش اومدید 🤝\nلطفاً رزومه، پروپوزال یا نمونه‌کارتون رو همینجا بفرستید.\n\n⚠️ نکته مهم: لطفاً حتماً همراه با فایلتون، یک راه ارتباطی (مثل شماره تماس، آیدی تلگرام یا ایمیل) هم بنویسید تا بتونم باهاتون در تماس باشم.\n\n(اگر منصرف شدید، دکمه «خروج» رو بزنید)',
        'chat_mode_off': 'از حالت چت خارج شدیم و به منوی اصلی برگشتیم 🔙',
        
        # پیام‌های سیستمی و خطاها
        'error_send': '⚠️ ای وای! مثل اینکه مشکلی پیش اومد و پیامتون ارسال نشد. ممنون میشم دوباره امتحان کنید.',
        'only_in_chat': 'برای اینکه پیامتون مستقیم به دستم برسه، اول از منوی پایین روی «ارتباط با من» یا «همکاری» کلیک کنید 👇',
        'canceled': 'عملیات لغو شد و به منوی اصلی برگشتیم 🔙',

        # متن‌های اطلاع‌رسانی
       'socials_text': 'خوشحال میشم تو شبکه‌های اجتماعی هم همراه من باشید 👇\n\n✈️ <a href="https://t.me/Rover_journal">چنل تلگرام</a>\n💬 <a href="https://t.me/RoverGap">گپ تلگرام</a>\n📸 <a href="https://www.instagram.com/rover_logs?igsh=MjVucXBtdnF6c3l6">اینستاگرام</a>\n▶️ <a href="https://youtube.com/@rover_logs?si=M6XOkL18alLiD3o">یوتیوب</a>\n🎵 <a href="https://www.tiktok.com/@rover_logs?_r=1&_t=ZN-98ZRjPlhdPq">تیک‌تاک</a>',
        'faq_text': '۱. چقدر طول می‌کشه تا جواب پیامم رو بدید؟\n- سعی می‌کنم در سریع‌ترین زمان ممکن (معمولاً کمتر از ۲۴ ساعت) پاسخ بدم.\n\n۲. آیا پروژه جدید برای همکاری قبول می‌کنید؟\n- بله، حتماً! لطفاً از طریق بخش «همکاری» رزومه یا طرحتون رو بفرستید تا بررسی کنم.'
    },
    'en': {
        'welcome': 'Alright! How can I help you today? ✨\nPlease select an option from the menu below:',
        
        # دکمه‌های منو
        'contact': '📞 Chat with Me',
        'collab': '🤝 Collaboration Request',
        'socials': '🌐 My Socials',
        'faq': '❓ FAQ',
        'change_lang': 'تغییر زبان 🇮🇷',
        'exit_mode': '🔙 Exit & Return',

        # پیام‌های داخل حالت‌ها
        'chat_mode_on': 'You have entered the chat 💬\nFeel free to send any message, file, photo, or GIF; it will reach me directly.\n\n(Whenever you are done, you can press the "Exit" button)',
        'collab_mode_on': 'Welcome to the collaboration section 🤝\nPlease send your CV, proposal, or portfolio here.\n\n⚠️ Important: Please make sure to include a contact method (like your phone number, Telegram ID, or email) in your message so I can reach back to you.\n\n(If you change your mind, press the "Exit" button)',
        'chat_mode_off': 'We left the chat and returned to the main menu 🔙',
        
        # پیام‌های سیستمی و خطاها
        'error_send': '⚠️ Oops! Looks like something went wrong and your message wasn\'t sent. Please try again.',
        'only_in_chat': 'To make sure your message reaches me directly, please click on "Chat with Me" or "Collaboration Request" from the menu below first 👇',
        'canceled': 'Action cancelled. We are back at the main menu 🔙',

        # متن‌های اطلاع‌رسانی
       'socials_text': 'I\'d love to connect with you on social media 👇\n\n✈️ <a href="https://t.me/Rover_journal">Telegram Channel</a>\n💬 <a href="https://t.me/RoverGap">Telegram Group</a>\n📸 <a href="https://www.instagram.com/rover_logs?igsh=MjVucXBtdnF6c3l6">Instagram</a>\n▶️ <a href="https://youtube.com/@rover_logs?si=M6XOkL18alLiD3o">YouTube</a>\n🎵 <a href="https://www.tiktok.com/@rover_logs?_r=1&_t=ZN-98ZRjPlhdPq">TikTok</a>',
        'faq_text': '1. How long does it take for you to reply?\n- I try to respond as quickly as possible (usually in less than 24 hours).\n\n2. Are you open to new collaboration projects?\n- Yes, absolutely! Please send your CV or proposal through the "Collaboration" section so I can review it.'
    }
}


# --- ساخت کیبوردها ---
def get_lang_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(KeyboardButton('🇮🇷 فارسی'), KeyboardButton('🇬🇧 English'))
    return markup

def get_main_keyboard(lang):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(KeyboardButton(TEXTS[lang]['contact']), KeyboardButton(TEXTS[lang]['collab']))
    markup.add(KeyboardButton(TEXTS[lang]['socials']), KeyboardButton(TEXTS[lang]['faq']))
    markup.add(KeyboardButton(TEXTS[lang]['change_lang']))
    return markup

def get_cancel_keyboard(lang):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(TEXTS[lang]['exit_mode']))
    return markup

# --- تابع ریپلای و قفل هوشمند ---
def send_reply_to_user(message):
    reply_to_id = message.reply_to_message.message_id
    target_user_id = None
    
    try:
        if reply_to_id in message_map:
            target_user_id = message_map[reply_to_id]['chat_id']
            original_message_id = message_map[reply_to_id]['message_id']
            bot.copy_message(chat_id=target_user_id, from_chat_id=message.chat.id, message_id=message.message_id, reply_to_message_id=original_message_id)
        elif message.reply_to_message.forward_from:
            target_user_id = message.reply_to_message.forward_from.id
            bot.copy_message(chat_id=target_user_id, from_chat_id=message.chat.id, message_id=message.message_id)
        else:
            bot.send_message(message.chat.id, "خطا: آیدی کاربر در دسترس نیست.")
            return

        if message.chat.id == ADMIN_ID and target_user_id:
            if active_admin_chat.get(ADMIN_ID) != target_user_id:
                active_admin_chat[ADMIN_ID] = target_user_id
                bot.send_message(ADMIN_ID, "🔗 قفل چت فعال شد!\nپیام‌های بعدی شما مستقیما برای این کاربر ارسال می‌شود.\nهر زمان چت تمام شد /cancel را بزنید.", disable_notification=True)

    except Exception as e:
        bot.send_message(message.chat.id, f"ارور در ارسال ریپلای: {e}")

def execute_broadcast(message):
    success_count = 0
    for u in all_users:
        try:
            bot.copy_message(chat_id=u, from_chat_id=ADMIN_ID, message_id=message.message_id)
            success_count += 1
        except Exception:
            pass 
    
    lang = user_languages.get(ADMIN_ID, 'fa')
    bot.send_message(ADMIN_ID, f"📢 پیام شما به {success_count} نفر ارسال شد.", reply_markup=get_main_keyboard(lang))
    user_states[ADMIN_ID] = 'main_menu'

# ==========================================
# دستورات (Commands)
# ==========================================

# دستور کنسل: بازگشت به منوی اصلی بدون ریست زبان
@bot.message_handler(commands=['cancel'])
def cancel_command(message):
    chat_id = message.chat.id
    save_user(chat_id)
    lang = user_languages.get(chat_id, 'fa')
    
    # خاموش کردن قفل چت ادمین
    if chat_id in active_admin_chat:
        del active_admin_chat[chat_id]
        bot.send_message(chat_id, "🔓 قفل چت غیرفعال شد.")
        
    user_states[chat_id] = 'main_menu'
    bot.send_message(chat_id, TEXTS[lang]['canceled'], reply_markup=get_main_keyboard(lang))

# دستور استارت و ریست کامل: بازگشت به منوی انتخاب زبان
@bot.message_handler(commands=['start', 'reset'])
def send_welcome(message):
    chat_id = message.chat.id
    save_user(chat_id)
    user_states[chat_id] = 'main_menu'
    
    if chat_id in active_admin_chat:
        del active_admin_chat[chat_id]
        
    bot.send_message(chat_id, "سلام! به ربات شخصی من خیلی خوش اومدی 🌸 برای شروع، لطفا زبانت رو انتخاب کن:\nHello and welcome! ✨ To get started, please select your preferred language:", reply_markup=get_lang_keyboard())

@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    if message.chat.id == ADMIN_ID:
        user_states[ADMIN_ID] = 'broadcast'
        bot.send_message(ADMIN_ID, "📢 حالت ارسال همگانی.\nپیام/گیف/فایل خود را بفرستید (برای لغو /cancel بزنید):")

# ==========================================
# پردازش پیام‌های متنی
# ==========================================
@bot.message_handler(content_types=['text'])
def handle_text(message):
    save_user(message.chat.id)
    state = user_states.get(message.chat.id, 'main_menu')
    lang = user_languages.get(message.chat.id, 'fa')
    text = message.text

    if message.chat.id == ADMIN_ID and state == 'broadcast':
        if text.startswith('/'): 
            return # توسط هندلرهای بالا (مثل cancel) مدیریت می‌شود
        execute_broadcast(message)
        return

    if message.chat.id in [ADMIN_ID, GROUP_ID] and message.reply_to_message:
        send_reply_to_user(message)
        return

    if message.chat.id == ADMIN_ID and ADMIN_ID in active_admin_chat:
        if not text.startswith('/'): 
            try:
                bot.copy_message(chat_id=active_admin_chat[ADMIN_ID], from_chat_id=ADMIN_ID, message_id=message.message_id)
            except Exception:
                bot.send_message(ADMIN_ID, "ارور در ارسال. شاید کاربر ربات را بلاک کرده است.")
            return

    if message.chat.id == GROUP_ID:
        return

    if text in ['🇮🇷 فارسی', '🇬🇧 English', 'تغییر زبان 🇬🇧', 'Change Language 🇮🇷']:
        user_languages[message.chat.id] = 'fa' if 'فارسی' in text or '🇮🇷' in text else 'en'
        lang = user_languages[message.chat.id]
        user_states[message.chat.id] = 'main_menu'
        bot.send_message(message.chat.id, TEXTS[lang]['welcome'], reply_markup=get_main_keyboard(lang))
        return

    if text == TEXTS[lang]['exit_mode']:
        user_states[message.chat.id] = 'main_menu'
        bot.send_message(message.chat.id, TEXTS[lang]['chat_mode_off'], reply_markup=get_main_keyboard(lang))
        return

    if state == 'chat_mode':
        try:
            forwarded_msg = bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
            message_map[forwarded_msg.message_id] = {'chat_id': message.chat.id, 'message_id': message.message_id}
        except Exception:
            bot.send_message(message.chat.id, TEXTS[lang]['error_send'])
            
    elif state == 'collab_mode':
        try:
            forwarded_msg = bot.forward_message(GROUP_ID, message.chat.id, message.message_id, message_thread_id=TOPIC_ID)
            message_map[forwarded_msg.message_id] = {'chat_id': message.chat.id, 'message_id': message.message_id}
        except Exception:
            bot.send_message(message.chat.id, TEXTS[lang]['error_send'])
            
    elif state == 'main_menu':
        if text == TEXTS[lang]['socials']:
           bot.send_message(message.chat.id, TEXTS[lang]['socials_text'], parse_mode='HTML')
        elif text == TEXTS[lang]['faq']:
            bot.send_message(message.chat.id, TEXTS[lang]['faq_text'])
        elif text == TEXTS[lang]['contact']:
            user_states[message.chat.id] = 'chat_mode'
            bot.send_message(message.chat.id, TEXTS[lang]['chat_mode_on'], reply_markup=get_cancel_keyboard(lang))
        elif text == TEXTS[lang]['collab']:
            user_states[message.chat.id] = 'collab_mode'
            bot.send_message(message.chat.id, TEXTS[lang]['collab_mode_on'], reply_markup=get_cancel_keyboard(lang))
        else:
            bot.send_message(message.chat.id, TEXTS[lang]['only_in_chat'])

# ==========================================
# پردازش فایل، گیف، عکس، استیکر و...
# ==========================================
@bot.message_handler(content_types=['photo', 'video', 'document', 'voice', 'audio', 'animation', 'sticker'])
def handle_media(message):
    save_user(message.chat.id)
    state = user_states.get(message.chat.id, 'main_menu')
    lang = user_languages.get(message.chat.id, 'fa')

    if message.chat.id == ADMIN_ID and state == 'broadcast':
        execute_broadcast(message)
        return

    if message.chat.id in [ADMIN_ID, GROUP_ID] and message.reply_to_message:
        send_reply_to_user(message)
        return

    if message.chat.id == ADMIN_ID and ADMIN_ID in active_admin_chat:
        try:
            bot.copy_message(chat_id=active_admin_chat[ADMIN_ID], from_chat_id=ADMIN_ID, message_id=message.message_id)
        except Exception:
            bot.send_message(ADMIN_ID, "ارور در ارسال مدیا.")
        return

    if message.chat.id == GROUP_ID:
        return

    if state == 'chat_mode':
        try:
            forwarded_msg = bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
            message_map[forwarded_msg.message_id] = {'chat_id': message.chat.id, 'message_id': message.message_id}
        except Exception:
            bot.send_message(message.chat.id, TEXTS[lang]['error_send'])
            
    elif state == 'collab_mode':
        try:
            forwarded_msg = bot.forward_message(GROUP_ID, message.chat.id, message.message_id, message_thread_id=TOPIC_ID)
            message_map[forwarded_msg.message_id] = {'chat_id': message.chat.id, 'message_id': message.message_id}
        except Exception:
             bot.send_message(message.chat.id, TEXTS[lang]['error_send'])
    else:
        bot.send_message(message.chat.id, TEXTS[lang]['only_in_chat'])

# --- استارت ربات ---
if __name__ == '__main__':
    commands = [
        BotCommand("start", "شروع ربات / Start Bot"),
        BotCommand("cancel", "لغو و بازگشت به منو / Cancel & Menu"),
        BotCommand("reset", "تغییر زبان / Change Language")
    ]
    bot.set_my_commands(commands)
    
    print("Bot is running with Cancel Command Support...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
