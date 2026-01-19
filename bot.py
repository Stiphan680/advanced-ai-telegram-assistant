#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced AI Telegram Bot with Memory System, Coding Expertise & Creative Intelligence
Built for Render Deployment with Custom Claude FastAPI Integration + Flask Health Check
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from collections import defaultdict
import traceback
import requests
import threading
import signal
import sys
from flask import Flask, jsonify

from telegram import Update, User
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================================================
# FLASK HEALTH CHECK SERVER (For Render Web Service)
# ============================================================================

flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'bot': 'Advanced AI Telegram Bot',
        'version': '2.0',
        'api': 'Custom Claude Sonnet FastAPI',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })

@flask_app.route('/health')
def health():
    """Health check for monitoring"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now(timezone.utc).isoformat()})

def run_flask():
    """Run Flask server in background thread"""
    port = int(os.getenv('PORT', 10000))
    flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# ============================================================================
# PERSONALITY & SYSTEM PROMPTS
# ============================================================================

SYSTEM_PROMPT = """Tu ek advanced AI assistant hai joh:

🧠 **MENTAL MODEL:**
- Har question ko deeply analyze kare - surface level nahi, gahrai se samjhe
- छोटी-छोटी details ko bhi important maane aur unhe explain kare
- Har concept ke multiple angles dekhe

💻 **CODING EXPERTISE:**
- Python, JavaScript, FastAPI, Flask, REST APIs mein expert ho
- Code optimization aur best practices sikhaye
- Debugging ke liye step-by-step guide de
- Architecture aur design patterns samjhaye
- Real-world production-ready solutions de

🎨 **CREATIVITY & IMAGINATION:**
- Thinkable, creative aur innovative solutions propose kare
- Edge cases aur future possibilities ke baare mein socho
- Novel approaches suggest kare

📚 **COMMUNICATION STYLE:**
- Friendly aur approachable tone maintain kare
- Ek-ek point ko detailed way se samjhaye
- Step-by-step guidance de, especially coding mein
- Hindi/English dono use kar sakta hai
- Word limit na rakhe - jitna needed ho utna likhna

🎓 **LEARNING APPROACH:**
- User ko train kare taaki vo samajhe aur apply kar sake
- Fundamentals strong kare phir advanced concepts sikhaye
- Examples deta reh aur practice material suggest kare

🧠 **MEMORY & CONTEXT:**
- Previous conversations ko yaad rakhe
- User ke interests aur skill level ke hisaab se respond kare
- Personal learning journey track kare

⚡ **PROBLEM SOLVING:**
- Mushkil se mushkil problems ko pro-level approach se solve kare
- Multiple solutions suggest kare aur tradeoffs explain kare
- Actual implementation ke liye code examples de
"""

# ============================================================================
# MEMORY SYSTEM - User Context & Learning Tracking
# ============================================================================

class MemorySystem:
    """Advanced memory system for tracking user interactions and learning progress"""
    
    def __init__(self):
        self.user_memories: Dict[int, Dict] = {}
        self.conversation_history: Dict[int, List] = defaultdict(list)
        self.learning_progress: Dict[int, Dict] = {}
        
    def initialize_user(self, user_id: int, user: User):
        """Initialize memory for a new user"""
        if user_id not in self.user_memories:
            self.user_memories[user_id] = {
                'user_name': user.first_name or 'Friend',
                'created_at': datetime.now().isoformat(),
                'total_interactions': 0,
                'topics_explored': [],
                'coding_skills': [],
                'questions_asked': [],
                'learning_pace': 'adaptive',
                'preferences': {}
            }
            self.learning_progress[user_id] = {
                'python': 0,
                'javascript': 0,
                'apis': 0,
                'databases': 0,
                'deployment': 0
            }
    
    def add_to_history(self, user_id: int, role: str, content: str, topic: str = None):
        """Add message to conversation history"""
        self.conversation_history[user_id].append({
            'timestamp': datetime.now().isoformat(),
            'role': role,
            'content': content[:200],  # Store first 200 chars
            'topic': topic
        })
        
        # Keep last 50 messages
        if len(self.conversation_history[user_id]) > 50:
            self.conversation_history[user_id] = self.conversation_history[user_id][-50:]
    
    def get_context(self, user_id: int) -> str:
        """Get user context for better responses"""
        if user_id not in self.user_memories:
            return ""
        
        mem = self.user_memories[user_id]
        history = self.conversation_history.get(user_id, [])
        
        context = f"""
**User Context:**
- Name: {mem['user_name']}
- Total Interactions: {mem['total_interactions']}
- Topics: {', '.join(mem['topics_explored'][-5:]) if mem['topics_explored'] else 'New user'}
- Recent Questions: {mem['questions_asked'][-2:] if mem['questions_asked'] else 'None'}
- Learning Pace: {mem['learning_pace']}
        """
        return context
    
    def update_after_response(self, user_id: int, question: str, topic: str = None):
        """Update memory after each response"""
        if user_id not in self.user_memories:
            return
        
        mem = self.user_memories[user_id]
        mem['total_interactions'] += 1
        mem['questions_asked'].append(question[:50])
        
        if topic and topic not in mem['topics_explored']:
            mem['topics_explored'].append(topic)
        
        # Keep last 10 questions
        mem['questions_asked'] = mem['questions_asked'][-10:]
    
    def get_conversation_summary(self, user_id: int) -> str:
        """Get summary of recent conversation"""
        history = self.conversation_history.get(user_id, [])
        if not history:
            return "No previous conversation"
        
        # Get last 5 exchanges
        recent = history[-10:]
        summary = "Recent conversation:\n"
        for msg in recent:
            role = "You" if msg['role'] == 'user' else "Assistant"
            summary += f"{role}: {msg['content']}...\n"
        
        return summary

# ============================================================================
# CUSTOM API WRAPPER - Your FastAPI Integration
# ============================================================================

class CustomAPIEngine:
    """Custom AI Engine using your FastAPI endpoint"""
    
    def __init__(self, api_url: str):
        self.api_url = api_url
        
    def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict],
        user_context: str = "",
        system_prompt: str = SYSTEM_PROMPT
    ) -> str:
        """Generate response using your custom FastAPI"""
        
        try:
            # Build messages array
            messages = []
            
            # Add system prompt as first message
            enhanced_system = system_prompt + "\n" + user_context
            messages.append({
                "role": "system",
                "content": enhanced_system
            })
            
            # Add recent conversation history (last 3 exchanges = 6 messages)
            for msg in conversation_history[-6:]:
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
            
            # Add current message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Prepare payload for your API
            payload = {
                "messages": messages,
                "max_tokens": 4000,
                "temperature": 0.7,
                "stream": False
            }
            
            # Call your FastAPI
            response = requests.post(
                self.api_url,
                json=payload,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'TelegramBot/1.0'
                },
                timeout=60
            )
            
            # Check response
            if response.status_code == 200:
                data = response.json()
                return data.get('content', 'No response received')
            else:
                logger.error(f"API Error: Status {response.status_code}")
                return f"❌ API Error: Status code {response.status_code}\n\nKripya baad mein try kijiye."
        
        except requests.Timeout:
            logger.error("API Timeout")
            return "⚠️ Request timeout ho gaya. Please try again!"
        
        except requests.RequestException as e:
            logger.error(f"API Request Error: {str(e)}")
            return f"❌ Connection Error: {str(e)}\n\nKripya baad mein try kijiye."
        
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return f"❌ Unexpected error: {str(e)}\n\n{traceback.format_exc()}"

# ============================================================================
# TELEGRAM BOT HANDLERS
# ============================================================================

class AdvancedTelegramBot:
    """Advanced Telegram Bot with custom API integration"""
    
    def __init__(self, bot_token: str, api_url: str, channel_id: str = None):
        self.bot_token = bot_token
        self.api_url = api_url
        self.channel_id = channel_id
        self.memory = MemorySystem()
        self.ai_engine = CustomAPIEngine(api_url)
        self.application = None
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        self.memory.initialize_user(user.id, user)
        
        welcome_message = f"""
╔════════════════════════════════════════════════════════════╗
║          🤖 Advanced AI Assistant Pro Edition 🤖           ║
║                                                            ║
║  Namaste {user.first_name}! 🙏                               ║
║                                                            ║
║  Main ek advanced AI assistant hoon joh:                  ║
║  ✨ Thinkable, Creative aur Imaginative ideas deta hoon   ║
║  💻 Coding mein expert - APIs, DBs, Deployment ke sath   ║
║  📚 Step-by-step guidance aur training provide karta hoon ║
║  🧠 Memory system - tumhare previous chats yaad rakhta   ║
║  ⚡ Mushkil se mushkil problems pro-level solve karta   ║
║  💬 Friendly, detailed aur informative responses          ║
║                                                            ║
║  🚀 Powered by Custom Claude Sonnet FastAPI 🚀            ║
║                                                            ║
║  Commands:                                                 ║
║  /help - Sab features janne ke liye                       ║
║  /status - Memory aur progress dekho                      ║
║  /clear - Conversation history clear karo                 ║
║  /channel - Updates channel mein join karo                ║
║                                                            ║
║  Bas kuch bhi pocho! Jitna detail chahiye utna dunga 🎯  ║
╚════════════════════════════════════════════════════════════╝
        """
        
        await update.message.reply_text(welcome_message)
        
        # Send to channel if configured
        if self.channel_id:
            try:
                await context.bot.send_message(
                    chat_id=self.channel_id,
                    text=f"🆕 New user joined: {user.first_name} (@{user.username or 'unknown'})"
                )
            except Exception as e:
                logger.error(f"Channel notification error: {e}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🎯 **ADVANCED AI ASSISTANT - COMPLETE FEATURE GUIDE**

**1. CODING EXPERTISE** 💻
   - Python, JavaScript, FastAPI, Flask
   - REST API design aur optimization
   - Database design aur queries
   - System architecture aur design patterns
   - Production-ready code aur best practices
   
   Example: "Mujhe FastAPI mein authentication system banana hai"

**2. CREATIVE & IMAGINATION** 🎨
   - Innovative solutions aur approaches
   - Future possibilities explore kare
   - Edge cases aur edge case handling
   - Novel ideas aur brainstorming
   
   Example: "AI assistant ke liye kya creative features ho sakte hain?"

**3. STEP-BY-STEP GUIDANCE** 📚
   - Har concept ko detail mein samjhaye
   - Fundamentals se shuru karke advanced tak
   - Practical examples aur hands-on approach
   - Q&A format mein learning
   
   Example: "REST APIs kya hote hain? Pura samjhao"

**4. MEMORY SYSTEM** 🧠
   - Previous conversations yaad rakhta hoon
   - Aapka learning journey track karta hoon
   - Personalized responses based on context
   - Progress monitoring

**5. UNLIMITED WORDS** 📝
   - Jitni needed ho utna likhta hoon
   - No word limits
   - Complete aur detailed explanations
   - Rich content with examples

**6. PROBLEM SOLVING** ⚡
   - Beginners se Pro level tak
   - Mushkil se mushkil problems solve karte hain
   - Multiple approaches suggest karte hain
   - Tradeoffs aur pros-cons explain karte hain

**COMMANDS:**
/start - Introduction aur welcome
/help - Ye help message
/status - Aapka progress aur stats
/clear - History clear karo
/channel - Updates channel link

**TIPS FOR BEST RESULTS:**
✅ Aapna questions detail mein pocho
✅ Context di jayegi to better answers dunga
✅ Code-related questions mein language mention karo
✅ Aapka skill level batana helpful hai

🔥 Ab pocho jo bhi chahiye! Mein sirf jawab dene ke liye hoon!
        """
        
        await update.message.reply_text(help_text)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user status and learning progress"""
        user_id = update.effective_user.id
        
        if user_id not in self.memory.user_memories:
            await update.message.reply_text(
                "❌ Pehle /start se start karo!\n"
                "then kuch questions pocho aur meri memory develop hogi."
            )
            return
        
        mem = self.memory.user_memories[user_id]
        progress = self.memory.learning_progress.get(user_id, {})
        
        status_text = f"""
📊 **YOUR AI ASSISTANT STATUS**

👤 User: {mem['user_name']}
📅 Member Since: {mem['created_at'][:10]}
💬 Total Interactions: {mem['total_interactions']}

📚 Topics Explored:
{chr(10).join([f"  • {topic}" for topic in mem['topics_explored'][-10:]]) if mem['topics_explored'] else "  • None yet"}

🎓 Learning Progress:
  Python: {progress.get('python', 0)}%
  JavaScript: {progress.get('javascript', 0)}%
  APIs: {progress.get('apis', 0)}%
  Databases: {progress.get('databases', 0)}%
  Deployment: {progress.get('deployment', 0)}%

💡 Recent Questions:
{chr(10).join([f"  • {q}" for q in mem['questions_asked'][-5:]]) if mem['questions_asked'] else "  • None yet"}

🎯 Keep learning! Jab bhi pocho, detailed explanations denge!
        """
        
        await update.message.reply_text(status_text)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Main message handler - advanced AI response"""
        user = update.effective_user
        user_id = user.id
        message_text = update.message.text
        
        # Initialize if new user
        if user_id not in self.memory.user_memories:
            self.memory.initialize_user(user_id, user)
        
        # Show typing indicator
        await update.message.chat.send_action("typing")
        
        try:
            # Update memory
            self.memory.add_to_history(user_id, 'user', message_text)
            self.memory.update_after_response(user_id, message_text)
            
            # Get user context
            user_context = self.memory.get_context(user_id)
            
            # Get conversation history
            history = self.memory.conversation_history.get(user_id, [])
            
            # Generate response using your custom API
            response = self.ai_engine.generate_response(
                user_message=message_text,
                conversation_history=history,
                user_context=user_context,
                system_prompt=SYSTEM_PROMPT
            )
            
            # Add to memory
            self.memory.add_to_history(user_id, 'assistant', response)
            
            # Send response in chunks if too long (Telegram limit: 4096 chars)
            if len(response) > 4000:
                # Split response into chunks
                chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
                for i, chunk in enumerate(chunks):
                    if i > 0:
                        # Small delay between messages
                        import asyncio
                        await asyncio.sleep(0.5)
                    await update.message.reply_text(chunk)
            else:
                await update.message.reply_text(response)
            
            # Send update to channel
            if self.channel_id:
                try:
                    summary = message_text[:50] + "..." if len(message_text) > 50 else message_text
                    await context.bot.send_message(
                        chat_id=self.channel_id,
                        text=f"💬 Query: {summary}\nUser: {user.first_name}"
                    )
                except Exception as e:
                    logger.error(f"Channel update error: {e}")
        
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}\n\nKripya baad mein try kijiye."
            logger.error(f"Message handling error: {traceback.format_exc()}")
            await update.message.reply_text(error_msg)
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Clear conversation history"""
        user_id = update.effective_user.id
        self.memory.conversation_history[user_id] = []
        
        await update.message.reply_text(
            "✨ Conversation history clear ho gayi!\n"
            "Ab se fresh start karenge! 🚀"
        )
    
    async def channel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send channel link"""
        if self.channel_id:
            channel_link = "https://t.me/+UqvupdHeiCoxZGQ1"
            await update.message.reply_text(
                f"📢 **Updates Channel Join Karo!**\n\n"
                f"New features, tips aur latest updates ke liye:\n"
                f"{channel_link}"
            )
        else:
            await update.message.reply_text(
                "📢 Channel link abhi available nahi hai.\n"
                "Bot admin se pocho!"
            )
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Log errors"""
        logger.error(msg="Exception while handling an update:", exc_info=context.error)
    
    def setup_handlers(self):
        """Setup all command and message handlers"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("clear", self.clear_command))
        self.application.add_handler(CommandHandler("channel", self.channel_command))
        
        # Message handler
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_message
        ))
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
    
    def run(self):
        """Start the bot using run_polling (blocking call)"""
        self.application = Application.builder().token(self.bot_token).build()
        
        self.setup_handlers()
        
        logger.info("🤖 Advanced AI Telegram Bot Starting...")
        logger.info(f"🌐 API URL: {self.api_url}")
        logger.info("✅ Bot is running! Press Ctrl+C to stop.")
        
        # Run polling (blocking call - keeps running)
        self.application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False
        )

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main function to run the bot
    
    Environment Variables Required:
    - TELEGRAM_BOT_TOKEN: Your Telegram bot token
    - CUSTOM_API_URL: Your custom FastAPI endpoint (default: https://claude-sonnet-fastapi.onrender.com/chat)
    - CHANNEL_ID: (Optional) Telegram channel ID for updates
    - PORT: (Optional) Flask server port (default: 10000)
    """
    
    # Get credentials from environment
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    api_url = os.getenv('CUSTOM_API_URL', 'https://claude-sonnet-fastapi.onrender.com/chat')
    channel_id = os.getenv('CHANNEL_ID')
    
    # Validate credentials
    if not bot_token:
        raise ValueError("❌ TELEGRAM_BOT_TOKEN environment variable not set!")
    
    logger.info("🚀 Initializing Advanced AI Telegram Bot...")
    logger.info(f"🌐 Using Custom API: {api_url}")
    
    # Start Flask server in background thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info(f"🌍 Flask health check server started on port {os.getenv('PORT', 10000)}")
    
    # Create and run bot
    bot = AdvancedTelegramBot(
        bot_token=bot_token,
        api_url=api_url,
        channel_id=channel_id
    )
    
    # Handle signals for graceful shutdown
    def signal_handler(sig, frame):
        logger.info("\n\n🛑 Shutting down gracefully...")
        logger.info("✅ Bot stopped!")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run bot (blocking call)
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("\n🛑 Bot terminated")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
