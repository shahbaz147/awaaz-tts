import json
import urllib.request
import urllib.error
import sys
import os

SERVER_URL = "http://127.0.0.1:5000/api/synthesize"

TEST_CASES = [
    {
        "label": "Urdu (اردو)",
        "payload": {"text": "السلام علیکم! آواز نیوز میں خوش آمدید۔ آج کی اہم خبریں سنیں۔", "language": "urdu"},
        "file": "test_urdu.mp3"
    },
    {
        "label": "English (Pakistani Accent)",
        "payload": {"text": "Welcome to Awaaz News Briefs. Here is your sixty second daily update.", "language": "en-pk"},
        "file": "test_english_pk.mp3"
    },
    {
        "label": "Punjabi (پنجابی)",
        "payload": {"text": "جی آیاں نوں! آواز نیوز وچ اَج دیاں مکھ خبراں سنو۔", "language": "punjabi"},
        "file": "test_punjabi.mp3"
    },
    {
        "label": "Pashto (پښتو)",
        "payload": {"text": "پہ آواز کښې هر کله راشئ. د نن ورځې مهم خبرونه واورئ.", "language": "pashto"},
        "file": "test_pashto.mp3"
    },
    {
        "label": "Sindhi (سنڌي)",
        "payload": {"text": "آواز نيوز ۾ ڀلي ڪري آيا. اڄ جون اهم خبرون ٻڌو.", "language": "sindhi"},
        "file": "test_sindhi.mp3"
    },
    {
        "label": "Saraiki (سرائیکی)",
        "payload": {"text": "آواز نیوز اچ خوش آمدید۔ اڄ دیاں خاص خبراں سنو۔", "language": "saraiki"},
        "file": "test_saraiki.mp3"
    },
    {
        "label": "Balochi (بلوچی)",
        "payload": {"text": "آواز نیوز ءَ وش آتکگ ات۔ مروچی گپ ءُ تران گوش دار ات۔", "language": "balochi"},
        "file": "test_balochi.mp3"
    },
    {
        "label": "Hindko (ہندکو)",
        "payload": {"text": "آواز نیوز وچ تساں دا خیر مقدم اے۔ اَج دی خبراں سنو۔", "language": "hindko"},
        "file": "test_hindko.mp3"
    },
    {
        "label": "Brahui (براہوئی)",
        "payload": {"text": "آواز نیوز ٹی بخیر بفر۔ اینو نا خاص آ خبرا تے بنبو۔", "language": "brahui"},
        "file": "test_brahui.mp3"
    },
    {
        "label": "Burushaski (بروشسکی)",
        "payload": {"text": "آواز نیوز لو جوار۔ خبراں بنین۔", "language": "burushaski"},
        "file": "test_burushaski.mp3"
    },
    {
        "label": "Shina (شینا)",
        "payload": {"text": "آواز نیوز مجا بوٹیکر بخیر۔ اجو کی خبراں ہنش۔", "language": "shina"},
        "file": "test_shina.mp3"
    },
    {
        "label": "Khowar (کھوار)",
        "payload": {"text": "آواز نیوزا برائے مہربانی۔ نونی خبراں گوش دیور۔", "language": "khowar"},
        "file": "test_khowar.mp3"
    },
    {
        "label": "Balti (بلتی)",
        "payload": {"text": "آواز نیوز نا خیر مقدم۔ نا خبراں سنا۔", "language": "balti"},
        "file": "test_balti.mp3"
    },
    {
        "label": "Kashmiri (کاشمیری)",
        "payload": {"text": "آواز نیوٗزس منٛز توہہِ چھُ سۆاگتھ۔ ازکؠ اہم خبرٕ بوزِو۔", "language": "kashmiri"},
        "file": "test_kashmiri.mp3"
    },
    {
        "label": "Hindi (हिंदी)",
        "payload": {"text": "आवाज़ न्यूज़ में आपका स्वागत है। आज के मुख्य समाचार सुनें।", "language": "hindi"},
        "file": "test_hindi.mp3"
    },
    {
        "label": "Bengali (বাংলা)",
        "payload": {"text": "আওয়াজ নিউজে আপনাকে স্বাগতম। আজকের প্রধান খবর শুনুন।", "language": "bengali"},
        "file": "test_bengali.mp3"
    },
    {
        "label": "English (US Default)",
        "payload": {"text": "Welcome to Awaaz News. Here are today's top stories.", "language": "en"},
        "file": "test_english_us.mp3"
    }
]

def test_synthesis(payload: dict, output_filename: str, label: str):
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            SERVER_URL,
            data=data,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "User-Agent": "AwaazTester/1.0"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            audio_bytes = response.read()
            voice_used = response.headers.get("X-Voice-Used", "unknown")
            with open(output_filename, "wb") as f:
                f.write(audio_bytes)
            size_kb = len(audio_bytes) / 1024.0
            print(f"  ✅ {label.ljust(28)} -> Voice: {voice_used.ljust(22)} ({size_kb:.1f} KB)")
            return True
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"  ❌ {label.ljust(28)} -> HTTP {e.code}: {err_body}")
        return False
    except Exception as e:
        print(f"  ❌ {label.ljust(28)} -> Failed: {e}")
        return False

def main():
    print("=" * 75)
    print("🎙️ Awaaz Edge-TTS: All Pakistani & Regional Languages Test")
    print(f"Server Target: {SERVER_URL}")
    print("=" * 75)

    passed = 0
    for test in TEST_CASES:
        if test_synthesis(test["payload"], test["file"], test["label"]):
            passed += 1

    print("=" * 75)
    print(f"Results: {passed} / {len(TEST_CASES)} languages synthesized successfully!")
    print("=" * 75)

if __name__ == "__main__":
    main()
