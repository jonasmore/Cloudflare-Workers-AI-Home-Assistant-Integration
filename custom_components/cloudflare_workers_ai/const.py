"""Constants for the Cloudflare Workers AI integration."""

DOMAIN = "cloudflare_workers_ai"

CONF_ACCOUNT_ID = "account_id"
CONF_API_TOKEN = "api_token"
CONF_TTS_MODEL = "tts_model"
CONF_TTS_VOICE = "tts_voice"
CONF_TTS_LANGUAGE = "tts_language"
CONF_STT_MODEL = "stt_model"
CONF_LLM_MODEL = "llm_model"
CONF_LLM_HASS_API = "llm_hass_api"
CONF_PROMPT = "prompt"

DEFAULT_PROMPT = """You are a voice assistant for Home Assistant.
Your job is to help users control their smart home devices and answer questions.
Be concise and helpful."""

API_BASE_URL = "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}"

TTS_MODELS = {
    "@cf/deepgram/aura-2-en": "Aura 2 English (Recommended)",
    "@cf/deepgram/aura-2-es": "Aura 2 Spanish",
    "@cf/deepgram/aura-1": "Aura 1",
    "@cf/myshell-ai/melotts": "MeloTTS",
}

STT_MODELS = {
    "@cf/openai/whisper": "Whisper (Recommended)",
    "@cf/openai/whisper-large-v3-turbo": "Whisper Large V3 Turbo",
    "@cf/openai/whisper-tiny-en": "Whisper Tiny English",
    "@cf/deepgram/nova-3": "Deepgram Nova 3",
}

LLM_MODELS = {
    "@hf/nousresearch/hermes-2-pro-mistral-7b": "Hermes 2 Pro Mistral 7B",
    "@cf/meta/llama-4-scout-17b-16e-instruct": "Llama 4 Scout 17B",
    "@cf/meta/llama-3.3-70b-instruct-fp8-fast": "Llama 3.3 70B Fast",
    "@cf/mistralai/mistral-small-3.1-24b-instruct": "Mistral Small 3.1 24B",
}

# Models that support function calling for device control
# Based on Cloudflare documentation and testing
FUNCTION_CALLING_MODELS = [
    "@hf/nousresearch/hermes-2-pro-mistral-7b",
    "@cf/nousresearch/hermes-2-pro-mistral-7b",
    "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
    "@cf/meta/llama-4-scout-17b-16e-instruct",
    "@cf/mistralai/mistral-small-3.1-24b-instruct",
]

DEFAULT_TTS_MODEL = "@cf/deepgram/aura-2-en"
DEFAULT_STT_MODEL = "@cf/openai/whisper"
DEFAULT_LLM_MODEL = "@hf/nousresearch/hermes-2-pro-mistral-7b"

TTS_VOICES = {
    "@cf/deepgram/aura-2-en": {
        "amalthea": "Amalthea",
        "andromeda": "Andromeda",
        "apollo": "Apollo",
        "arcas": "Arcas",
        "aries": "Aries",
        "asteria": "Asteria",
        "athena": "Athena",
        "atlas": "Atlas",
        "aurora": "Aurora",
        "callista": "Callista",
        "cora": "Cora",
        "cordelia": "Cordelia",
        "delia": "Delia",
        "draco": "Draco",
        "electra": "Electra",
        "harmonia": "Harmonia",
        "helena": "Helena",
        "hera": "Hera",
        "hermes": "Hermes",
        "hyperion": "Hyperion",
        "iris": "Iris",
        "janus": "Janus",
        "juno": "Juno",
        "jupiter": "Jupiter",
        "luna": "Luna",
        "mars": "Mars",
        "minerva": "Minerva",
        "neptune": "Neptune",
        "odysseus": "Odysseus",
        "ophelia": "Ophelia",
        "orion": "Orion",
        "orpheus": "Orpheus",
        "pandora": "Pandora",
        "phoebe": "Phoebe",
        "pluto": "Pluto",
        "saturn": "Saturn",
        "thalia": "Thalia",
        "theia": "Theia",
        "vesta": "Vesta",
        "zeus": "Zeus",
    },
    "@cf/deepgram/aura-2-es": {
        "sirio": "Sirio",
        "nestor": "Nestor",
        "carina": "Carina",
        "celeste": "Celeste",
        "alvaro": "Alvaro",
        "diana": "Diana",
        "aquila": "Aquila",
        "selena": "Selena",
        "estrella": "Estrella",
        "javier": "Javier",
    },
    "@cf/deepgram/aura-1": {
        "angus": "Angus",
        "asteria": "Asteria",
        "arcas": "Arcas",
        "orion": "Orion",
        "orpheus": "Orpheus",
        "athena": "Athena",
        "luna": "Luna",
        "zeus": "Zeus",
        "perseus": "Perseus",
        "helios": "Helios",
        "hera": "Hera",
        "stella": "Stella",
    },
}

TTS_LANGUAGES = {
    "@cf/myshell-ai/melotts": {
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "zh": "Chinese",
        "ja": "Japanese",
        "ko": "Korean",
    },
}

DEFAULT_TTS_VOICES = {
    "@cf/deepgram/aura-2-en": "luna",
    "@cf/deepgram/aura-2-es": "aquila",
    "@cf/deepgram/aura-1": "angus",
}

DEFAULT_TTS_LANGUAGE = "en"
