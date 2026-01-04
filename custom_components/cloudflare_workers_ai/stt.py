"""Support for Cloudflare Workers AI Speech-to-Text."""
from __future__ import annotations

from collections.abc import AsyncIterable
import io
import logging
import wave
import struct

from homeassistant.components.stt import (
    AudioBitRates,
    AudioChannels,
    AudioCodecs,
    AudioFormats,
    AudioSampleRates,
    SpeechMetadata,
    SpeechResult,
    SpeechResultState,
    SpeechToTextEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .cloudflare_api import CloudflareAPI, CloudflareAPIError
from .const import CONF_STT_MODEL, DEFAULT_STT_MODEL, DOMAIN, STT_MODELS

_LOGGER = logging.getLogger(__name__)


def create_wav_header(sample_rate: int, bits_per_sample: int, channels: int, data_size: int) -> bytes:
    """Create a WAV file header for raw PCM data."""
    # WAV file header structure
    header = struct.pack('<4sI4s', b'RIFF', 36 + data_size, b'WAVE')
    
    # fmt subchunk
    fmt_chunk = struct.pack('<4sIHHIIHH',
        b'fmt ',           # Subchunk1ID
        16,                # Subchunk1Size (16 for PCM)
        1,                 # AudioFormat (1 = PCM)
        channels,          # NumChannels
        sample_rate,       # SampleRate
        sample_rate * channels * bits_per_sample // 8,  # ByteRate
        channels * bits_per_sample // 8,  # BlockAlign
        bits_per_sample    # BitsPerSample
    )
    
    # data subchunk header
    data_header = struct.pack('<4sI', b'data', data_size)
    
    return header + fmt_chunk + data_header


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Cloudflare Workers AI STT platform."""
    api: CloudflareAPI = hass.data[DOMAIN][config_entry.entry_id]["api"]
    
    async_add_entities([CloudflareWorkersSTT(api, config_entry)])


class CloudflareWorkersSTT(SpeechToTextEntity):
    """Cloudflare Workers AI STT entity."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, api: CloudflareAPI, config_entry: ConfigEntry) -> None:
        """Initialize STT entity."""
        self._api = api
        self._config_entry = config_entry
        self._attr_name = "Cloudflare Workers AI STT"
        self._attr_unique_id = f"{config_entry.entry_id}_stt"

    @property
    def supported_languages(self) -> list[str]:
        """Return list of supported languages."""
        return ["en", "es", "fr", "de", "it", "pt", "nl", "pl", "ru", "zh", "ja", "ko"]

    @property
    def supported_formats(self) -> list[AudioFormats]:
        """Return list of supported formats."""
        return [AudioFormats.WAV, AudioFormats.OGG]

    @property
    def supported_codecs(self) -> list[AudioCodecs]:
        """Return list of supported codecs."""
        return [AudioCodecs.PCM, AudioCodecs.OPUS]

    @property
    def supported_bit_rates(self) -> list[AudioBitRates]:
        """Return list of supported bit rates."""
        return [AudioBitRates.BITRATE_16]

    @property
    def supported_sample_rates(self) -> list[AudioSampleRates]:
        """Return list of supported sample rates."""
        return [AudioSampleRates.SAMPLERATE_16000]

    @property
    def supported_channels(self) -> list[AudioChannels]:
        """Return list of supported channels."""
        return [AudioChannels.CHANNEL_MONO]

    async def async_process_audio_stream(
        self, metadata: SpeechMetadata, stream: AsyncIterable[bytes]
    ) -> SpeechResult:
        """Process audio stream to text."""
        model = self._config_entry.options.get(CONF_STT_MODEL, DEFAULT_STT_MODEL)

        if model not in STT_MODELS:
            _LOGGER.error("Invalid STT model: %s", model)
            return SpeechResult(None, SpeechResultState.ERROR)

        try:
            # Collect audio chunks into a list first (more efficient than concatenating bytes)
            audio_chunks = []
            chunk_count = 0
            total_bytes = 0
            
            async for chunk in stream:
                if chunk:  # Skip empty chunks
                    audio_chunks.append(chunk)
                    chunk_count += 1
                    total_bytes += len(chunk)
            
            # Concatenate all chunks at once
            audio_data = b"".join(audio_chunks)

            _LOGGER.info(
                "STT: Received %d chunks, total %d bytes, format=%s, codec=%s, sample_rate=%s",
                chunk_count,
                len(audio_data),
                metadata.format,
                metadata.codec,
                metadata.sample_rate,
            )
            
            if len(audio_data) == 0:
                _LOGGER.error("STT: No audio data received")
                return SpeechResult(None, SpeechResultState.ERROR)
            
            if len(audio_data) < 1000:
                _LOGGER.warning("STT: Audio data seems too short (%d bytes)", len(audio_data))
            
            # Log audio format details for debugging
            _LOGGER.debug("Audio first 100 bytes: %s", audio_data[:100].hex() if len(audio_data) >= 100 else audio_data.hex())
            _LOGGER.debug("Audio last 20 bytes: %s", audio_data[-20:].hex() if len(audio_data) >= 20 else "N/A")
            
            # Home Assistant sends raw PCM data, not WAV files
            # We need to wrap it in a WAV container for Cloudflare
            if not audio_data.startswith(b'RIFF'):
                _LOGGER.info("STT: Converting raw PCM to WAV format")
                
                # Get audio parameters from metadata
                sample_rate = 16000  # Default
                if metadata.sample_rate == AudioSampleRates.SAMPLERATE_16000:
                    sample_rate = 16000
                elif metadata.sample_rate == AudioSampleRates.SAMPLERATE_8000:
                    sample_rate = 8000
                elif metadata.sample_rate == AudioSampleRates.SAMPLERATE_22050:
                    sample_rate = 22050
                elif metadata.sample_rate == AudioSampleRates.SAMPLERATE_44100:
                    sample_rate = 44100
                elif metadata.sample_rate == AudioSampleRates.SAMPLERATE_48000:
                    sample_rate = 48000
                
                channels = 1  # Mono
                bits_per_sample = 16  # 16-bit PCM
                
                # Create WAV header and prepend to audio data
                wav_header = create_wav_header(sample_rate, bits_per_sample, channels, len(audio_data))
                audio_data = wav_header + audio_data
                
                _LOGGER.info("STT: Created WAV file: %d Hz, %d-bit, %d channel(s), %d bytes total", 
                           sample_rate, bits_per_sample, channels, len(audio_data))
                _LOGGER.debug("STT: WAV header: %s", audio_data[:44].hex())
            else:
                _LOGGER.info("STT: Audio already in WAV format")
            
            text = await self._api.speech_to_text(model, audio_data)
            
            if text:
                _LOGGER.info("STT result: %s", text)
                return SpeechResult(text, SpeechResultState.SUCCESS)
            else:
                _LOGGER.error("STT returned empty result")
                return SpeechResult(None, SpeechResultState.ERROR)
                
        except CloudflareAPIError as err:
            _LOGGER.error("Error processing STT: %s", err)
            return SpeechResult(None, SpeechResultState.ERROR)
        except Exception as err:
            _LOGGER.exception("Unexpected error in STT processing: %s", err)
            return SpeechResult(None, SpeechResultState.ERROR)
