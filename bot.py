#!/usr/bin/env python3
"""
MEGA File Renamer Telegram Bot for Vercel
"""

import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from mega import Mega

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
APP_API_ID = int(os.getenv('APP_API_ID', '24737787'))
APP_API_HASH = os.getenv('APP_API_HASH', '4e939ca9653badf9a871ce57b0c7c246')
BOT_TOKEN = os.getenv('BOT_TOKEN', '8010019947:AAF-ZrgL-04gQAYO1Cn9oPnHXeK7sLk1Fnc')
BOT_USERNAME = os.getenv('BOT_USERNAME', '@NewBotGhost_bot')
OWNER_USERNAME = os.getenv('OWNER_USERNAME', '@Ghostkiller777')
MEGA_EMAIL = os.getenv('MEGA_EMAIL', 'sinegal816@lorkex.com')
MEGA_PASSWORD = os.getenv('MEGA_PASSWORD', 'Sajkwjnwi2872902unenbhdbnwj')

# Conversation states
EMAIL, PASSWORD, CONFIRM = range(3)

class MegaRenamerBot:
    def __init__(self):
        self.user_sessions = {}
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        user = update.effective_user
        await update.message.reply_text(
            f"🤖 **Welcome {user.first_name}!**\n\n"
            "I'm MEGA File Renamer Bot\n\n"
            "🔹 **Features:**\n"
            "• Rename ALL MEGA files to sam_1, sam_2, etc.\n"
            "• Preserve file extensions\n"
            "• Fast parallel processing\n\n"
            "⚠️ **Warning:** This is irreversible! Original filenames will be lost.\n\n"
            "Use /rename to start the process\n"
            "Use /help for instructions\n"
            "Use /cancel to stop any operation"
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command handler"""
        help_text = """
📖 **How to use this bot:**

1. **/start** - Begin interaction
2. **/rename** - Start MEGA file renaming process
3. **/status** - Check bot status
4. **/cancel** - Cancel current operation

🔧 **Process:**
- Bot will login to your MEGA account
- Scan all files and show count
- Ask for confirmation before renaming
- Rename ALL files sequentially
- Show progress and final report

⚠️ **Important:**
- Original filenames will be permanently lost
- File extensions are preserved
- Process cannot be undone
- Use test account first if possible
        """
        await update.message.reply_text(help_text)
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check bot status"""
        await update.message.reply_text(
            "🤖 **Bot Status:**\n\n"
            "✅ Bot is running normally\n"
            "🔹 Ready to rename MEGA files\n"
            f"🔹 Owner: {OWNER_USERNAME}\n"
            "Use /rename to start"
        )
    
    async def rename(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start rename process"""
        user_id = update.effective_user.id
        
        # Check if already in process
        if user_id in self.user_sessions:
            await update.message.reply_text("⚠️ You already have an operation in progress. Use /cancel to stop it.")
            return ConversationHandler.END
        
        await update.message.reply_text(
            "🔐 **MEGA File Renamer**\n\n"
            "I will rename ALL files in your MEGA account.\n\n"
            "⚠️ **This is irreversible!** Original filenames will be permanently lost.\n\n"
            "Do you want to continue? Type 'YES' to proceed or /cancel to abort:"
        )
        
        self.user_sessions[user_id] = {'step': 'awaiting_confirmation'}
        return CONFIRM
    
    async def confirm_operation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle operation confirmation"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_sessions:
            await update.message.reply_text("Session expired. Please use /rename to start again.")
            return ConversationHandler.END
        
        if update.message.text.upper() != 'YES':
            await update.message.reply_text("❌ Operation cancelled.")
            del self.user_sessions[user_id]
            return ConversationHandler.END
        
        # Start MEGA processing
        await update.message.reply_text("🔄 Logging into MEGA account...")
        
        try:
            # Initialize MEGA
            mega = Mega()
            m = mega.login(MEGA_EMAIL, MEGA_PASSWORD)
            
            await update.message.reply_text("✅ Login successful!\n📁 Scanning files...")
            
            # Get all files
            all_files = m.get_files()
            file_list = []
            
            for file_id, file_data in all_files.items():
                if isinstance(file_data, dict) and file_data.get('t') == 0:
                    if isinstance(file_data.get('a'), dict):
                        filename = file_data['a'].get('n')
                        if filename:
                            file_list.append({
                                'id': file_id,
                                'name': filename,
                                'data': file_data
                            })
            
            total_files = len(file_list)
            
            if total_files == 0:
                await update.message.reply_text("❌ No files found in your MEGA account.")
                del self.user_sessions[user_id]
                return ConversationHandler.END
            
            # Store in session
            self.user_sessions[user_id].update({
                'mega': m,
                'file_list': file_list,
                'total_files': total_files
            })
            
            await update.message.reply_text(
                f"📊 **Scan Complete!**\n\n"
                f"Found **{total_files}** files in your account\n\n"
                f"⚠️ **Final Warning:** This will rename ALL {total_files} files permanently!\n\n"
                f"Type 'CONFIRM' to start renaming or /cancel to abort:"
            )
            
            self.user_sessions[user_id]['step'] = 'awaiting_final_confirmation'
            return CONFIRM
            
        except Exception as e:
            await update.message.reply_text(f"❌ MEGA Error: {str(e)}")
            del self.user_sessions[user_id]
            return ConversationHandler.END
    
    async def start_renaming(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the actual renaming process"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_sessions:
            await update.message.reply_text("Session expired. Please use /rename to start again.")
            return ConversationHandler.END
        
        if update.message.text.upper() != 'CONFIRM':
            await update.message.reply_text("❌ Operation cancelled.")
            del self.user_sessions[user_id]
            return ConversationHandler.END
        
        session = self.user_sessions[user_id]
        m = session['mega']
        file_list = session['file_list']
        total_files = session['total_files']
        
        progress_msg = await update.message.reply_text("🔄 Starting rename process...\n0% completed")
        
        success_count = 0
        failed_count = 0
        failed_files = []
        
        # Rename files sequentially
        for index, file_info in enumerate(file_list, 1):
            try:
                old_name = file_info['name']
                
                # Preserve file extension
                if '.' in old_name:
                    ext = '.' + old_name.split('.')[-1]
                else:
                    ext = ''
                
                new_name = f"sam_{index}{ext}"
                
                # Rename file
                m.rename(file_info['data'], new_name)
                success_count += 1
                
                # Update progress every 10 files or 10%
                if index % 10 == 0 or index == total_files:
                    progress_percent = (index / total_files) * 100
                    await progress_msg.edit_text(
                        f"🔄 Renaming in progress...\n"
                        f"📊 {progress_percent:.1f}% completed\n"
                        f"✅ {success_count} successful\n"
                        f"❌ {failed_count} failed"
                    )
                
            except Exception as e:
                failed_count += 1
                failed_files.append((old_name, str(e)))
                logger.error(f"Failed to rename {old_name}: {e}")
        
        # Send final report
        report_text = (
            f"🎉 **Rename Complete!**\n\n"
            f"📊 **Summary:**\n"
            f"• Total files: {total_files}\n"
            f"• ✅ Successfully renamed: {success_count}\n"
            f"• ❌ Failed: {failed_count}\n"
            f"• 📈 Success rate: {(success_count/total_files)*100:.1f}%\n\n"
        )
        
        if failed_count > 0:
            report_text += f"⚠️ {failed_count} files failed to rename. Check logs for details.\n"
        
        report_text += "All files renamed to sam_1, sam_2, ..., sam_n format with original extensions preserved."
        
        await update.message.reply_text(report_text)
        
        # Cleanup
        del self.user_sessions[user_id]
        return ConversationHandler.END
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel any operation"""
        user_id = update.effective_user.id
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
        
        await update.message.reply_text("❌ Operation cancelled.")
        return ConversationHandler.END
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        try:
            await update.message.reply_text("❌ An error occurred. Please try again or contact admin.")
        except:
            pass

# Initialize bot
bot = MegaRenamerBot()

def setup_application():
    """Setup telegram application"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add conversation handler for rename process
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('rename', bot.rename)],
        states={
            CONFIRM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, bot.confirm_operation),
                MessageHandler(filters.TEXT & ~filters.COMMAND, bot.start_renaming)
            ]
        },
        fallbacks=[CommandHandler('cancel', bot.cancel)]
    )
    
    # Add handlers
    application.add_handler(CommandHandler('start', bot.start))
    application.add_handler(CommandHandler('help', bot.help_command))
    application.add_handler(CommandHandler('status', bot.status))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('cancel', bot.cancel))
    
    # Add error handler
    application.add_error_handler(bot.error_handler)
    
    return application

# Vercel serverless function handler
async def handler(request):
    """Vercel serverless function handler"""
    try:
        application = setup_application()
        
        # Initialize and start polling (for webhook in production)
        await application.initialize()
        await application.start()
        
        # Process update
        body = await request.json()
        update = Update.de_json(body, application.bot)
        await application.process_update(update)
        
        await application.stop()
        
        return {'statusCode': 200, 'body': 'OK'}
    
    except Exception as e:
        logger.error(f"Handler error: {e}")
        return {'statusCode': 500, 'body': 'Error'}

# For local testing
if __name__ == "__main__":
    async def main():
        application = setup_application()
        
        print("🤖 Bot is starting...")
        print(f"🔹 Bot Username: {BOT_USERNAME}")
        print(f"🔹 Owner: {OWNER_USERNAME}")
        print("🔹 Use /start to begin")
        
        await application.run_polling()
    
    asyncio.run(main())
