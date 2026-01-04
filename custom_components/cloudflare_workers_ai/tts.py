"""Support for Cloudflare Workers AI Text-to-Speech."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.tts import TextToSpeechEntity, TtsAudioType
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .cloudflare_api import CloudflareAPI, CloudflareAPIError
from .const import CONF_TTS_MODEL, DEFAULT_TTS_MODEL, DOMAIN, TTS_MODELS

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
        return [CONF_TTS_MODEL]

    @property
    def default_options(self) -> dict[str, Any]:
        """Return default options."""
        model = self._config_entry.options.get(CONF_TTS_MODEL, DEFAULT_TTS_MODEL)
        return {CONF_TTS_MODEL: model}

    async def async_get_tts_audio(
        self, message: str, language: str, options: dict[str, Any] | None = None
    ) -> TtsAudioType:
        """Load TTS audio."""
        model = DEFAULT_TTS_MODEL
        
        if options and CONF_TTS_MODEL in options:
            model = options[CONF_TTS_MODEL]
        elif self._config_entry.options:
            model = self._config_entry.options.get(CONF_TTS_MODEL, DEFAULT_TTS_MODEL)

        if model not in TTS_MODELS:
            _LOGGER.error("Invalid TTS model: %s", model)
            return None, None

        try:
            _LOGGER.info("Generating TTS with model %s for text: %s", model, message[:50])
            audio_data = await self._api.text_to_speech(model, message)
            
            if audio_data and len(audio_data) > 0:
                _LOGGER.info("TTS generated %d bytes of audio", len(audio_data))
                return "mp3", audio_data
            else:
                _LOGGER.error("TTS returned empty audio data")
                return None, None
        except CloudflareAPIError as err:
            _LOGGER.error("Error generating TTS: %s", err)
            return None, None
