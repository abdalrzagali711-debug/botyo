import telebot
import yt_dlp
import os
from flask import Flask
from threading import Thread

TOKEN = "8577286605:AAHVkonH1grTFnHZeOaTmGnFw21XWhRNAYs"
bot = telebot.TeleBot(TOKEN)

app = Flask('')
@app.route('/')
def home(): return "OK"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

@bot.message_handler(func=lambda m: "youtube.com" in m.text or "youtu.be" in m.text)
def download_video(message):
    msg = bot.reply_to(message, "⏳ جاري التحميل بأفضل جودة مناسبة...")
    try:
        # إعدادات متطورة لاختيار جودة لا تتخطى 50 ميجا
        ydl_opts = {
            'format': 'best[filesize<50M]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': 'video_%(id)s.mp4',
            'noplaylist': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(message.text, download=True)
            filename = ydl.prepare_filename(info)
        
        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video, caption="تم التحميل بنجاح ✅")
        
        os.remove(filename)
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ فشل التحميل. السبب: الفيديو محمي أو حجمه كبير جداً.", message.chat.id, msg.message_id)
        print(f"Error: {e}")

if __name__ == "__main__":
    Thread(target=lambda: bot.infinity_polling(skip_pending=True)).start()
    run()
