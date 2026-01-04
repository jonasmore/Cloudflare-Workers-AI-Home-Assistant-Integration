# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-04

### Added
- Initial release of Cloudflare Workers AI integration for Home Assistant
- Text-to-Speech (TTS) support with 4 models:
  - Deepgram Aura 2 English
  - Deepgram Aura 2 Spanish
  - Deepgram Aura 1 (Multi-language)
  - MyShell.ai MeloTTS (Multi-language)
- Speech-to-Text (STT) support with 4 models:
  - OpenAI Whisper
  - OpenAI Whisper Large V3 Turbo
  - OpenAI Whisper Tiny English
  - Deepgram Nova 3
- Conversation (LLM) support with 4 models (all with function calling):
  - Hermes 2 Pro Mistral 7B
  - Llama 4 Scout 17B
  - Llama 3.3 70B Fast
  - Mistral Small 3.1 24B
- Full device control via voice with 22 built-in tools:
  - Device control (turn on/off)
  - Light control (color, brightness)
  - Media control (play, pause, next, previous)
  - Volume control
  - Fan control
  - Vacuum control
  - Timer management
  - And more
- Natural language color interpretation ("set to the color of the sky")
- Area-based device control ("turn on all lights in the living room")
- Floor-based device control
- Domain filtering for targeted control (lights only, switches only, etc.)
- Configuration flow with model selection
- Full Home Assistant Assist pipeline integration
- Comprehensive debug logging for troubleshooting

### Technical Details
- Proper voluptuous schema parsing for Home Assistant intent system
- Correct parameter mapping for device control tools
- Enhanced system prompts for accurate entity name usage
- Comprehensive HTTP/LLM request/response logging
- Support for Cloudflare Workers AI function calling format

[0.1.0]: https://github.com/jonasmore/cloudflare-workers-ai-HA/releases/tag/v0.1.0
