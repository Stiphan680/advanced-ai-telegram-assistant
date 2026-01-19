#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced AI Telegram Bot - GOOGLE GEMINI FREE VERSION
Koi cost nahi, 100% free, excellent performance!

Google Gemini API:
- Free tier: Generous limits
- Performance: 95% Claude level
- No credit card needed
- Unlimited free usage
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict
import traceback

from telegram import Update, User
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import google.generativeai as genai

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================================================
# PERSONALITY & SYSTEM PROMPTS
# ============================================================================

SYSTEM_PROMPT = """Tu ek advanced AI assistant hai joh:

🧠 **MENTAL MODEL:**
- Har question ko deeply analyze kare - surface level nahi, gahrai se samjhe
- छोटी-छोटी details ko bhi important maane aur unhe explain kare
- Har concept ke multiple angles dekhe
- Critical thinking aur deep reasoning use kare

💻 **CODING EXPERTISE:**
- Python, JavaScript, FastAPI, Flask, REST APIs mein expert
- Code optimization aur best practices sikhaye
- Debugging ke liye step-by-step guide de
- Architecture aur design patterns samjhaye
- Real-world production-ready solutions de
- Performance optimization techniques sikhaye

🎨 **CREATIVITY & IMAGINATION:**
- Thinkable, creative aur innovative solutions propose kare
- Edge cases aur future possibilities ke baare mein socho
- Novel approaches suggest kare
- "What if" scenarios explore kare

📚 **COMMUNICATION STYLE:**
- Friendly aur approachable tone maintain kare
- Ek-ek point ko detailed way se samjhaye
- Step-by-step guidance de, especially coding mein
- Hindi/English dono use kar sakta hai
- Word limit na rakhe - jitna needed ho utna likhna
- Agar complex topic ho to examples de

🎓 **LEARNING APPROACH:**
- User ko train kare taaki vo samajhe aur apply kar sake
- Fundamentals strong kare phir advanced concepts sikhaye
- Examples deta reh aur practice material suggest kare
- Common mistakes highlight kare
- Best practices emphasize kare

🧠 **MEMORY & CONTEXT:**
- Previous conversations ko yaad rakhe
- User ke interests aur skill level ke hisaab se respond kare
- Personal learning journey track kare
- Progress acknowledge kare

⚡ **PROBLEM SOLVING:**
- Mushkil se mushkil problems ko pro-level approach se solve kare
- Multiple solutions suggest kare aur tradeoffs explain kare
- Actual implementation ke liye code examples de
- Edge cases consider kare
- Performance implications discuss kare

💡 **TONE:**
- Enthusiastic aur motivating
- Patient aur non-judgmental
- Confident par humble
- Whenever possible, encourage independent thinking

Tu ALWAYS helpful, honest, aur informative be. Kabi bhi misinformation mat de.
"""

# ============================================================================
# MEMORY SYSTEM - User Context & Learning Tracking
# ============================================================================

class MemorySystem:
    """Advanced memory system for tracking user interactions"""
    
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
                'questions_asked': [],
                'learning_pace': 'adaptive',
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
            'content': content[:300] if len(content) > 300 else content,
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
        
        context = f"""
**User Context:**
- Name: {mem['user_name']}
- Total Interactions: {mem['total_interactions']}
- Topics: {', '.join(mem['topics_explored'][-5:]) if mem['topics_explored'] else 'New user'}
- Recent Questions: {mem['questions_asked'][-2:] if mem['questions_asked'] else 'None'}
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
        
        mem['questions_asked'] = mem['questions_asked'][-10:]

# ============================================================================
# GOOGLE GEMINI AI ENGINE - 100% FREE
# ============================================================================

class GeminiAIEngine:
    """Advanced AI Engine using Google Gemini (FREE TIER)"""
    
    def __init__(self, api_key: str):
        """Initialize Gemini API"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        logger.info(f"✅ Gemini AI Engine initialized (FREE)")
    
    def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict],
        user_context: str = "",
        system_prompt: str = SYSTEM_PROMPT
    ) -> str:
        """Generate response using Google Gemini"""
        
        try:
            # Build conversation context
            context_messages = []
            
            # Add system prompt
            context_messages.append(f"System Instructions:\n{system_prompt}\n")
            
            # Add user context
            if user_context:
                context_messages.append(f"User Background:\n{user_context}\n")
            
            # Add recent conversation history (last 3 exchanges)
            for msg in conversation_history[-6:]:
                role_text = "User" if msg['role'] == 'user' else "Assistant"
                context_messages.append(f"{role_text}: {msg['content']}")
            
            # Add current message
            context_messages.append(f"User: {user_message}")
            
            # Combine all context
            full_prompt = "\n".join(context_messages)
            
            # Call Gemini API
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=2048,
                    temperature=0.7,
                )
            )
            
            return response.text if response.text else "Maaf kijiye, response generate nahi ho saka."
        
        except Exception as e:
            logger.error(f"Gemini API Error: {str(e)}")
            return f"❌ Error: {str(e)}\n\nKripya baad mein try kijiye. Agar issue persist kare to API key check karo."

# ============================================================================
# TELEGRAM BOT HANDLERS
# ============================================================================

class AdvancedTelegramBot:
    """Advanced Telegram Bot with Gemini AI"""
    
    def __init__(self, bot_token: str, gemini_key: str, channel_id: str = None):
        self.bot_token = bot_token
        self.gemini_key = gemini_key
        self.channel_id = channel_id
        self.memory = MemorySystem()
        self.ai_engine = GeminiAIEngine(gemini_key)
        self.application = None
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        self.memory.initialize_user(user.id, user)
        
        welcome_message = f"""
╔════════════════════════════════════════════════╗
║   🤖 Advanced AI Assistant (Google Gemini)    ║
║         100% FREE - No Cost Needed!           ║
║                                                ║
║  Namaste {user.first_name}! 🙏                      ║
║                                                ║
║  Main ek advanced AI assistant hoon joh:      ║
║  ✨ Thinkable, Creative aur Imaginative       ║
║  💻 Coding mein expert (APIs, DBs, Deploy)    ║
║  📚 Step-by-step guidance provide karta       ║
║  🧠 Aapke chats yaad rakhta hoon               ║
║  ⚡ Mushkil problems pro-level solve karta    ║
║  💬 Friendly aur detailed responses            ║
║  ♾️  Word limit nahi - utna likhta utna       ║
║                                                ║
║  Commands:                                     ║
║  /help - Sab features janne ke liye           ║
║  /status - Aapka progress dekho               ║
║  /clear - Chat history clear karo             ║
║                                                ║
║  Bas kuch bhi pocho! Google Gemini FREE se    ║
║  powered responses dunga 🚀                    ║
║                                                ║
╚════════════════════════════════════════════════╝
        """
        
        await update.message.reply_text(welcome_message)
        logger.info(f"New user: {user.first_name} (@{user.username or 'unknown'})")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🎓 **ADVANCED AI ASSISTANT - COMPLETE GUIDE**

**1. CODING EXPERTISE** 💻
   - Python, JavaScript, FastAPI, Flask
   - REST API design aur optimization
   - Database design aur queries
   - System architecture patterns
   - Production-ready code examples

**2. CREATIVE & IMAGINATIVE** 🎨
   - Innovative solutions suggest karte hain
   - Edge cases explore karte hain
   - Novel ideas propose karte hain

**3. STEP-BY-STEP GUIDANCE** 📚
   - Har concept ko detail mein samjhaye
   - Beginner se advanced tak
   - Practical examples
   - Q&A format mein learning

**4. MEMORY SYSTEM** 🧠
   - Previous conversations yaad rakhta hoon
   - Aapka learning journey track karta hoon
   - Personalized responses

**5. UNLIMITED WORDS** 📝
   - Jitni needed ho utna likhta hoon
   - Complete explanations
   - Rich examples aur code

**6. PROBLEM SOLVING** ⚡
   - Beginner se Pro level tak
   - Mushkil problems solve karte hain
   - Multiple approaches
   - Tradeoffs explain karte hain

**POWERED BY:** Google Gemini (100% FREE)
**No API costs, no premium needed!**

**TIPS:**
✅ Detail mein question pocho
✅ Context dijiye
✅ Skill level batao
✅ Multiple attempts karo clarity ke liye

🔥 Ab pocho jo bhi chahiye! Mein sirf jawab dene ke liye hoon!
        """
        
        await update.message.reply_text(help_text)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user status"""
        user_id = update.effective_user.id
        
        if user_id not in self.memory.user_memories:
            await update.message.reply_text(
                "❌ Pehle /start se start karo!\n"
                "Phir kuch questions pocho aur meri memory develop hogi."
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

💡 Keep learning! Jab bhi pocho, detailed explanations dunga!
        """
        
        await update.message.reply_text(status_text)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Main message handler"""
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
            
            # Generate response using Gemini
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
                chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
                for i, chunk in enumerate(chunks):
                    if i > 0:
                        import asyncio
                        await asyncio.sleep(0.5)
                    await update.message.reply_text(chunk, parse_mode='Markdown')
            else:
                await update.message.reply_text(response, parse_mode='Markdown')
            
            logger.info(f"Response sent to {user.first_name}")
        
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}\n\nKripya baad mein try kijiye."
            logger.error(f"Message handling error: {traceback.format_exc()}")
            await update.message.reply_text(error_msg)
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Clear conversation history"""
        user_id = update.effective_user.id
        self.memory.conversation_history[user_id] = []
        
        await update.message.reply_text(
            "✨ Chat history clear ho gayi!\n"
            "Ab se fresh start karenge! 🚀"
        )
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Log errors"""
        logger.error(msg="Exception while handling an update:", exc_info=context.error)
    
    def setup_handlers(self):
        """Setup all handlers"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("clear", self.clear_command))
        
        # Message handler
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_message
        ))
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
    
    async def run(self):
        """Start the bot"""
        self.application = Application.builder().token(self.bot_token).build()
        
        self.setup_handlers()
        
        logger.info("🤖 Advanced AI Telegram Bot (Google Gemini FREE) Starting...")
        
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(
            allowed_updates=None,
            drop_pending_updates=True
        )
        
        logger.info("✅ Bot is running! Press Ctrl+C to stop.")
    
    async def stop(self):
        """Stop bot gracefully"""
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """
    Main function to run the bot
    
    Environment Variables Required:
    - TELEGRAM_BOT_TOKEN: Your Telegram bot token
    - GOOGLE_GEMINI_API_KEY: Your Google Gemini API key (FREE!)
    
    Get Google Gemini API Key (FREE):
    1. Go to: https://makersuite.google.com/app/apikey
    2. Click "Create API Key"
    3. Copy the key
    4. Set in environment: export GOOGLE_GEMINI_API_KEY=your_key
    """
    
    # Get credentials from environment
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    gemini_key = os.getenv('GOOGLE_GEMINI_API_KEY')
    channel_id = os.getenv('CHANNEL_ID')
    
    # Validate credentials
    if not bot_token:
        raise ValueError("❌ TELEGRAM_BOT_TOKEN environment variable not set!")
    if not gemini_key:
        raise ValueError("❌ GOOGLE_GEMINI_API_KEY environment variable not set!\n"
                        "Get FREE key at: https://makersuite.google.com/app/apikey")
    
    logger.info("🚀 Initializing Advanced AI Telegram Bot (Google Gemini FREE)...")
    logger.info("💰 No API costs, 100% FREE!") 
    
    # Create and run bot
    bot = AdvancedTelegramBot(
        bot_token=bot_token,
        gemini_key=gemini_key,
        channel_id=channel_id
    )
    
    try:
        await bot.run()
    except KeyboardInterrupt:
        logger.info("\n\n🛑 Shutting down gracefully...")
        await bot.stop()
        logger.info("✅ Bot stopped!")

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot terminated")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        print(traceback.format_exc())
