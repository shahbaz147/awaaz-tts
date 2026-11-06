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

# Default voice requested (Ava is Microsoft's most natural human conversational voice)
DEFAULT_VOICE = "en-US-AvaNeural"

# Supported core languages voice catalog: Urdu, Punjabi, English, Hindi, Bengali
SUPPORTED_VOICES = {
    "urdu": {
        "female": "ur-PK-UzmaNeural",
        "male": "ur-PK-AsadNeural",
        "default": "ur-PK-UzmaNeural",
        "description": "Urdu (اردو)"
    },
    "punjabi": {
        "female": "pa-IN-VaaniNeural",
        "male": "pa-IN-OjasNeural",
        "default": "pa-IN-VaaniNeural",
        "description": "Punjabi (پنجابی / ਪੰਜਾਬੀ)"
    },
    "english": {
        "female": "en-US-AvaNeural",
        "male": "en-US-AndrewNeural",
        "default": "en-US-AvaNeural",
        "description": "English (Ultra Human)"
    },
    "english_pk": {
        "female": "en-PK-UzmaNeural",
        "male": "en-PK-AsadNeural",
        "default": "en-PK-UzmaNeural",
        "description": "English (Pakistani Accent)"
    },
    "hindi": {
        "female": "hi-IN-SwaraNeural",
        "male": "hi-IN-MadhurNeural",
        "default": "hi-IN-SwaraNeural",
        "description": "Hindi (हिंदी)"
    },
    "bengali": {
        "female": "bn-IN-TanishaaNeural",
        "male": "bn-IN-BashkarNeural",
        "default": "bn-IN-TanishaaNeural",
        "description": "Bengali (বাংলা)"
    }
}

# Regex to detect Arabic/Urdu script
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
    Resolves the best voice for the 5 supported languages: Urdu, Punjabi, English, Hindi, Bengali.
    """
    if requested_voice and requested_voice.strip():
        return requested_voice.strip()

    if requested_lang and requested_lang.strip():
        lang_key = requested_lang.strip().lower()
        selected_gender = "male" if gender and gender.lower() == "male" else "female"

        if lang_key in ("ur", "urdu", "pk", "ur-pk"):
            if not ARABIC_URDU_SCRIPT_REGEX.search(text):
                # Text is in English script; use natural Pakistani English accent
                return SUPPORTED_VOICES["english_pk"].get(selected_gender, SUPPORTED_VOICES["english_pk"]["default"])
            return SUPPORTED_VOICES["urdu"].get(selected_gender, SUPPORTED_VOICES["urdu"]["default"])
        elif lang_key in ("pa", "punjabi", "panjabi", "pa-in", "pa-pk"):
            if ARABIC_URDU_SCRIPT_REGEX.search(text):
                return SUPPORTED_VOICES["urdu"].get(selected_gender, SUPPORTED_VOICES["urdu"]["default"])
            return SUPPORTED_VOICES["punjabi"].get(selected_gender, SUPPORTED_VOICES["punjabi"]["default"])
        elif lang_key in ("hi", "hindi", "hi-in"):
            return SUPPORTED_VOICES["hindi"].get(selected_gender, SUPPORTED_VOICES["hindi"]["default"])
        elif lang_key in ("bn", "bengali", "bangali", "bn-bd", "bn-in"):
            return SUPPORTED_VOICES["bengali"].get(selected_gender, SUPPORTED_VOICES["bengali"]["default"])
        elif lang_key in ("en", "english", "en-us", "en-pk"):
            return SUPPORTED_VOICES["english"].get(selected_gender, DEFAULT_VOICE)

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
        "supported_languages": [
            {"language": "Urdu (اردو)", "code": "ur", "voices": ["ur-PK-UzmaNeural", "ur-PK-AsadNeural"]},
            {"language": "Punjabi (پنجابی)", "code": "pa", "voices": ["pa-IN-VaaniNeural", "pa-IN-OjasNeural"]},
            {"language": "English", "code": "en", "voices": ["en-US-AvaNeural", "en-PK-UzmaNeural"]},
            {"language": "Hindi (हिंदी)", "code": "hi", "voices": ["hi-IN-SwaraNeural", "hi-IN-MadhurNeural"]},
            {"language": "Bengali (বাংলা)", "code": "bn", "voices": ["bn-IN-TanishaaNeural", "bn-IN-BashkarNeural"]}
        ],
        "endpoints": {
            "synthesize": "POST /api/synthesize",
            "voices": "GET /api/voices"
        }
    }), 200


@app.route("/api/voices", methods=["GET"])
@app.route("/voices", methods=["GET"])
def list_voices():
    """Returns all available core language voices."""
    return jsonify({
        "supported_voices": SUPPORTED_VOICES,
        "default_voice": DEFAULT_VOICE
    }), 200


@app.route("/api/synthesize", methods=["GET", "POST"])
@app.route("/synthesize", methods=["GET", "POST"])
def synthesize():
    """Converts text to MP3 speech stream (supports both GET query and POST JSON)."""
    try:
        if request.method == "GET":
            text = request.args.get("text", "")
            requested_voice = request.args.get("voice")
            requested_lang = request.args.get("language") or request.args.get("lang")
            gender = request.args.get("gender", "female")
            rate = request.args.get("rate", "+0%")
            pitch = request.args.get("pitch", "+0Hz")
        else:
            data = request.get_json(silent=True) or {}
            text = data.get("text", "")
            requested_voice = data.get("voice")
            requested_lang = data.get("language") or data.get("lang")
            gender = data.get("gender", "female")
            rate = data.get("rate", "+0%")
            pitch = data.get("pitch", "+0Hz")

        if not isinstance(text, str) or not text.strip():
            return jsonify({"error": "Field 'text' is required and cannot be empty."}), 400

        text = text.strip()
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
        response.headers["Cache-Control"] = "public, max-age=86400, s-maxage=86400"
        return response

    except Exception as e:
        return jsonify({
            "error": f"Failed to synthesize audio: {str(e)}",
            "hint": "Ensure UTF-8 encoding is used."
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
