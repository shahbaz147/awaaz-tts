import asyncio
import io
import os
import re
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import edge_tts

app = Flask(__name__)
# Enable CORS for all routes so mobile apps and web clients can access without restrictions
CORS(app)

# Default voice requested
DEFAULT_VOICE = "en-US-AndrewNeural"

# Supported Pakistani native & regional languages voice catalog
PAKISTANI_VOICES = {
    "urdu": {
        "female": "ur-PK-UzmaNeural",
        "male": "ur-PK-AsadNeural",
        "default": "ur-PK-UzmaNeural",
        "description": "Urdu (Pakistan) - اردو"
    },
    "urdu_in": {
        "female": "ur-IN-GulNeural",
        "male": "ur-IN-SalmanNeural",
        "default": "ur-IN-GulNeural",
        "description": "Urdu (Subcontinent) - اردو"
    },
    "english_pk": {
        "female": "en-PK-UzmaNeural",
        "male": "en-PK-AsadNeural",
        "default": "en-PK-UzmaNeural",
        "description": "English (Pakistani Accent)"
    },
    "punjabi": {
        "female": "pa-IN-VaaniNeural",
        "male": "pa-IN-OjasNeural",
        "default": "pa-IN-VaaniNeural",
        "description": "Punjabi - پنجابی / ਪੰਜਾਬੀ"
    },
    "pashto": {
        "female": "ps-AF-LatifaNeural",
        "male": "ps-AF-GulNawazNeural",
        "default": "ps-AF-LatifaNeural",
        "description": "Pashto - پښتو"
    },
    "sindhi": {
        "female": "ur-PK-UzmaNeural",
        "male": "ur-PK-AsadNeural",
        "default": "ur-PK-UzmaNeural",
        "description": "Sindhi - سنڌي (Pakistani Phonetic Model)"
    },
    "saraiki": {
        "female": "pa-IN-VaaniNeural",
        "male": "pa-IN-OjasNeural",
        "default": "pa-IN-VaaniNeural",
        "description": "Saraiki - سرائیکی (Lahnda Regional Model)"
    },
    "balochi": {
        "female": "ur-PK-UzmaNeural",
        "male": "ur-PK-AsadNeural",
        "default": "ur-PK-UzmaNeural",
        "description": "Balochi - بلوچی"
    },
    "hindko": {
        "female": "pa-IN-VaaniNeural",
        "male": "ur-PK-AsadNeural",
        "default": "pa-IN-VaaniNeural",
        "description": "Hindko - ہندکو"
    },
    "brahui": {
        "female": "ur-PK-UzmaNeural",
        "male": "ur-PK-AsadNeural",
        "default": "ur-PK-UzmaNeural",
        "description": "Brahui - براہوئی"
    },
    "burushaski": {
        "female": "ur-PK-UzmaNeural",
        "male": "ur-PK-AsadNeural",
        "default": "ur-PK-UzmaNeural",
        "description": "Burushaski - بروشسکی"
    },
    "shina": {
        "female": "ur-PK-UzmaNeural",
        "male": "ur-PK-AsadNeural",
        "default": "ur-PK-UzmaNeural",
        "description": "Shina - شینا"
    },
    "khowar": {
        "female": "ur-PK-UzmaNeural",
        "male": "ur-PK-AsadNeural",
        "default": "ur-PK-UzmaNeural",
        "description": "Khowar - کھوار"
    },
    "balti": {
        "female": "ur-PK-UzmaNeural",
        "male": "ur-PK-AsadNeural",
        "default": "ur-PK-UzmaNeural",
        "description": "Balti - بلتی"
    },
    "kashmiri": {
        "female": "ur-PK-UzmaNeural",
        "male": "ur-IN-SalmanNeural",
        "default": "ur-PK-UzmaNeural",
        "description": "Kashmiri - کاشمیری"
    },
    "hindi": {
        "female": "hi-IN-SwaraNeural",
        "male": "hi-IN-MadhurNeural",
        "default": "hi-IN-SwaraNeural",
        "description": "Hindi - हिंदी"
    },
    "bengali": {
        "female": "bn-IN-TanishaaNeural",
        "male": "bn-IN-BashkarNeural",
        "default": "bn-IN-TanishaaNeural",
        "description": "Bengali - বাংলা"
    },
    "english_us": {
        "female": "en-US-AriaNeural",
        "male": "en-US-AndrewNeural",
        "default": "en-US-AndrewNeural",
        "description": "English (US) - Default"
    }
}

# Regex to detect Arabic/Urdu/Pashto/Sindhi script
ARABIC_URDU_SCRIPT_REGEX = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]")


def get_script_fallback_voice(text: str) -> str:
    """Detects script alphabet to choose an intelligent native fallback voice."""
    if re.search(r"[\u0980-\u09FF]", text):
        return "bn-IN-TanishaaNeural"
    if re.search(r"[\u0900-\u097F]", text):
        return "hi-IN-SwaraNeural"
    if re.search(r"[\u0A00-\u0A7F]", text):
        return "pa-IN-VaaniNeural"
    if ARABIC_URDU_SCRIPT_REGEX.search(text):
        return "ur-PK-UzmaNeural"
    return DEFAULT_VOICE


def resolve_voice(text: str, requested_voice: str = None, requested_lang: str = None, gender: str = "female") -> str:
    """
    Resolves the best voice based on explicit voice parameter, language parameter,
    or automatic script detection for all Pakistani regional dialects and neighboring languages.
    """
    if requested_voice and requested_voice.strip():
        return requested_voice.strip()

    if requested_lang and requested_lang.strip():
        lang_key = requested_lang.strip().lower()
        selected_gender = "male" if gender and gender.lower() == "male" else "female"

        if lang_key in ("ur", "urdu", "pk", "ur-pk"):
            return PAKISTANI_VOICES["urdu"].get(selected_gender, PAKISTANI_VOICES["urdu"]["default"])
        elif lang_key in ("pa", "punjabi", "panjabi", "pa-in", "pa-pk"):
            if ARABIC_URDU_SCRIPT_REGEX.search(text):
                return PAKISTANI_VOICES["urdu"].get(selected_gender, PAKISTANI_VOICES["urdu"]["default"])
            return PAKISTANI_VOICES["punjabi"].get(selected_gender, PAKISTANI_VOICES["punjabi"]["default"])
        elif lang_key in ("ps", "pashto", "pushto", "pakhto", "ps-af", "ps-pk"):
            if ARABIC_URDU_SCRIPT_REGEX.search(text):
                return PAKISTANI_VOICES["urdu"].get(selected_gender, PAKISTANI_VOICES["urdu"]["default"])
            return PAKISTANI_VOICES["pashto"].get(selected_gender, PAKISTANI_VOICES["pashto"]["default"])
        elif lang_key in ("sd", "sindhi", "sd-pk", "sd-in"):
            return PAKISTANI_VOICES["sindhi"].get(selected_gender, PAKISTANI_VOICES["sindhi"]["default"])
        elif lang_key in ("skr", "saraiki", "seraiki", "siriki"):
            return PAKISTANI_VOICES["saraiki"].get(selected_gender, PAKISTANI_VOICES["saraiki"]["default"])
        elif lang_key in ("bal", "balochi", "baluchi"):
            return PAKISTANI_VOICES["balochi"].get(selected_gender, PAKISTANI_VOICES["balochi"]["default"])
        elif lang_key in ("hno", "hindko"):
            return PAKISTANI_VOICES["hindko"].get(selected_gender, PAKISTANI_VOICES["hindko"]["default"])
        elif lang_key in ("brh", "brahui"):
            return PAKISTANI_VOICES["brahui"].get(selected_gender, PAKISTANI_VOICES["brahui"]["default"])
        elif lang_key in ("bsk", "burushaski"):
            return PAKISTANI_VOICES["burushaski"].get(selected_gender, PAKISTANI_VOICES["burushaski"]["default"])
        elif lang_key in ("scl", "shina"):
            return PAKISTANI_VOICES["shina"].get(selected_gender, PAKISTANI_VOICES["shina"]["default"])
        elif lang_key in ("khw", "khowar", "chitrali"):
            return PAKISTANI_VOICES["khowar"].get(selected_gender, PAKISTANI_VOICES["khowar"]["default"])
        elif lang_key in ("bft", "balti"):
            return PAKISTANI_VOICES["balti"].get(selected_gender, PAKISTANI_VOICES["balti"]["default"])
        elif lang_key in ("ks", "kashmiri"):
            return PAKISTANI_VOICES["kashmiri"].get(selected_gender, PAKISTANI_VOICES["kashmiri"]["default"])
        elif lang_key in ("hi", "hindi", "hi-in"):
            return PAKISTANI_VOICES["hindi"].get(selected_gender, PAKISTANI_VOICES["hindi"]["default"])
        elif lang_key in ("bn", "bengali", "bangali", "bn-bd", "bn-in"):
            return PAKISTANI_VOICES["bengali"].get(selected_gender, PAKISTANI_VOICES["bengali"]["default"])
        elif lang_key in ("en-pk", "english-pk", "pakistani-english"):
            return PAKISTANI_VOICES["english_pk"].get(selected_gender, PAKISTANI_VOICES["english_pk"]["default"])
        elif lang_key in ("en", "english", "en-us"):
            return PAKISTANI_VOICES["english_us"].get(selected_gender, DEFAULT_VOICE)

    return get_script_fallback_voice(text)


async def generate_speech_bytes(text: str, voice: str, rate: str = "+0%", pitch: str = "+0Hz") -> io.BytesIO:
    """
    Generates MP3 audio stream in-memory using Microsoft Edge TTS without disk I/O.
    """
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch)
    buffer = io.BytesIO()

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buffer.write(chunk["data"])

    buffer.seek(0)
    return buffer


@app.route("/", methods=["GET"])
@app.route("/api", methods=["GET"])
@app.route("/api/", methods=["GET"])
@app.route("/api/health", methods=["GET"])
@app.route("/api/index.py", methods=["GET"])
def health_check():
    """Health check and service discovery endpoint."""
    return jsonify({
        "status": "online",
        "service": "Awaaz Edge-TTS Server (Vercel Serverless)",
        "default_voice": DEFAULT_VOICE,
        "supported_pakistani_languages": [
            {"language": "Urdu (اردو)", "code": "ur", "voices": ["ur-PK-UzmaNeural", "ur-PK-AsadNeural"]},
            {"language": "English (Pakistani Accent)", "code": "en-pk", "voices": ["en-PK-UzmaNeural", "en-PK-AsadNeural"]},
            {"language": "Punjabi (پنجابی)", "code": "pa", "voices": ["pa-IN-VaaniNeural", "pa-IN-OjasNeural"]},
            {"language": "Pashto (پښتو)", "code": "ps", "voices": ["ps-AF-LatifaNeural", "ps-AF-GulNawazNeural"]},
            {"language": "Sindhi (سنڌي)", "code": "sd", "voices": ["ur-PK-UzmaNeural", "ur-PK-AsadNeural"]},
            {"language": "Saraiki (سرائیکی)", "code": "skr", "voices": ["pa-IN-VaaniNeural", "pa-IN-OjasNeural"]},
            {"language": "Balochi (بلوچی)", "code": "bal", "voices": ["ur-PK-UzmaNeural", "ur-PK-AsadNeural"]},
            {"language": "Hindko (ہندکو)", "code": "hno", "voices": ["pa-IN-VaaniNeural", "ur-PK-AsadNeural"]},
            {"language": "Brahui (براہوئی)", "code": "brh", "voices": ["ur-PK-UzmaNeural", "ur-PK-AsadNeural"]},
            {"language": "Burushaski (بروشسکی)", "code": "bsk", "voices": ["ur-PK-UzmaNeural"]},
            {"language": "Shina (شینا)", "code": "scl", "voices": ["ur-PK-UzmaNeural"]},
            {"language": "Khowar (کھوار)", "code": "khw", "voices": ["ur-PK-UzmaNeural"]},
            {"language": "Balti (بلتی)", "code": "bft", "voices": ["ur-PK-UzmaNeural"]},
            {"language": "Kashmiri (کاشمیری)", "code": "ks", "voices": ["ur-PK-UzmaNeural"]},
            {"language": "Hindi (हिंदी)", "code": "hi", "voices": ["hi-IN-SwaraNeural", "hi-IN-MadhurNeural"]},
            {"language": "Bengali (বাংলা)", "code": "bn", "voices": ["bn-IN-TanishaaNeural", "bn-IN-BashkarNeural"]},
            {"language": "English (US)", "code": "en", "voices": ["en-US-AndrewNeural", "en-US-AriaNeural"]}
        ],
        "endpoints": {
            "synthesize": "POST /api/synthesize",
            "voices": "GET /api/voices"
        }
    }), 200


@app.route("/api/voices", methods=["GET"])
def list_voices():
    """Returns all available Pakistani and regional language voices."""
    return jsonify({
        "pakistani_voices": PAKISTANI_VOICES,
        "default_voice": DEFAULT_VOICE
    }), 200


@app.route("/api/synthesize", methods=["POST"])
def synthesize():
    """Converts text to MP3 speech stream."""
    try:
        data = request.get_json(silent=True)
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Invalid request. Expected JSON body with a 'text' field."}), 400

        text = data.get("text", "")
        if not isinstance(text, str) or not text.strip():
            return jsonify({"error": "Field 'text' is required and cannot be empty."}), 400

        text = text.strip()
        requested_voice = data.get("voice")
        requested_lang = data.get("language")
        gender = data.get("gender", "female")
        rate = data.get("rate", "+0%")
        pitch = data.get("pitch", "+0Hz")

        selected_voice = resolve_voice(text, requested_voice, requested_lang, gender)

        try:
            audio_buffer = asyncio.run(generate_speech_bytes(text, selected_voice, rate, pitch))
        except Exception as synth_err:
            fallback_voice = get_script_fallback_voice(text)
            if fallback_voice == selected_voice:
                fallback_voice = DEFAULT_VOICE
            try:
                audio_buffer = asyncio.run(generate_speech_bytes(text, fallback_voice, rate, pitch))
                selected_voice = fallback_voice
            except Exception:
                raise synth_err

        response = send_file(
            audio_buffer,
            mimetype="audio/mpeg",
            as_attachment=False,
            download_name="speech.mp3"
        )
        response.headers["Accept-Ranges"] = "bytes"
        response.headers["X-Voice-Used"] = selected_voice
        response.headers["Cache-Control"] = "no-cache"
        return response

    except Exception as e:
        return jsonify({
            "error": f"Failed to synthesize audio: {str(e)}",
            "hint": "Ensure UTF-8 encoding is used."
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
