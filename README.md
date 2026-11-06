# Awaaz Edge-TTS Server 🎙️

A high-speed, lightweight, production-ready Python Flask Text-to-Speech API powered by Microsoft Edge TTS. **Zero API keys, zero rate limits, and 100% free.**

Supports high-fidelity English along with **all Pakistani native and regional languages** (Urdu, Pakistani-accented English, Punjabi, and Pashto).

---

## 🚀 Quick Start (Local Run)

### 1. Install Dependencies
```bash
cd tts-server
pip install -r requirements.txt
```

### 2. Run the Server
```bash
python app.py
```
The server will start at `http://127.0.0.1:5000`.

---

## 📡 API Reference

### 1. Synthesize Speech (POST `/api/synthesize`)

Converts input text to an MP3 audio stream.

#### Endpoint
`POST http://localhost:5000/api/synthesize`

#### Headers
`Content-Type: application/json`

---

### Request Payload Examples

#### Example 1: Default English (`en-US-AndrewNeural`)
```json
{
  "text": "Welcome to Awaaz. Elevate your soul with books, audio, and news."
}
```

#### Example 2: Urdu (Pakistan)
```json
{
  "text": "آواز ایپ میں خوش آمدید۔ اردو کتابیں اور آڈیو بکس سنیں۔",
  "language": "urdu",
  "gender": "female"
}
```
*(Note: If you send Urdu text without specifying a language or voice, the server automatically detects the script and uses the Pakistani Urdu voice!)*

#### Example 3: Pakistani-Accented English
```json
{
  "text": "Breaking news from Islamabad today.",
  "language": "en-pk",
  "gender": "male"
}
```

#### Example 4: Punjabi
```json
{
  "text": "جی آیاں نوں، آواز لائیبریری وچ تہاڈا سواگت ہے۔",
  "language": "punjabi"
}
```

#### Example 5: Pashto
```json
{
  "text": "پہ آواز کښې هر کله راشئ.",
  "language": "pashto"
}
```

#### Example 6: Explicit Voice Name & Speed Adjustment
```json
{
  "text": "Listen to this news update in clear English.",
  "voice": "en-US-AndrewNeural",
  "rate": "+10%",
  "pitch": "+0Hz"
}
```

---

### Testing with `cURL` (Save direct to MP3)

```bash
curl -X POST http://localhost:5000/api/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Welcome to Awaaz audiobooks."}' \
  --output speech.mp3
```

---

## 🇵🇰 Supported Pakistani Languages & Voices

| Language | Locale Code | Voice Name (Female) | Voice Name (Male) |
| :--- | :---: | :--- | :--- |
| **Urdu (اردو)** | `ur` / `ur-pk` | `ur-PK-UzmaNeural` | `ur-PK-AsadNeural` |
| **English (Pakistani Accent)** | `en-pk` | `en-PK-UzmaNeural` | `en-PK-AsadNeural` |
| **Punjabi (پنجابی / ਪੰਜਾਬੀ)** | `pa` | `pa-IN-VaaniNeural` | `pa-IN-OjasNeural` |
| **Pashto (پښتو)** | `ps` | `ps-AF-LatifaNeural` | `ps-AF-GulNawazNeural` |
| **English (US - Default)** | `en` | `en-US-AriaNeural` | `en-US-AndrewNeural` |

---

## 🌐 Free Cloud Deployment Guide

### Option 1: Deploy to Render (Recommended - Free)
1. Push this folder to a GitHub repository.
2. Sign in to [Render](https://render.com).
3. Click **New +** $\to$ **Web Service**.
4. Connect your GitHub repository and set:
   - **Root Directory**: `tts-server` (or leave blank if it's the root of your repo)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --workers 2 --threads 4 --timeout 120 --bind 0.0.0.0:$PORT`
5. Click **Create Web Service**. Your free live URL will be ready in under 1 minute!

---

### Option 2: Deploy to Railway (Free)
1. Go to [Railway.app](https://railway.app).
2. Click **New Project** $\to$ **Deploy from GitHub repo**.
3. Railway automatically detects `requirements.txt` and `Procfile` and deploys your service.
4. Under project **Settings** $\to$ **Networking**, click **Generate Domain**.

---

## 📱 Android Client Integration (Kotlin / OkHttp)

```kotlin
fun playTextToSpeech(text: String, voice: String = "en-US-AndrewNeural", onReady: (File) -> Unit) {
    val client = OkHttpClient()
    val jsonBody = JSONObject().apply {
        put("text", text)
        put("voice", voice)
    }.toString().toRequestBody("application/json".toMediaType())

    val request = Request.Builder()
        .url("https://your-render-app.onrender.com/api/synthesize")
        .post(jsonBody)
        .build()

    client.newCall(request).enqueue(object : Callback {
        override fun onFailure(call: Call, e: IOException) {
            Log.e("TTS", "Synthesis failed: ${e.message}")
        }

        override fun onResponse(call: Call, response: Response) {
            response.body?.byteStream()?.use { input ->
                val tempFile = File.createTempFile("tts_", ".mp3")
                tempFile.outputStream().use { output -> input.copyTo(output) }
                onReady(tempFile)
            }
        }
    })
}
```

