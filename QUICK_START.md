# ⚡ Quick Start Guide - 10 Minutes Setup

**Bas 10 minutes mein bot deploy kar do! 🚀**

---

## **💳 1. Get API Keys (3 mins)**

### **Telegram Bot Token:**
```
Telegram → @BotFather
/newbot
Choose name + username
Copy token: 123456:ABC...XYZ
```

### **Claude API Key:**
```
https://console.anthropic.com/
Sign up/Login
API Keys → Create Key
Copy key: sk-ant-v0-...
```

---

## **📦 2. Clone Repository (1 min)**

```bash
git clone https://github.com/Stiphan680/advanced-ai-telegram-assistant.git
cd advanced-ai-telegram-assistant
```

---

## **📝 3. Setup Environment (2 mins)**

```bash
# Copy environment file
cp .env.example .env

# Edit .env mein paste karo:
# TELEGRAM_BOT_TOKEN=your_token
# CLAUDE_API_KEY=your_api_key
```

---

## **🚀 4. Deploy on Render (4 mins)**

### **Option A: Connect GitHub (Automatic)**
```
render.com → New Web Service
Select repository
Configure:
  - Build: pip install -r requirements.txt
  - Start: python bot.py
Add environment variables in Render dashboard
Deploy!
```

### **Option B: Manual Deploy (Advanced)**
```bash
# Local setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python bot.py
```

---

## **📋 5. Test Bot**

```
Telegram mein bot search karo
/start
Kuch question pocho
Bot respond karega!
```

---

## **📊 Features**

✅ Advanced AI responses (Claude 3.5)
✅ Memory system (yaad rakhta hai)
✅ Coding expertise
✅ Creative ideas
✅ Step-by-step training
✅ Unlimited words
✅ 24/7 availability (on Render)

---

## **📚 Full Docs**

- **README.md** - Complete overview
- **SETUP.md** - Detailed setup guide
- **ARCHITECTURE.md** - Technical details

---

## **📄 Channel Updates**

https://t.me/+UqvupdHeiCoxZGQ1

---

**Done! Bot live hai! 🎆**
