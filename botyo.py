import telebot
import yt_dlp
import os
from flask import Flask
from threading import Thread

# --- إعدادات البوت ---
TOKEN = "8577286605:AAHVkonH1grTFnHZeOaTmGnFw21XWhRNAYs" # ضع التوكن الخاص بك هنا
bot = telebot.TeleBot(TOKEN)

# --- سيرفر ويب خفيف لإبقاء البوت حياً ---
app = Flask('')
@app.route('/')
def home():
    return "OK"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 1. الرسالة الترحيبية ---
@bot.message_handler(commands=['start'])
def welcome(message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"👋 أهلاً بك يا {user_name} في بوت تحميل الفيديوهات!\n\n"
        "📥 أنا هنا لمساعدتك في تحميل فيديوهات يوتيوب بسهولة.\n"
        "✨ فقط أرسل لي رابط الفيديو (أو Shorts) وسأقوم بمعالجته لك فوراً.\n\n"
        "⚠️ ملاحظة: أقصى حجم مدعوم للإرسال هو 50 ميجابايت."
    )
    bot.reply_to(message, welcome_text)

# --- 2. معالجة روابط يوتيوب والتحميل الذكي ---
@bot.message_handler(func=lambda m: "youtube.com" in m.text or "youtu.be" in m.text)
def download_logic(message):
    msg = bot.reply_to(message, "⏳ جاري فحص حجم الفيديو والتحميل... يرجى الانتظار.")
    
    try:
        # إعدادات yt-dlp لاختيار جودة لا تتعدى 50 ميجا
        # تقوم هذه الصيغة باختيار أفضل جودة متاحة بشرط ألا يتجاوز الحجم 48MB
        ydl_opts = {
            'format': 'best[filesize<48M]/bestvideo[ext=mp4][filesize<40M]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(message.text, download=True)
            file_path = ydl.prepare_filename(info)

        # إرسال الفيديو للمستخدم
        with open(file_path, 'rb') as video:
            bot.send_video(message.chat.id, video, caption="✅ تم التحميل بنجاح بواسطة بوتك!")
        
        # حذف الملف بعد الإرسال لتوفير مساحة في Render
        if os.path.exists(file_path):
            os.remove(file_path)
        bot.delete_message(message.chat.id, msg.message_id)

    except Exception as e:
        error_msg = "❌ عذراً، لا يمكن تحميل هذا الفيديو:\n"
        if "filesize" in str(e).lower():
            error_msg += "الحجم لا يزال كبيراً جداً حتى بعد محاولة الضغط."
        else:
            error_msg += "الفيديو قد يكون محمياً أو هناك مشكلة في الرابط."
        
        bot.edit_message_text(error_msg, message.chat.id, msg.message_id)
        print(f"Error detail: {e}")

# --- تشغيل البوت والسيرفر ---
if __name__ == "__main__":
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    # تشغيل البوت في خيط منفصل
    Thread(target=lambda: bot.infinity_polling(skip_pending=True)).start()
    # تشغيل السيرفر الرئيسي لـ Render
    run()
