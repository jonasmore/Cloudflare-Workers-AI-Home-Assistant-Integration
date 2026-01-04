# Quick Start Guide

Get up and running with Cloudflare Workers AI in 5 minutes!

## 1. Get Cloudflare Credentials (2 minutes)

1. Sign up at [cloudflare.com](https://cloudflare.com) (if you don't have an account)
2. Go to [API Tokens](https://dash.cloudflare.com/profile/api-tokens)
3. Click **Create Token** → Use "Edit Cloudflare Workers" template
4. Copy your **API Token** (save it somewhere safe!)
5. Get your **Account ID** from the dashboard URL or Workers & Pages section

## 2. Install via HACS (1 minute)

1. Open **HACS** → **Integrations**
2. Click **⋮** (three dots) → **Custom repositories**
3. Add: `https://github.com/jonasmore/cloudflare-workers-ai-HA`
4. Category: **Integration** → **Add**
5. Search "Cloudflare Workers AI" → **Download**
6. **Restart Home Assistant**

## 3. Configure Integration (1 minute)

1. **Settings** → **Devices & Services** → **+ Add Integration**
2. Search "Cloudflare Workers AI"
3. Enter your **Account ID** and **API Token**
4. Click **Submit**

## 4. Set Up Voice Assistant (1 minute)

1. **Settings** → **Voice Assistants** → **+ Add Assistant**
2. Configure:
   - **Conversation Agent**: Cloudflare Workers AI
   - **Speech-to-Text**: Cloudflare Workers AI STT
   - **Text-to-Speech**: Cloudflare Workers AI TTS
3. Click **Create**

## 5. Enable Device Control (30 seconds)

1. **Settings** → **Voice Assistants** → **Expose** tab
2. Select entities you want to control
3. In integration config, set **LLM Home Assistant API** to **"Assist"**
4. Choose a function calling model (Hermes 2 Pro recommended)

## 🎉 You're Done!

Try these commands:
- "What time is it?"
- "Turn on the kitchen light"
- "Set the living room to red"
- "Turn off all lights"

## Recommended Models

For best results:
- **TTS**: Deepgram Aura 2 English (clear, natural voice)
- **STT**: Whisper Large V3 Turbo (best accuracy)
- **LLM**: Hermes 2 Pro Mistral 7B (fast device control)

## Need Help?

- 📖 [Full Installation Guide](INSTALLATION.md)
- 📚 [Complete README](README.md)
- 🐛 [Report Issues](https://github.com/jonasmore/cloudflare-workers-ai-HA/issues)

---

**Enjoy your voice-controlled smart home!** 🏠🎤
