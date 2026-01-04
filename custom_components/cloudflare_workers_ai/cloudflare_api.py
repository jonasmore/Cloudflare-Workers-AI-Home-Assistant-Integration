"""Cloudflare Workers AI API client."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)


class CloudflareAPIError(Exception):
    """Exception raised for Cloudflare API errors."""


class CloudflareAPI:
    """Cloudflare Workers AI API client."""

    def __init__(self, account_id: str, api_token: str) -> None:
        """Initialize the API client."""
        self.account_id = account_id
        self.api_token = api_token
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run"

    def _get_headers(self) -> dict[str, str]:
        """Get headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_token}",
        }

    async def verify_token(self) -> bool:
        """Verify the API token using Cloudflare's official verify endpoint."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/tokens/verify"
                async with session.get(url, headers=self._get_headers()) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("success"):
                            _LOGGER.info("API token verified successfully")
                            return True
                        else:
                            _LOGGER.error("API token verification failed: %s", result)
                            raise CloudflareAPIError("Token verification failed")
                    else:
                        error_text = await response.text()
                        _LOGGER.error(
                            "Failed to verify API token (status %s): %s", response.status, error_text
                        )
                        raise CloudflareAPIError(f"Token verification failed with status {response.status}")
        except CloudflareAPIError:
            raise
        except Exception as err:
            _LOGGER.error("Error verifying API token: %s", err)
            raise CloudflareAPIError(f"Token verification failed: {err}") from err

    async def test_connection(self) -> bool:
        """Test the API connection by verifying token and checking AI models access."""
        try:
            # First verify the token
            await self.verify_token()
            
            # Then check AI models access
            async with aiohttp.ClientSession() as session:
                url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/models/search"
                async with session.get(url, headers=self._get_headers()) as response:
                    if response.status == 200:
                        _LOGGER.info("Successfully connected to Cloudflare Workers AI")
                        return True
                    _LOGGER.error(
                        "Failed to access Cloudflare Workers AI: %s", response.status
                    )
                    raise CloudflareAPIError(f"Cannot access Workers AI (status {response.status})")
        except CloudflareAPIError:
            raise
        except Exception as err:
            _LOGGER.error("Error testing Cloudflare API connection: %s", err)
            raise CloudflareAPIError(f"Connection test failed: {err}") from err

    async def text_to_speech(self, model: str, text: str) -> bytes:
        """Convert text to speech using specified model."""
        url = f"{self.base_url}/{model}"
        
        # Different models use different parameter names
        if "melotts" in model.lower():
            payload = {"prompt": text}
        else:
            payload = {"text": text}

        try:
            async with aiohttp.ClientSession() as session:
                headers = self._get_headers()
                headers["Content-Type"] = "application/json"
                
                _LOGGER.debug("TTS request to %s with text: %s", url, text[:50])
                
                async with session.post(
                    url, headers=headers, json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        _LOGGER.error(
                            "TTS API error (status %s): %s", response.status, error_text
                        )
                        raise CloudflareAPIError(
                            f"TTS request failed with status {response.status}: {error_text}"
                        )
                    
                    content_type = response.headers.get("Content-Type", "")
                    _LOGGER.debug("TTS response content-type: %s", content_type)
                    
                    # MeloTTS returns JSON with base64-encoded audio
                    if "melotts" in model.lower() and "application/json" in content_type:
                        import base64
                        json_data = await response.json()
                        if "result" in json_data and "audio" in json_data["result"]:
                            audio_base64 = json_data["result"]["audio"]
                            audio_data = base64.b64decode(audio_base64)
                            _LOGGER.debug("TTS decoded %d bytes from base64", len(audio_data))
                            return audio_data
                        else:
                            _LOGGER.error("MeloTTS response missing audio field: %s", json_data)
                            raise CloudflareAPIError("MeloTTS response missing audio field")
                    else:
                        # Aura models return raw audio bytes
                        audio_data = await response.read()
                        _LOGGER.debug("TTS received %d bytes of audio data", len(audio_data))
                        return audio_data
        except CloudflareAPIError:
            raise
        except Exception as err:
            _LOGGER.error("TTS request failed: %s", err)
            raise CloudflareAPIError(f"TTS request failed: {err}") from err

    async def speech_to_text(self, model: str, audio_data: bytes) -> str:
        """Convert speech to text using specified model."""
        url = f"{self.base_url}/{model}"

        try:
            async with aiohttp.ClientSession() as session:
                headers = self._get_headers()
                
                _LOGGER.info("STT API request to %s with %d bytes of audio", url, len(audio_data))
                
                # Whisper Large V3 Turbo requires base64-encoded audio in JSON
                if "whisper-large-v3-turbo" in model.lower():
                    import base64
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                    headers["Content-Type"] = "application/json"
                    payload = {"audio": audio_base64}
                    
                    async with session.post(
                        url, headers=headers, json=payload
                    ) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            _LOGGER.error(
                                "STT API error (status %s): %s", response.status, error_text
                            )
                            raise CloudflareAPIError(
                                f"STT request failed with status {response.status}: {error_text}"
                            )
                        
                        result = await response.json()
                        _LOGGER.info("STT response: %s", result)
                        
                        # Extract text from Whisper Large V3 Turbo response
                        text = None
                        if isinstance(result, dict) and "result" in result:
                            result_data = result["result"]
                            if isinstance(result_data, dict) and "text" in result_data:
                                text = result_data["text"]
                        
                        if text and isinstance(text, str) and text.strip():
                            _LOGGER.info("STT extracted text: %s", text)
                            return text.strip()
                        else:
                            _LOGGER.error("Could not extract text from STT response: %s", result)
                            raise CloudflareAPIError(f"No valid text in response: {result}")
                else:
                    # Standard models use raw audio bytes
                    headers["Content-Type"] = "application/octet-stream"
                    
                    async with session.post(
                        url, headers=headers, data=audio_data
                    ) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            _LOGGER.error(
                                "STT API error (status %s): %s", response.status, error_text
                            )
                            raise CloudflareAPIError(
                                f"STT request failed with status {response.status}: {error_text}"
                            )
                        
                        result = await response.json()
                        _LOGGER.info("STT response: %s", result)
                        
                        # Extract text from various response formats
                        text = None
                        if isinstance(result, dict):
                            if "result" in result:
                                result_data = result["result"]
                                if isinstance(result_data, dict):
                                    # Whisper format: {"text": "..."}
                                    if "text" in result_data:
                                        text = result_data["text"]
                                    # Whisper VTT format: {"vtt": "WEBVTT\n\n..."}
                                    elif "vtt" in result_data:
                                        vtt_text = result_data["vtt"]
                                        lines = vtt_text.split('\n')
                                        text_lines = [line for line in lines if line and not line.startswith('WEBVTT') and '-->' not in line]
                                        text = ' '.join(text_lines).strip()
                                    # Deepgram format: {"results": {"channels": [{"alternatives": [{"transcript": "..."}]}]}}
                                    elif "results" in result_data:
                                        try:
                                            channels = result_data["results"]["channels"]
                                            if channels and len(channels) > 0:
                                                alternatives = channels[0]["alternatives"]
                                                if alternatives and len(alternatives) > 0:
                                                    text = alternatives[0]["transcript"]
                                        except (KeyError, IndexError, TypeError) as e:
                                            _LOGGER.warning("Could not parse Deepgram response: %s", e)
                                elif isinstance(result_data, str):
                                    text = result_data
                            elif "text" in result:
                                text = result["text"]
                        
                        if text and isinstance(text, str) and text.strip():
                            _LOGGER.info("STT extracted text: %s", text)
                            return text.strip()
                        else:
                            _LOGGER.error("Could not extract text from STT response: %s", result)
                            raise CloudflareAPIError(f"No valid text in response: {result}")
        except CloudflareAPIError:
            raise
        except Exception as err:
            _LOGGER.exception("STT request failed with exception: %s", err)
            raise CloudflareAPIError(f"STT request failed: {err}") from err

    async def conversation(
        self, 
        model: str, 
        messages: list[dict[str, Any]], 
        max_tokens: int = 512,
        tools: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        """Send conversation request to LLM with optional function calling support."""
        url = f"{self.base_url}/{model}"
        payload = {"messages": messages, "max_tokens": max_tokens}
        
        # Add tools for function calling if provided
        if tools:
            payload["tools"] = tools

        try:
            async with aiohttp.ClientSession() as session:
                headers = self._get_headers()
                headers["Content-Type"] = "application/json"
                
                # Log full request details (redact API key)
                redacted_headers = {k: ("***REDACTED***" if k == "Authorization" else v) for k, v in headers.items()}
                _LOGGER.debug("LLM HTTP Request - URL: %s", url)
                _LOGGER.debug("LLM HTTP Request - Headers: %s", redacted_headers)
                _LOGGER.debug("LLM HTTP Request - Payload: %s", payload)
                _LOGGER.debug("LLM request to %s with %d tools", url, len(tools) if tools else 0)
                
                async with session.post(
                    url, headers=headers, json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        _LOGGER.error(
                            "LLM API error (status %s): %s", response.status, error_text
                        )
                        raise CloudflareAPIError(
                            f"LLM request failed with status {response.status}: {error_text}"
                        )
                    
                    result = await response.json()
                    _LOGGER.debug("LLM raw response: %s", result)
                    
                    # Log HTTP response details
                    _LOGGER.debug("LLM HTTP Response - Status: %s", response.status)
                    _LOGGER.debug("LLM HTTP Response - Full JSON: %s", result)
                    
                    # Return the full response for function calling support
                    if isinstance(result, dict) and "result" in result:
                        return result["result"]
                    
                    return result
        except CloudflareAPIError:
            raise
        except Exception as err:
            _LOGGER.error("LLM request failed: %s", err)
            raise CloudflareAPIError(f"LLM request failed: {err}") from err
