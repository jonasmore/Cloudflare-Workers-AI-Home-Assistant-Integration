# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-01-14

### Added
- **Dynamic TTS Voice Selection**: Choose from 40+ voices for Aura models
  - Aura 2 EN: 40 English voices (luna, mars, zeus, athena, and more)
  - Aura 2 ES: 10 Spanish voices (aquila, sirio, diana, and more)
  - Aura 1: 12 voices (angus, asteria, orion, and more)
- **TTS Language Selection**: Select language for MeloTTS (English, Spanish, French, Chinese, Japanese, Korean)
- **Real-time Conversation State Tracking**: Monitor exactly what your voice assistant is doing
  - Shows current processing stage (idle, processing, waiting for LLM, generating response)
  - Displays specific tool execution details (e.g., "executing: HassTurnOn on 'kitchen light' (1/2)")
  - Shows device/area/floor being controlled
  - Error state indication
- Configuration UI improvements with helpful descriptions and disclaimers
- Validation to prevent incompatible voice/language combinations
- Improved UI labels and descriptions for better user experience

### Fixed
- Conversation entity availability issue (removed incompatible `async_migrate_engine` call)
- Invalid voice/language selections are automatically reset to defaults
- Incompatible voice/language settings are cleaned up when switching models

### Technical Details
- Added `CONF_TTS_VOICE` and `CONF_TTS_LANGUAGE` configuration constants
- Implemented comprehensive voice and language mappings for all TTS models
- Enhanced conversation entity with state property and real-time updates
- Added validation logic in config flow to ensure data consistency
- Updated translation files with proper labels for all new options

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

[0.2.0]: https://github.com/jonasmore/cloudflare-workers-ai-HA/releases/tag/v0.2.0
[0.1.0]: https://github.com/jonasmore/cloudflare-workers-ai-HA/releases/tag/v0.1.0
