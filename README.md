# Cloudflare Workers AI for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]
[![hassfest][hassfest-shield]][hassfest]
[![validate][validate-shield]][validate]

[![downloads][downloads-shield]][downloads]
[![stars][stars-shield]][stars]
[![issues][issues-shield]][issues]

A comprehensive Home Assistant integration that brings Cloudflare Workers AI capabilities to your smart home, including Text-to-Speech, Speech-to-Text, and Conversation (LLM) with **full device control** for the Assist pipeline.

> **⚠️ Early Development Notice** 
> This integration is in early development. While core features are functional, you may encounter bugs or unexpected behavior. Please report any issues on [GitHub](https://github.com/jonasmore/Cloudflare-Workers-AI-Home-Assistant-Integration/issues). Feedback and contributions are welcome!

<p align="center">
  <img src="https://raw.githubusercontent.com/jonasmore/Cloudflare-Workers-AI-Home-Assistant-Integration/main/images/workers-x-ha.png" alt="Cloudflare Workers AI" width="50%">
</p>

## ✨ Features

- 🗣️ **Text-to-Speech (TTS)** - 4 high-quality voice models
- 🎤 **Speech-to-Text (STT)** - 4 advanced STT models
- 💬 **Conversation (LLM)** - 4 powerful language models with full device control
- 🎮 **Device Control** - Full Home Assistant device control via voice with 22 built-in tools
- 🎨 **Smart Color Control** - Natural language color changes ("set the light to the color of the sky")
- 🏠 **Area-Based Control** - Control all devices in a room at once
- ⚙️ **Easy Configuration** - Simple setup through Home Assistant UI

## 📋 Supported Models

### Text-to-Speech (4 Models)
| Model | Name | Language | Provider |
|-------|------|----------|----------|
| `@cf/deepgram/aura-2-en` | Aura 2 English | English | Deepgram |
| `@cf/deepgram/aura-2-es` | Aura 2 Spanish | Spanish | Deepgram |
| `@cf/deepgram/aura-1` | Aura 1 | Multi-language | Deepgram |
| `@cf/myshell-ai/melotts` | MeloTTS | Multi-language | MyShell.ai |

### Speech-to-Text (4 Models)
| Model | Name | Provider |
|-------|------|----------|
| `@cf/openai/whisper` | Whisper | OpenAI |
| `@cf/openai/whisper-large-v3-turbo` | Whisper Large V3 Turbo | OpenAI |
| `@cf/openai/whisper-tiny-en` | Whisper Tiny English | OpenAI |
| `@cf/deepgram/nova-3` | Deepgram Nova 3 | Deepgram |

### Conversation/LLM (4 Models - All with Function Calling)

All models support full device control via function calling:

| Model | Name | Parameters | Provider |
|-------|------|------------|----------|
| `@hf/nousresearch/hermes-2-pro-mistral-7b` | Hermes 2 Pro | 7B | NousResearch |
| `@cf/meta/llama-4-scout-17b-16e-instruct` | Llama 4 Scout | 17B (16 experts) | Meta |
| `@cf/meta/llama-3.3-70b-instruct-fp8-fast` | Llama 3.3 70B Fast | 70B | Meta |
| `@cf/mistralai/mistral-small-3.1-24b-instruct` | Mistral Small 3.1 | 24B | MistralAI |

## 📦 Prerequisites

Before installing this integration, you need:

1. **Cloudflare Account** - Sign up at [cloudflare.com](https://cloudflare.com)
2. **Workers AI Access** - Enable Workers AI in your Cloudflare account
3. **API Token** - Create an API token with Workers AI permissions:
   - Go to [Cloudflare Dashboard](https://dash.cloudflare.com/profile/api-tokens)
   - Click "Create Token"
   - Use "Edit Cloudflare Workers" template or create custom token
   - Ensure it has `Workers AI` permissions
4. **Account ID** - Found in your Cloudflare dashboard URL or account settings

## 🔧 Installation

### HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=jonasmore&repository=Cloudflare-Workers-AI-Home-Assistant-Integration&category=integration)

**Or manually:**

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/jonasmore/Cloudflare-Workers-AI-Home-Assistant-Integration`
6. Select category: "Integration"
7. Click "Add"
8. Find "Cloudflare Workers AI" in HACS
9. Click "Download"
10. Restart Home Assistant

### Manual Installation

1. Download the latest release from [GitHub Releases](https://github.com/jonasmore/Cloudflare-Workers-AI-Home-Assistant-Integration/releases)
2. Extract the `custom_components/cloudflare_workers_ai` folder
3. Copy it to your Home Assistant `config/custom_components` directory
4. Restart Home Assistant

## ⚙️ Configuration

### Initial Setup

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Cloudflare Workers AI"
4. Enter your credentials:
   - **Account ID**: Your Cloudflare account ID
   - **API Token**: Your Cloudflare API token
5. Click **Submit**

<p align="center">
  <img src="https://raw.githubusercontent.com/jonasmore/Cloudflare-Workers-AI-Home-Assistant-Integration/main/images/setup.png" alt="Setup Screenshot" width="60%">
</p>

### Model Selection

After initial setup, configure which models to use:

1. Go to **Settings** → **Devices & Services**
2. Find "Cloudflare Workers AI" integration
3. Click **Configure**
4. Select your preferred models:
   - **TTS Model**: Choose from 4 text-to-speech models
   - **STT Model**: Choose from 4 speech-to-text models
   - **LLM Model**: Choose from 4 conversation models (all with device control)
5. Click **Submit**

<p align="center">
  <img src="https://raw.githubusercontent.com/jonasmore/Cloudflare-Workers-AI-Home-Assistant-Integration/main/images/config.png" alt="Configuration Screenshot" width="60%">
</p>

### Create an Assist Pipeline

1. Go to **Settings** → **Voice Assistants** → **Assistants**
2. Click **+ Add Assistant** or edit an existing one
3. Configure the assistant:
   - **Name**: Give it a descriptive name (e.g., "Cloudflare AI Assistant")
   - **Language**: Select your preferred language
   - **Conversation agent**: Select "Cloudflare Workers AI"
   - **Speech-to-text**: Select "Cloudflare Workers AI STT"
   - **Text-to-speech**: Select "Cloudflare Workers AI TTS"
   - **Wake word**: Choose a wake word engine (optional)
4. Click **Create** to save your assistant

<p align="center">
  <img src="https://raw.githubusercontent.com/jonasmore/Cloudflare-Workers-AI-Home-Assistant-Integration/main/images/assist-pipeline.png" alt="Assist Pipeline" width="60%">
</p>

### Expose Entities for Voice Control

1. Go to **Settings** → **Voice Assistants** → **Expose**
2. Select the entities you want to control via voice:
   - Toggle switches, lights, and other devices
   - Choose specific entities or entire domains
3. Click **Save**

Now you can use voice commands like:
- "Turn on the kitchen light"
- "Set the table to red"
- "Turn off all lights in the living room"
- "Change the bedroom light to the color of the sky"
- "What's the temperature in the living room?"

## 🎯 Usage

### Text-to-Speech (TTS)

Use in automations or scripts:

```yaml
service: tts.speak
target:
  entity_id: tts.cloudflare_workers_ai_tts
data:
  message: "Hello, this is a test message"
  media_player_entity_id: media_player.living_room
```

### Speech-to-Text (STT)

Configure in the Assist pipeline:

1. Go to **Settings** → **Voice Assistants**
2. Click on your assistant or create a new one
3. Under **Speech-to-Text**, select "Cloudflare Workers AI STT"

### Conversation (LLM) with Device Control

Configure in the Assist pipeline:

1. Go to **Settings** → **Voice Assistants**
2. Click on your assistant or create a new one
3. Under **Conversation Agent**, select "Cloudflare Workers AI"


## 🎮 Device Control Examples

### Simple Device Control
```
"Turn on the kitchen light"
"Turn off the bedroom fan"
"Open the garage door"
```

### Color Control
```
"Set the table light to red"
"Change the living room to blue"
"Make the bedroom light the color of the sky"
```

### Area-Based Control
```
"Turn on all lights in the living room"
"Turn off everything in the kitchen"
"Set all lights upstairs to warm white"
```

### Advanced Control
```
"Set the living room light to 50% brightness"
"Turn on the TV in the bedroom"
"Play music in the kitchen"
```

## 🛠️ Available Tools (22 Total)

The integration provides 22 built-in tools for device control:

- **Device Control**: HassTurnOn, HassTurnOff
- **Light Control**: HassLightSet (color, brightness)
- **Media Control**: HassMediaUnpause, HassMediaPause, HassMediaNext, HassMediaPrevious
- **Volume Control**: HassSetVolume, HassSetVolumeRelative, HassMediaPlayerMute, HassMediaPlayerUnmute
- **Media Search**: HassMediaSearchAndPlay
- **Climate Control**: (via HassTurnOn/Off)
- **Fan Control**: HassFanSetSpeed
- **Vacuum Control**: HassVacuumStart, HassVacuumReturnToBase
- **Timer Control**: HassCancelAllTimers
- **Communication**: HassBroadcast
- **Lists**: HassListAddItem, HassListCompleteItem
- **Information**: GetDateTime, GetLiveContext, todo_get_items

## 🐛 Troubleshooting

### Connection Issues

**Error**: "Failed to connect to Cloudflare API"

**Solutions**:
- Verify your Account ID is correct
- Check that your API Token has Workers AI permissions
- Ensure your Cloudflare account has Workers AI enabled
- Check your internet connection

### Device Control Not Working

**Solutions**:
- Ensure **LLM Home Assistant API** is set to **"Assist"**
- Use a function calling model (Hermes 2 Pro, Llama 3.3, Llama 4 Scout, or Mistral Small)
- Verify entities are exposed in **Settings** → **Voice Assistants** → **Expose**
- Use exact device names as they appear in Home Assistant
- Check Home Assistant logs for detailed error messages

### STT Not Recognizing Speech

**Solutions**:
- Ensure audio format is supported (WAV, OGG)
- Check microphone quality and audio levels
- Try Whisper Large V3 Turbo for better accuracy
- Verify language settings match your speech

## 💡 Tips & Best Practices

1. **Entity Names**: Use simple, clear names for your devices (e.g., "kitchen light" instead of "kitchen_ceiling_light_1")
2. **Aliases**: Add aliases to entities for more natural voice commands
3. **Areas**: Organize devices into areas for area-based control
4. **Model Selection**: 
   - Use Hermes 2 Pro for fastest device control
   - Use Llama 3.3 70B for best accuracy
   - Use Whisper Large for best STT accuracy
5. **Expose Carefully**: Only expose entities you want to control via voice

## 📊 API Rate Limits

Cloudflare Workers AI has usage limits based on your plan:
- **Free Plan**: 10,000 neurons per day
- **Paid Plans**: Higher limits based on your subscription

Monitor your usage in the Cloudflare dashboard. For detailed pricing information, see the [Cloudflare Workers AI Pricing](https://developers.cloudflare.com/workers-ai/platform/pricing/).

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/jonasmore/Cloudflare-Workers-AI-Home-Assistant-Integration/issues)
- **Home Assistant Community**: [Community Forum](https://community.home-assistant.io/)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Cloudflare Workers AI](https://developers.cloudflare.com/workers-ai/) for providing the AI models
- [Home Assistant](https://www.home-assistant.io/) for the amazing smart home platform
- Inspired by [OpenAI Conversation](https://github.com/home-assistant/core/tree/dev/homeassistant/components/openai_conversation) and other LLM integrations


**Star ⭐ this repository if you find it useful!**

[releases-shield]: https://img.shields.io/github/release/jonasmore/Cloudflare-Workers-AI-Home-Assistant-Integration.svg?style=for-the-badge
[releases]: https://github.com/jonasmore/Cloudflare-Workers-AI-Home-Assistant-Integration/releases
[license-shield]: https://img.shields.io/github/license/jonasmore/Cloudflare-Workers-AI-Home-Assistant-Integration.svg?style=for-the-badge
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[hassfest-shield]: https://img.shields.io/github/actions/workflow/status/jonasmore/Cloudflare-Workers-AI-Home-Assistant-Integration/hassfest.yaml?style=for-the-badge&label=Hassfest
[hassfest]: https://github.com/jonasmore/Cloudflare-Workers-AI-Home-Assistant-Integration/actions/workflows/hassfest.yaml
[validate-shield]: https://img.shields.io/github/actions/workflow/status/jonasmore/Cloudflare-Workers-AI-Home-Assistant-Integration/validate.yaml?style=for-the-badge&label=HACS
[validate]: https://github.com/jonasmore/Cloudflare-Workers-AI-Home-Assistant-Integration/actions/workflows/validate.yaml
[downloads-shield]: https://img.shields.io/github/downloads/jonasmore/Cloudflare-Workers-AI-Home-Assistant-Integration/total.svg?style=for-the-badge
[downloads]: https://github.com/jonasmore/Cloudflare-Workers-AI-Home-Assistant-Integration/releases
[stars-shield]: https://img.shields.io/github/stars/jonasmore/Cloudflare-Workers-AI-Home-Assistant-Integration.svg?style=for-the-badge
[stars]: https://github.com/jonasmore/Cloudflare-Workers-AI-Home-Assistant-Integration/stargazers
[issues-shield]: https://img.shields.io/github/issues/jonasmore/Cloudflare-Workers-AI-Home-Assistant-Integration.svg?style=for-the-badge
[issues]: https://github.com/jonasmore/Cloudflare-Workers-AI-Home-Assistant-Integration/issues