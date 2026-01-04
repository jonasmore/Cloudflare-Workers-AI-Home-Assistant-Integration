"""Constants for the Cloudflare Workers AI integration."""

DOMAIN = "cloudflare_workers_ai"

CONF_ACCOUNT_ID = "account_id"
CONF_API_TOKEN = "api_token"
CONF_TTS_MODEL = "tts_model"
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
