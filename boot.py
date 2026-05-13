import threading
import time
import schedule
import requests
from flask import Flask, render_template_string, request
import os

# ==================== بياناتك البرمجية ====================
ID_INSTANCE = "7107618599"
API_TOKEN = "b64ee4da37274ee0a2798c3f1bc3cfd09203b7f202a842e382"
GROUP_ID = "120363426154525956@g.us" 
# شيلنا توكن نجروك خلاص مش محتاجينه
# =========================================================

app = Flask(__name__)

ahadith = [
    "قال ﷺ: (من سلك طريقًا يلتمس فيه علمًا سهل الله له به طريقًا إلى الجنة)",
    "قال ﷺ: (الدال على الخير كفاعله)",
    "قال ﷺ: (من صلّى عليّ واحدة صلّى الله عليه بها عشراً)",
    "قال ﷺ: (كلمتان خفيفتان على اللسان، ثقيلتان في الميزان: سبحان الله وبحمده، سبحان الله العظيم)",
    "قال ﷺ: (خيركم من تعلم القرآن وعلمه)",
    "قال ﷺ: (إنما الأعمال بالنيات وإنما لكل امرئ ما نوى)",
    "قال ﷺ: (المسلم من سلم المسلمون من لسانه ويده)"
]

def send_wa(message):
    url = f"[https://7107.api.greenapi.com/waInstance](https://7107.api.greenapi.com/waInstance){ID_INSTANCE}/sendMessage/{API_TOKEN}"
    payload = {"chatId": GROUP_ID, "message": message}
    try:
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code == 200:
            print(f"✅ تم الإرسال للواتساب بنجاح")
    except Exception as e:
        print(f"⚠️ خطأ إرسال: {e}")

def send_random_hadith():
    hadith = ahadith[int(time.time()/600) % len(ahadith)]
    send_wa(f"📖 حديث شريف:\n{hadith}")

def setup_prayer_jobs():
    try:
        res = requests.get("[https://api.aladhan.com/v1/timingsByCity?city=Cairo&country=Egypt&method=5](https://api.aladhan.com/v1/timingsByCity?city=Cairo&country=Egypt&method=5)")
        times = res.json()['data']['timings']
        prayers = {"الفجر": times['Fajr'], "الظهر": times['Dhuhr'], "العصر": times['Asr'], "المغرب": times['Maghrib'], "العشاء": times['Isha']}
        schedule.clear('prayer-group')
        for name, p_time in prayers.items():
            schedule.every().day.at(p_time).do(lambda n=name: send_wa(f"🕋 حان الآن موعد أذان {n} بتوقيت القاهرة.")).tag('prayer-group')
        print("📍 تم تحديث مواقيت الصلاة")
    except:
        pass

# إرسال أول حديث فور التشغيل
send_random_hadith()

# جدولة المهام
schedule.every(1).hours.do(lambda: send_wa("🌹 تذكير: صلوا على النبي ﷺ 🌹"))
schedule.every(10).minutes.do(send_random_hadith)
setup_prayer_jobs()

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

html_page = """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>لوحة تحكم بوت علي سكر</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #e5ddd5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); width: 100%; max-width: 450px; text-align: center; }
        h2 { color: #075e54; }
        textarea { width: 100%; height: 150px; padding: 15px; border: 1px solid #ccc; border-radius: 10px; font-size: 16px; margin-bottom: 15px; resize: none; box-sizing: border-box;}
        button { background: #25d366; color: white; border: none; padding: 15px; border-radius: 10px; cursor: pointer; font-size: 18px; width: 100%; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🕋 تحكم بوت (ذكر الله)</h2>
        <form method="POST">
            <textarea name="msg" placeholder="اكتب رسالة يدوية هنا..."></textarea>
            <button type="submit">إرسال للجروب الآن</button>
        </form>
        {% if status %}<p style="color: #075e54; margin-top: 10px;">{{ status }}</p>{% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    status = None
    if request.method == 'POST':
        message = request.form.get('msg')
        if message:
            send_wa(message)
            status = "✅ تم الإرسال بنجاح!"
    return render_template_string(html_page, status=status)

if __name__ == '__main__':
    threading.Thread(target=run_scheduler, daemon=True).start()
    # أهم تعديل لـ Render: قراءة البورت من البيئة المحيطة
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
