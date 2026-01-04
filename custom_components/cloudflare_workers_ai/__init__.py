"""The Cloudflare Workers AI integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .cloudflare_api import CloudflareAPI, CloudflareAPIError
from .const import CONF_ACCOUNT_ID, CONF_API_TOKEN, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.TTS, Platform.STT, Platform.CONVERSATION]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Cloudflare Workers AI from a config entry."""
    account_id = entry.data[CONF_ACCOUNT_ID]
    api_token = entry.data[CONF_API_TOKEN]

    api = CloudflareAPI(account_id, api_token)

    try:
        await api.test_connection()
    except CloudflareAPIError as err:
        _LOGGER.error("Failed to connect to Cloudflare API: %s", err)
        raise ConfigEntryNotReady from err

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "account_id": account_id,
        "api_token": api_token,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
