"""Config flow for Cloudflare Workers AI integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
import homeassistant.helpers.config_validation as cv

from .cloudflare_api import CloudflareAPI, CloudflareAPIError
from .const import (
    CONF_ACCOUNT_ID,
    CONF_API_TOKEN,
    CONF_LLM_HASS_API,
    CONF_LLM_MODEL,
    CONF_PROMPT,
    CONF_STT_MODEL,
    CONF_TTS_LANGUAGE,
    CONF_TTS_MODEL,
    CONF_TTS_VOICE,
    DEFAULT_LLM_MODEL,
    DEFAULT_PROMPT,
    DEFAULT_STT_MODEL,
    DEFAULT_TTS_LANGUAGE,
    DEFAULT_TTS_MODEL,
    DEFAULT_TTS_VOICES,
    DOMAIN,
    LLM_MODELS,
    STT_MODELS,
    TTS_LANGUAGES,
    TTS_MODELS,
    TTS_VOICES,
)

_LOGGER = logging.getLogger(__name__)


class CloudflareWorkersAIConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Cloudflare Workers AI."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            account_id = user_input[CONF_ACCOUNT_ID]
            api_token = user_input[CONF_API_TOKEN]

            try:
                api = CloudflareAPI(account_id, api_token)
                await api.test_connection()
            except CloudflareAPIError as err:
                _LOGGER.error("Cannot connect to Cloudflare API: %s", err)
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(account_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="Cloudflare Workers AI",
                    data={
                        CONF_ACCOUNT_ID: account_id,
                        CONF_API_TOKEN: api_token,
                    },
                    options={
                        CONF_TTS_MODEL: DEFAULT_TTS_MODEL,
                        CONF_STT_MODEL: DEFAULT_STT_MODEL,
                        CONF_LLM_MODEL: DEFAULT_LLM_MODEL,
                        CONF_LLM_HASS_API: "none",
                        CONF_PROMPT: DEFAULT_PROMPT,
                    },
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_ACCOUNT_ID): cv.string,
                vol.Required(CONF_API_TOKEN): cv.string,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle reconfiguration of the integration."""
        errors: dict[str, str] = {}
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])

        if user_input is not None:
            account_id = user_input[CONF_ACCOUNT_ID]
            api_token = user_input[CONF_API_TOKEN]

            try:
                api = CloudflareAPI(account_id, api_token)
                await api.test_connection()
            except CloudflareAPIError as err:
                _LOGGER.error("Cannot connect to Cloudflare API: %s", err)
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Update the config entry with new credentials
                self.hass.config_entries.async_update_entry(
                    entry,
                    data={
                        CONF_ACCOUNT_ID: account_id,
                        CONF_API_TOKEN: api_token,
                    },
                )
                # Reload the integration to use new credentials
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="reconfigure_successful")

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_ACCOUNT_ID,
                    default=entry.data.get(CONF_ACCOUNT_ID),
                ): cv.string,
                vol.Required(
                    CONF_API_TOKEN,
                    default=entry.data.get(CONF_API_TOKEN),
                ): cv.string,
            }
        )

        return self.async_show_form(
            step_id="reconfigure", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> CloudflareWorkersAIOptionsFlow:
        """Get the options flow for this handler."""
        return CloudflareWorkersAIOptionsFlow(config_entry)


class CloudflareWorkersAIOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Cloudflare Workers AI."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Clean up incompatible voice/language settings
            tts_model = user_input.get(CONF_TTS_MODEL)
            
            # Remove voice if model doesn't support it
            if tts_model not in TTS_VOICES and CONF_TTS_VOICE in user_input:
                user_input.pop(CONF_TTS_VOICE)
            
            # Remove language if model doesn't support it
            if tts_model not in TTS_LANGUAGES and CONF_TTS_LANGUAGE in user_input:
                user_input.pop(CONF_TTS_LANGUAGE)
            
            # Validate voice exists for the model
            if CONF_TTS_VOICE in user_input and tts_model in TTS_VOICES:
                if user_input[CONF_TTS_VOICE] not in TTS_VOICES[tts_model]:
                    # Reset to default voice if invalid
                    user_input[CONF_TTS_VOICE] = DEFAULT_TTS_VOICES.get(tts_model)
            
            return self.async_create_entry(title="", data=user_input)

        options = self._config_entry.options
        tts_model = options.get(CONF_TTS_MODEL, DEFAULT_TTS_MODEL)

        llm_apis = ["none", "assist", "conversation"]
        
        schema_dict = {
            vol.Required(
                CONF_TTS_MODEL,
                default=tts_model,
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        selector.SelectOptionDict(value=key, label=value)
                        for key, value in TTS_MODELS.items()
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
        }
        
        if tts_model in TTS_VOICES:
            voices = TTS_VOICES[tts_model]
            default_voice = DEFAULT_TTS_VOICES.get(tts_model, list(voices.keys())[0])
            
            # Get saved voice, validate it exists for this model
            saved_voice = options.get(CONF_TTS_VOICE, default_voice)
            if saved_voice not in voices:
                saved_voice = default_voice
            
            schema_dict[vol.Required(
                CONF_TTS_VOICE,
                default=saved_voice,
            )] = selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        selector.SelectOptionDict(value=key, label=value)
                        for key, value in voices.items()
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            )
        
        if tts_model in TTS_LANGUAGES:
            languages = TTS_LANGUAGES[tts_model]
            
            # Get saved language, validate it exists
            saved_language = options.get(CONF_TTS_LANGUAGE, DEFAULT_TTS_LANGUAGE)
            if saved_language not in languages:
                saved_language = DEFAULT_TTS_LANGUAGE
            
            schema_dict[vol.Required(
                CONF_TTS_LANGUAGE,
                default=saved_language,
            )] = selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        selector.SelectOptionDict(value=key, label=value)
                        for key, value in languages.items()
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            )
        
        schema_dict.update({
            vol.Required(
                CONF_STT_MODEL,
                default=options.get(CONF_STT_MODEL, DEFAULT_STT_MODEL),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        selector.SelectOptionDict(value=key, label=value)
                        for key, value in STT_MODELS.items()
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_LLM_MODEL,
                default=options.get(CONF_LLM_MODEL, DEFAULT_LLM_MODEL),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        selector.SelectOptionDict(value=key, label=value)
                        for key, value in LLM_MODELS.items()
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Optional(
                CONF_LLM_HASS_API,
                default=options.get(CONF_LLM_HASS_API, "none"),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        selector.SelectOptionDict(value=api, label=api.title() if api != "none" else "None (No device control)")
                        for api in llm_apis
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Optional(
                CONF_PROMPT,
                default=options.get(CONF_PROMPT, DEFAULT_PROMPT),
            ): selector.TextSelector(
                selector.TextSelectorConfig(
                    multiline=True,
                    type=selector.TextSelectorType.TEXT,
                )
            ),
        })
        
        data_schema = vol.Schema(schema_dict)

        return self.async_show_form(step_id="init", data_schema=data_schema)
