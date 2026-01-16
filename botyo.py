import telebot
import yt_dlp
import os
from flask import Flask
from threading import Thread

# --- إعدادات البوت ---
TOKEN = "8577286605:AAHVkonH1grTFnHZeOaTmGnFw21XWhRNAYs"
bot = telebot.TeleBot(TOKEN)

# --- سيرفر الويب للبقاء حياً ---
app = Flask('')
@app.route('/')
def home():
    return "YouTube Downloader is Online!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- وظائف التحميل ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! أرسل لي رابط فيديو من يوتيوب وسأقوم بتحميله لك.")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text
    if "youtube.com" in url or "youtu.be" in url:
        msg = bot.reply_to(message, "⏳ جاري جلب الفيديو، انتظر قليلاً...")
        
        try:
            # إعدادات التحميل
            ydl_opts = {
                'format': 'best',
                'outtmpl': 'video.mp4',
                'max_filesize': 50 * 1024 * 1024, # حد 50 ميجا لتجنب مشاكل رندر وتليجرام
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # إرسال الفيديو للمستخدم
            with open('video.mp4', 'rb') as video:
                bot.send_video(message.chat.id, video, caption="تم التحميل بواسطة بوتك!")
            
            # حذف الملف بعد الإرسال لتوفير المساحة
            os.remove('video.mp4')
            bot.delete_message(message.chat.id, msg.message_id)
            
        except Exception as e:
            bot.edit_message_text(f"❌ حدث خطأ: تأكد من أن حجم الفيديو ليس كبيراً جداً.", message.chat.id, msg.message_id)
            if os.path.exists('video.mp4'): os.remove('video.mp4')
    else:
        bot.reply_to(message, "الرجاء إرسال رابط يوتيوب صحيح.")

# --- تشغيل البوت ---
if __name__ == "__main__":
    keep_alive()
    print("Bot is running...")
    bot.infinity_polling()