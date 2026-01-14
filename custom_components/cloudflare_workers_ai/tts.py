"""Support for Cloudflare Workers AI Text-to-Speech."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.tts import TextToSpeechEntity, TtsAudioType
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .cloudflare_api import CloudflareAPI, CloudflareAPIError
from .const import (
    CONF_TTS_LANGUAGE,
    CONF_TTS_MODEL,
    CONF_TTS_VOICE,
    DEFAULT_TTS_LANGUAGE,
    DEFAULT_TTS_MODEL,
    DEFAULT_TTS_VOICES,
    DOMAIN,
    TTS_LANGUAGES,
    TTS_MODELS,
    TTS_VOICES,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Cloudflare Workers AI TTS platform."""
    api: CloudflareAPI = hass.data[DOMAIN][config_entry.entry_id]["api"]
    
    async_add_entities([CloudflareWorkersTTS(api, config_entry)])


class CloudflareWorkersTTS(TextToSpeechEntity):
    """Cloudflare Workers AI TTS entity."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, api: CloudflareAPI, config_entry: ConfigEntry) -> None:
        """Initialize TTS entity."""
        self._api = api
        self._config_entry = config_entry
        self._attr_name = "Cloudflare Workers AI TTS"
        self._attr_unique_id = f"{config_entry.entry_id}_tts"

    @property
    def supported_languages(self) -> list[str]:
        """Return list of supported languages."""
        return ["en", "es", "fr", "de", "it", "pt", "nl", "pl", "ru", "zh", "ja", "ko"]

    @property
    def default_language(self) -> str:
        """Return the default language."""
        return "en"

    @property
    def supported_options(self) -> list[str]:
        """Return list of supported options."""
        return [CONF_TTS_MODEL, CONF_TTS_VOICE, CONF_TTS_LANGUAGE]

    @property
    def default_options(self) -> dict[str, Any]:
        """Return default options."""
        model = self._config_entry.options.get(CONF_TTS_MODEL, DEFAULT_TTS_MODEL)
        options = {CONF_TTS_MODEL: model}
        
        # Add voice if model supports it
        if model in TTS_VOICES:
            default_voice = DEFAULT_TTS_VOICES.get(model)
            voice = self._config_entry.options.get(CONF_TTS_VOICE, default_voice)
            if voice:
                options[CONF_TTS_VOICE] = voice
        
        # Add language if model supports it
        if model in TTS_LANGUAGES:
            language = self._config_entry.options.get(CONF_TTS_LANGUAGE, DEFAULT_TTS_LANGUAGE)
            options[CONF_TTS_LANGUAGE] = language
        
        return options

    async def async_get_tts_audio(
        self, message: str, language: str, options: dict[str, Any] | None = None
    ) -> TtsAudioType:
        """Load TTS audio."""
        model = DEFAULT_TTS_MODEL
        voice = None
        tts_language = None
        
        if options and CONF_TTS_MODEL in options:
            model = options[CONF_TTS_MODEL]
        elif self._config_entry.options:
            model = self._config_entry.options.get(CONF_TTS_MODEL, DEFAULT_TTS_MODEL)

        if model not in TTS_MODELS:
            _LOGGER.error("Invalid TTS model: %s", model)
            return None, None

        # Get voice parameter if model supports it
        if model in TTS_VOICES:
            if options and CONF_TTS_VOICE in options:
                voice = options[CONF_TTS_VOICE]
            elif self._config_entry.options:
                voice = self._config_entry.options.get(
                    CONF_TTS_VOICE, 
                    DEFAULT_TTS_VOICES.get(model)
                )
        
        # Get language parameter if model supports it
        if model in TTS_LANGUAGES:
            if options and CONF_TTS_LANGUAGE in options:
                tts_language = options[CONF_TTS_LANGUAGE]
            elif self._config_entry.options:
                tts_language = self._config_entry.options.get(
                    CONF_TTS_LANGUAGE, 
                    DEFAULT_TTS_LANGUAGE
                )

        try:
            _LOGGER.info(
                "Generating TTS with model %s, voice %s, language %s for text: %s", 
                model, voice, tts_language, message[:50]
            )
            audio_data = await self._api.text_to_speech(
                model, message, voice=voice, language=tts_language
            )
            
            if audio_data and len(audio_data) > 0:
                _LOGGER.info("TTS generated %d bytes of audio", len(audio_data))
                return "mp3", audio_data
            else:
                _LOGGER.error("TTS returned empty audio data")
                return None, None
        except CloudflareAPIError as err:
            _LOGGER.error("Error generating TTS: %s", err)
            return None, None
