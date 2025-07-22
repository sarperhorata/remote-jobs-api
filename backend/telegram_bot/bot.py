import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, ContextTypes, filters

# Get configuration from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ENABLED = bool(TELEGRAM_BOT_TOKEN)

# Setup logger
logger = logging.getLogger(__name__)

# Import models with proper path
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from models.models import UserProfile, UserProfileCreate, UserProfileUpdate, WorkType, JobType, WorkHours, UserNotificationPreference
except ImportError:
    # Fallback for when imports are not available
    logger.warning("Could not import models, some features will be limited")
    UserProfile = None
    UserProfileCreate = None 
    UserProfileUpdate = None
    WorkType = None
    JobType = None
    WorkHours = None
    UserNotificationPreference = None

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Conversation states
(
    PROFILE_MENU,
    FIRST_NAME, 
    LAST_NAME, 
    EMAIL, 
    PHONE, 
    LOCATION,
    BIO,
    WORK_PREFERENCES, 
    WORK_TYPE, 
    JOB_TYPE,
    SKILL_NAME,
    SKILL_LEVEL,
    SKILL_EXPERIENCE,
    ADD_MORE_SKILLS,
) = range(14)

class RemoteJobsBot:
    """
    Telegram bot implementation for Remote Jobs Monitor
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RemoteJobsBot, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the bot with token"""
        if self._initialized:
            return
            
        if not TELEGRAM_ENABLED:
            logger.warning("Telegram bot is disabled. Set TELEGRAM_BOT_TOKEN environment variable to enable it.")
            self.enabled = False
            self.application = None
            self._initialized = True
            return
            
        self.token = TELEGRAM_BOT_TOKEN
        self.enabled = True
        try:
            self.application = Application.builder().token(self.token).build()
            self.setup_handlers()
            logger.info("Telegram bot initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {str(e)}")
            self.enabled = False
            self.application = None
        
        self._initialized = True
        
    def setup_handlers(self):
        """Setup all command and message handlers"""
        # Skip if bot is disabled
        if not self.enabled or not self.application:
            return
            
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("jobs", self.jobs))
        self.application.add_handler(CommandHandler("subscribe", self.subscribe))
        
        # Profile conversation handler
        profile_conv_handler = ConversationHandler(
            entry_points=[CommandHandler("profile", self.profile_start)],
            states={
                PROFILE_MENU: [
                    CallbackQueryHandler(self.create_profile, pattern="^create_profile$"),
                    CallbackQueryHandler(self.show_profile, pattern="^show_profile$"),
                    CallbackQueryHandler(self.edit_profile, pattern="^edit_profile$"),
                    CallbackQueryHandler(self.cancel_profile, pattern="^cancel$"),
                ],
                FIRST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_first_name)],
                LAST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_last_name)],
                EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_email)],
                PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_phone)],
                LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_location)],
                BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_bio)],
                WORK_PREFERENCES: [
                    CallbackQueryHandler(self.get_work_preferences, pattern="^set_work_preferences$"),
                    CallbackQueryHandler(self.skip_work_preferences, pattern="^skip_work_preferences$"),
                ],
                WORK_TYPE: [
                    CallbackQueryHandler(self.get_work_type_remote, pattern="^remote$"),
                    CallbackQueryHandler(self.get_work_type_hybrid, pattern="^hybrid$"),
                    CallbackQueryHandler(self.get_work_type_office, pattern="^office$"),
                    CallbackQueryHandler(self.get_work_type_any, pattern="^any$"),
                ],
                JOB_TYPE: [
                    CallbackQueryHandler(self.get_job_type_full_time, pattern="^full_time$"),
                    CallbackQueryHandler(self.get_job_type_part_time, pattern="^part_time$"),
                    CallbackQueryHandler(self.get_job_type_contract, pattern="^contract$"),
                    CallbackQueryHandler(self.get_job_type_freelance, pattern="^freelance$"),
                    CallbackQueryHandler(self.get_job_type_internship, pattern="^internship$"),
                    CallbackQueryHandler(self.get_job_type_any, pattern="^any$"),
                ],
                SKILL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_skill_name)],
                SKILL_LEVEL: [
                    CallbackQueryHandler(self.get_skill_level, pattern="^(beginner|intermediate|advanced|expert)$"),
                ],
                SKILL_EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_skill_experience)],
                ADD_MORE_SKILLS: [
                    CallbackQueryHandler(self.add_more_skills, pattern="^add_more_skills$"),
                    CallbackQueryHandler(self.finish_skills, pattern="^finish_skills$"),
                ],
            },
            fallbacks=[CommandHandler("cancel", self.cancel_profile)],
        )
        self.application.add_handler(profile_conv_handler)
        
        # Default handler for unknown commands
        self.application.add_handler(MessageHandler(filters.COMMAND, self.unknown_command))
        
        # Default handler for non-command messages
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send welcome message when command /start is issued."""
        user = update.effective_user
        await update.message.reply_html(
            f"Merhaba {user.mention_html()}! 🐝\n\n"
            f"<b>Buzz2Remote Bot'a Hoş Geldiniz!</b> 🚀\n\n"
            f"Remote iş fırsatlarını bulmanıza ve profilinize uygun yeni işler olduğunda sizi bilgilendirmeme yardımcı oluyorum.\n\n"
            f"📋 <b>Mevcut Komutlar:</b>\n"
            f"• /start - Bu karşılama mesajını göster\n"
            f"• /help - Yardım bilgilerini göster\n"
            f"• /jobs - En son iş ilanlarını al\n"
            f"• /subscribe - İş uyarılarına abone ol\n"
            f"• /profile - Profilinizi yönetin\n\n"
            f"🎯 Hadi başlayalım! #Buzz2Remote #RemoteJobs"
        )
        
        # Check if user already has a profile
        user_profile = await self.get_user_profile(user.id)
        
        if not user_profile:
            await update.message.reply_text(
                "It looks like you don't have a profile yet. Would you like to create one?",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Create Profile", callback_data="create_profile")]
                ])
            )
        else:
            # User already has a profile
            await update.message.reply_text(
                f"Welcome back, {user_profile.first_name}! What would you like to do today?",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("View Profile", callback_data="show_profile")],
                    [InlineKeyboardButton("Edit Profile", callback_data="edit_profile")],
                    [InlineKeyboardButton("Browse Jobs", callback_data="browse_jobs")],
                ])
            )
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send help message when command /help is issued."""
        await update.message.reply_html(
            "🐝 <b>Buzz2Remote Bot Yardım</b> 🐝\n\n"
            "📋 <b>Kullanabileceğiniz Komutlar:</b>\n\n"
            "🚀 <b>/start</b> - Botu başlat\n"
            "👤 <b>/profile</b> - Profilinizi oluşturun veya güncelleyin\n"
            "💼 <b>/jobs</b> - Mevcut işleri görüntüleyin\n"
            "🔔 <b>/subscribe</b> - İş uyarılarına abone olun\n"
            "❓ <b>/help</b> - Bu yardım mesajını göster\n\n"
            "🎯 <b>Özellikler:</b>\n"
            "• Remote iş fırsatlarını keşfedin\n"
            "• Profilinize uygun işleri bulun\n"
            "• Yeni iş ilanlarından haberdar olun\n"
            "• Profilinizi yönetin\n\n"
            "💡 <b>İpucu:</b> İlk kez kullanıyorsanız /profile komutu ile profilinizi oluşturun!\n\n"
            "#Buzz2Remote #Help #RemoteJobs"
        )
    
    async def jobs(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /jobs command to browse jobs."""
        # Check if user has a profile
        user = update.effective_user
        user_profile = await self.get_user_profile(user.id)
        
        if not user_profile:
            await update.message.reply_text(
                "You need to create a profile first to browse jobs that match your preferences.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Create Profile", callback_data="create_profile")]
                ])
            )
            return
        
        # For now, just show a placeholder
        await update.message.reply_html(
            "🔍 <b>İş Arama Seçenekleri:</b>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 Tüm İşleri Görüntüle", callback_data="browse_all_jobs")],
                [InlineKeyboardButton("🎯 Uygun İşleri Görüntüle", callback_data="browse_matching_jobs")],
                [InlineKeyboardButton("🔎 İş Ara", callback_data="search_jobs")],
            ])
        )
    
    async def subscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /subscribe command to set up job alerts."""
        # Check if user has a profile
        user = update.effective_user
        user_profile = await self.get_user_profile(user.id)
        
        if not user_profile:
            await update.message.reply_text(
                "You need to create a profile first to subscribe to job alerts.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Create Profile", callback_data="create_profile")]
                ])
            )
            return
        
        # For now, just show subscription options
        await update.message.reply_html(
            "📣 <b>Abonelik Seçenekleri:</b>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📅 Günlük Uyarılar", callback_data="subscribe_daily")],
                [InlineKeyboardButton("📊 Haftalık Özet", callback_data="subscribe_weekly")],
                [InlineKeyboardButton("⚡ Gerçek Zamanlı Uyarılar (Premium)", callback_data="subscribe_realtime")],
                [InlineKeyboardButton("🚫 Aboneliği İptal Et", callback_data="unsubscribe")],
            ])
        )
    
    async def profile_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the profile conversation."""
        user = update.effective_user
        user_profile = await self.get_user_profile(user.id)
        
        buttons = []
        
        if user_profile:
            buttons.extend([
                [InlineKeyboardButton("👁️ Profili Görüntüle", callback_data="show_profile")],
                [InlineKeyboardButton("✏️ Profili Düzenle", callback_data="edit_profile")],
            ])
        else:
            buttons.append([InlineKeyboardButton("➕ Profil Oluştur", callback_data="create_profile")])
        
        buttons.append([InlineKeyboardButton("❌ İptal", callback_data="cancel")])
        
        await update.message.reply_html(
            "👤 <b>Profil Yönetimi:</b>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        
        return PROFILE_MENU
    
    async def create_profile(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle the creation of a new user profile."""
        query = update.callback_query
        await query.answer()
        
        # Initialize user data for profile creation
        context.user_data["profile"] = {}
        
        await query.edit_message_text(
            "Let's create your profile. This will help us find the best jobs for you.\n\n"
            "What is your first name?"
        )
        
        return FIRST_NAME
    
    async def get_first_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Get the user's first name."""
        first_name = update.message.text
        context.user_data["profile"]["first_name"] = first_name
        
        await update.message.reply_text(
            f"Nice to meet you, {first_name}! What is your last name?"
        )
        
        return LAST_NAME
    
    async def get_last_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Get the user's last name."""
        last_name = update.message.text
        context.user_data["profile"]["last_name"] = last_name
        
        await update.message.reply_text(
            "What is your email address? We'll use this for job alerts."
        )
        
        return EMAIL
    
    async def get_email(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Get the user's email address."""
        email = update.message.text
        context.user_data["profile"]["email"] = email
        
        # TODO: Validate email format
        
        await update.message.reply_text(
            "What is your phone number? (You can send /skip if you prefer not to share)",
            reply_markup=ReplyKeyboardMarkup([["/skip"]], one_time_keyboard=True)
        )
        
        return PHONE
    
    async def get_phone(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Get the user's phone number."""
        if update.message.text == "/skip":
            await update.message.reply_text(
                "No problem! Let's move on.",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            phone = update.message.text
            context.user_data["profile"]["phone"] = phone
            await update.message.reply_text(
                "Phone number saved!",
                reply_markup=ReplyKeyboardRemove()
            )
        
        await update.message.reply_text(
            "Where are you located? Please provide your city and country (e.g., 'Istanbul, Turkey')"
        )
        
        return LOCATION
    
    async def get_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Get the user's location."""
        location = update.message.text
        
        try:
            city, country = location.split(",", 1)
            context.user_data["profile"]["city"] = city.strip()
            context.user_data["profile"]["country"] = country.strip()
        except ValueError:
            # If the user didn't use a comma, save the entire text as city
            context.user_data["profile"]["city"] = location
            context.user_data["profile"]["country"] = None
        
        await update.message.reply_text(
            "Tell me a bit about yourself and your professional background (you can send /skip if you prefer):",
            reply_markup=ReplyKeyboardMarkup([["/skip"]], one_time_keyboard=True)
        )
        
        return BIO
    
    async def get_bio(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Get the user's bio."""
        if update.message.text == "/skip":
            await update.message.reply_text(
                "No problem! Let's move on.",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            bio = update.message.text
            context.user_data["profile"]["bio"] = bio
            await update.message.reply_text(
                "Bio saved!",
                reply_markup=ReplyKeyboardRemove()
            )
        
        await update.message.reply_text(
            "Would you like to set your work preferences now?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Set Preferences", callback_data="set_work_preferences")],
                [InlineKeyboardButton("Skip for Now", callback_data="skip_work_preferences")],
            ])
        )
        
        return WORK_PREFERENCES
    
    async def get_work_preferences(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start setting work preferences."""
        query = update.callback_query
        await query.answer()
        
        # Initialize work preferences data
        if "work_preferences" not in context.user_data["profile"]:
            context.user_data["profile"]["work_preferences"] = {}
        
        await query.edit_message_text(
            "What type of work arrangement do you prefer?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Remote", callback_data="remote")],
                [InlineKeyboardButton("Hybrid", callback_data="hybrid")],
                [InlineKeyboardButton("Office", callback_data="office")],
                [InlineKeyboardButton("Any", callback_data="any")],
            ])
        )
        
        return WORK_TYPE
    
    async def get_work_type_remote(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Set work type to remote."""
        return await self._set_work_type(update, context, WorkType.REMOTE)
    
    async def get_work_type_hybrid(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Set work type to hybrid."""
        return await self._set_work_type(update, context, WorkType.HYBRID)
    
    async def get_work_type_office(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Set work type to office."""
        return await self._set_work_type(update, context, WorkType.OFFICE)
    
    async def get_work_type_any(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Set work type to any."""
        return await self._set_work_type(update, context, WorkType.ANY)
    
    async def _set_work_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE, work_type: WorkType) -> int:
        """Helper method to set work type and proceed to next question."""
        query = update.callback_query
        await query.answer()
        
        context.user_data["profile"]["work_preferences"]["work_type"] = work_type
        
        await query.edit_message_text(
            "What type of job are you looking for?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Full-time", callback_data="full_time")],
                [InlineKeyboardButton("Part-time", callback_data="part_time")],
                [InlineKeyboardButton("Contract", callback_data="contract")],
                [InlineKeyboardButton("Freelance", callback_data="freelance")],
                [InlineKeyboardButton("Internship", callback_data="internship")],
                [InlineKeyboardButton("Any", callback_data="any")],
            ])
        )
        
        return JOB_TYPE
    
    async def get_job_type_full_time(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Set job type to full time."""
        return await self._set_job_type(update, context, JobType.FULL_TIME)
    
    async def get_job_type_part_time(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Set job type to part time."""
        return await self._set_job_type(update, context, JobType.PART_TIME)
    
    async def get_job_type_contract(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Set job type to contract."""
        return await self._set_job_type(update, context, JobType.CONTRACT)
    
    async def get_job_type_freelance(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Set job type to freelance."""
        return await self._set_job_type(update, context, JobType.FREELANCE)
    
    async def get_job_type_internship(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Set job type to internship."""
        return await self._set_job_type(update, context, JobType.INTERNSHIP)
    
    async def get_job_type_any(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Set job type to any."""
        return await self._set_job_type(update, context, JobType.ANY)
    
    async def _set_job_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE, job_type: JobType) -> int:
        """Helper method to set job type and proceed to skills."""
        query = update.callback_query
        await query.answer()
        
        context.user_data["profile"]["work_preferences"]["job_type"] = job_type
        
        # Initialize skills array
        if "skills" not in context.user_data["profile"]:
            context.user_data["profile"]["skills"] = []
        
        await query.edit_message_text(
            "Great! Now let's add some skills to your profile.\n\n"
            "What's your top skill? (e.g., 'Python', 'JavaScript', 'Project Management')"
        )
        
        return SKILL_NAME
    
    async def get_skill_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Get the name of a skill."""
        skill_name = update.message.text
        
        # Save the skill name temporarily
        context.user_data["temp_skill"] = {"name": skill_name}
        
        await update.message.reply_text(
            f"What's your proficiency level in {skill_name}?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Beginner", callback_data="beginner")],
                [InlineKeyboardButton("Intermediate", callback_data="intermediate")],
                [InlineKeyboardButton("Advanced", callback_data="advanced")],
                [InlineKeyboardButton("Expert", callback_data="expert")],
            ])
        )
        
        return SKILL_LEVEL
    
    async def get_skill_level(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Get the skill level."""
        query = update.callback_query
        await query.answer()
        
        skill_level = query.data
        context.user_data["temp_skill"]["level"] = skill_level
        
        await query.edit_message_text(
            f"How many years of experience do you have with {context.user_data['temp_skill']['name']}?\n"
            "Enter a number or send 0 if less than a year."
        )
        
        return SKILL_EXPERIENCE
    
    async def get_skill_experience(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Get years of experience with the skill."""
        try:
            years = int(update.message.text)
            context.user_data["temp_skill"]["years_experience"] = years
            
            # Add the skill to the profile
            if "skills" not in context.user_data["profile"]:
                context.user_data["profile"]["skills"] = []
            
            context.user_data["profile"]["skills"].append(context.user_data["temp_skill"])
            del context.user_data["temp_skill"]
            
            await update.message.reply_text(
                "Skill added! Would you like to add more skills?",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Add Another Skill", callback_data="add_more_skills")],
                    [InlineKeyboardButton("I'm Done", callback_data="finish_skills")],
                ])
            )
            
            return ADD_MORE_SKILLS
            
        except ValueError:
            await update.message.reply_text(
                "Please enter a valid number. How many years of experience do you have?"
            )
            return SKILL_EXPERIENCE
    
    async def add_more_skills(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Add more skills to the profile."""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "What's another skill you'd like to add to your profile?"
        )
        
        return SKILL_NAME
    
    async def finish_skills(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Finish adding skills and save the profile."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        
        # Create or update the user profile
        success = await self.save_user_profile(user.id, context.user_data["profile"])
        
        if success:
            await query.edit_message_text(
                "Your profile has been saved successfully! 🎉\n\n"
                "You can now browse jobs and receive personalized job alerts that match your profile.\n\n"
                "Use /jobs to start browsing available positions."
            )
        else:
            await query.edit_message_text(
                "There was an error saving your profile. Please try again later or contact support."
            )
        
        # Clear user data
        context.user_data.clear()
        
        return ConversationHandler.END
    
    async def skip_work_preferences(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Skip setting work preferences."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        
        # Create or update the user profile
        success = await self.save_user_profile(user.id, context.user_data["profile"])
        
        if success:
            await query.edit_message_text(
                "Your basic profile has been saved! 🎉\n\n"
                "You can complete your work preferences and add skills later by using /profile command.\n\n"
                "Use /jobs to start browsing available positions."
            )
        else:
            await query.edit_message_text(
                "There was an error saving your profile. Please try again later or contact support."
            )
        
        # Clear user data
        context.user_data.clear()
        
        return ConversationHandler.END
    
    async def show_profile(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Show the user's profile."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        user_profile = await self.get_user_profile(user.id)
        
        if not user_profile:
            await query.edit_message_text(
                "You don't have a profile yet. Would you like to create one?",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Create Profile", callback_data="create_profile")],
                    [InlineKeyboardButton("Cancel", callback_data="cancel")],
                ])
            )
            return PROFILE_MENU
        
        # Format profile for display
        profile_text = f"📋 *YOUR PROFILE*\n\n"
        profile_text += f"*Name:* {user_profile.first_name} {user_profile.last_name}\n"
        profile_text += f"*Email:* {user_profile.email}\n"
        
        if user_profile.phone:
            profile_text += f"*Phone:* {user_profile.phone}\n"
        
        if user_profile.city or user_profile.country:
            location = []
            if user_profile.city:
                location.append(user_profile.city)
            if user_profile.country:
                location.append(user_profile.country)
            profile_text += f"*Location:* {', '.join(location)}\n"
        
        if user_profile.bio:
            profile_text += f"\n*About:*\n{user_profile.bio}\n"
        
        # Work preferences
        if user_profile.work_preferences:
            profile_text += "\n*Work Preferences:*\n"
            wp = user_profile.work_preferences
            
            if wp.work_type:
                profile_text += f"- Work Type: {wp.work_type.value.capitalize()}\n"
            
            if wp.job_type:
                profile_text += f"- Job Type: {wp.job_type.value.replace('_', ' ').capitalize()}\n"
        
        # Skills
        if user_profile.skills and len(user_profile.skills) > 0:
            profile_text += "\n*Skills:*\n"
            for skill in user_profile.skills:
                exp_text = f"({skill.years_experience}+ years)" if skill.years_experience and skill.years_experience > 0 else ""
                profile_text += f"- {skill.name}: {skill.level.value.capitalize()} {exp_text}\n"
        
        # Subscription status
        profile_text += f"\n*Subscription:* {user_profile.subscription_type.capitalize() if user_profile.subscription_type else 'Free'}"
        
        # Show profile and options
        await query.edit_message_text(
            profile_text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Edit Profile", callback_data="edit_profile")],
                [InlineKeyboardButton("Back", callback_data="cancel")],
            ])
        )
        
        return PROFILE_MENU
    
    async def edit_profile(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the profile editing process."""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        user_profile = await self.get_user_profile(user.id)
        
        if not user_profile:
            await query.edit_message_text(
                "You don't have a profile yet. Would you like to create one?",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Create Profile", callback_data="create_profile")],
                    [InlineKeyboardButton("Cancel", callback_data="cancel")],
                ])
            )
            return PROFILE_MENU
        
        # For now, just redirect to create profile (we'll implement editing later)
        await query.edit_message_text(
            "Profile editing will be available in a future update. For now, you can create a new profile.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Create New Profile", callback_data="create_profile")],
                [InlineKeyboardButton("Cancel", callback_data="cancel")],
            ])
        )
        
        return PROFILE_MENU
    
    async def cancel_profile(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel the conversation."""
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            await query.edit_message_text("Profile management canceled.")
        else:
            await update.message.reply_text(
                "Profile management canceled.",
                reply_markup=ReplyKeyboardRemove()
            )
        
        # Clear user data
        context.user_data.clear()
        
        return ConversationHandler.END
    
    async def unknown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle unknown commands."""
        await update.message.reply_text(
            "Sorry, I didn't understand that command. Use /help to see available commands."
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle non-command messages."""
        await update.message.reply_text(
            "I'm not sure how to respond to that. Use /help to see available commands."
        )
    
    async def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        """
        Get user profile from database.
        This is a placeholder function for now.
        """
        # TODO: Implement database lookup
        return None
    
    async def save_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> bool:
        """
        Save user profile to database.
        This is a placeholder function for now.
        """
        # TODO: Implement database save
        logger.info(f"Saving profile for user {user_id}: {profile_data}")
        return True
    
    async def run_async(self):
        """Run the bot in async mode"""
        if not self.enabled or not self.application:
            logger.warning("Cannot run disabled bot")
            return
            
        try:
            logger.info("🔄 Starting Telegram bot in polling mode (local development)")
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling(drop_pending_updates=True)
        except Exception as e:
            logger.error(f"❌ Error running Telegram bot: {e}")
            try:
                if self.application:
                    await self.application.stop()
                    await self.application.shutdown()
            except Exception as shutdown_error:
                logger.error(f"Error during shutdown: {shutdown_error}")
    
    def run(self):
        """Run the bot polling in a blocking way"""
        if not self.enabled or not self.application:
            logger.warning("Cannot run Telegram bot: bot is disabled or not properly initialized")
            return
            
        try:
            logger.info("Starting Telegram bot polling...")
            self.application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True,
                error_callback=self._error_callback,
                close_loop=False
            )
        except Exception as e:
            logger.error(f"Error in Telegram bot polling: {str(e)}")
            # Try to restart the bot after a short delay
            time.sleep(5)
            logger.info("Attempting to restart Telegram bot...")
            self.application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True,
                error_callback=self._error_callback,
                close_loop=False
            )
            
    def _error_callback(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Log errors caused by updates."""
        logger.error(f"Telegram bot error: {context.error} caused by {update}")
    
    async def send_deployment_notification(self, deployment_data: Dict[str, Any]) -> bool:
        """
        Send deployment notification to Telegram
        
        Args:
            deployment_data: Dictionary containing deployment information
        """
        if not self.enabled or not self.application:
            logger.warning("Cannot send deployment notification: Bot is disabled")
            return False
            
        try:
            # Get notification chat ID from environment
            notification_chat_id = os.getenv('TELEGRAM_CHAT_ID')
            
            if not notification_chat_id:
                logger.warning("TELEGRAM_CHAT_ID not set, cannot send deployment notification")
                return False
            
            try:
                notification_chat_id = int(notification_chat_id)
            except ValueError:
                logger.error(f"Invalid TELEGRAM_CHAT_ID format: {notification_chat_id}")
                return False
            
            # Format message based on notification type
            notification_type = deployment_data.get('type', 'deployment')
            
            if notification_type == 'deployment':
                message = self._format_deployment_message(deployment_data)
            elif notification_type == 'external_api_crawl':
                message = self._format_external_api_message(deployment_data)
            elif notification_type == 'distill_crawl':
                message = self._format_distill_crawl_message(deployment_data)
            elif notification_type == 'daily_statistics':
                message = self._format_daily_stats_message(deployment_data)
            else:
                message = self._format_generic_message(deployment_data)
            
            # Send notification
            try:
                await self.application.bot.send_message(
                    chat_id=notification_chat_id,
                    text=message,
                    parse_mode='HTML',
                    disable_web_page_preview=True
                )
                logger.info(f"Deployment notification sent successfully to chat {notification_chat_id}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to send deployment notification: {str(e)}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to process deployment notification: {str(e)}")
            return False
    
    def _format_deployment_message(self, data: Dict[str, Any]) -> str:
        """Format deployment notification message"""
        status_emoji = "✅" if data.get('status') == 'success' else "⚠️" if data.get('status') == 'warning' else "❌"
        
        # Get current date and time
        current_time = datetime.now()
        date_str = current_time.strftime('%d.%m.%Y')
        time_str = current_time.strftime('%H:%M')
        
        message = f"🚀 <b>DEPLOYMENT GÜNCELLEMESİ</b>\n\n"
        message += f"🕐 <b>Tarih:</b> {date_str}\n"
        message += f"⏰ <b>Saat:</b> {time_str} UTC\n\n"
        
        message += f"🌍 <b>Ortam:</b> {data.get('environment', 'Bilinmiyor')}\n"
        message += f"📊 <b>Durum:</b> {data.get('status', 'bilinmiyor').upper()}\n"
        
        if 'commit' in data:
            message += f"🔗 <b>Commit:</b> {data['commit']}\n"
        
        if 'message' in data:
            message += f"💬 <b>Mesaj:</b> {data['message']}\n"
        
        if 'services' in data:
            message += f"⚙️ <b>Servisler:</b> {', '.join(data['services'])}\n"
        
        message += f"\n🎯 <b>ÖZET</b>\n"
        if data.get('status') == 'success':
            message += f"Buzz2Remote backend servisi başarıyla deploy edildi ve çalışıyor.\n\n"
        else:
            message += f"Deployment sırasında bir sorun oluştu.\n\n"
        
        message += f"#Buzz2Remote #Deployment #Backend"
        return message
    
    def _format_external_api_message(self, data: Dict[str, Any]) -> str:
        """Format external API crawl notification message"""
        status_emoji = "✅" if data.get('status') == 'success' else "❌"
        
        # Get current date and time
        current_time = datetime.now()
        date_str = current_time.strftime('%d.%m.%Y')
        time_str = current_time.strftime('%H:%M')
        
        message = f"🌐 <b>EXTERNAL API CRAWL</b>\n\n"
        message += f"🕐 <b>Tarih:</b> {date_str}\n"
        message += f"⏰ <b>Saat:</b> {time_str} UTC\n\n"
        
        message += f"📊 <b>Durum:</b> {data.get('status', 'bilinmiyor').upper()}\n"
        
        if data.get('status') == 'success':
            message += f"📈 <b>Toplam İş:</b> {data.get('total_jobs', 0):,}\n"
            
            if 'api_results' in data:
                message += "\n🔍 <b>API Sonuçları:</b>\n"
                for api_name, count in data['api_results'].items():
                    message += f"• {api_name}: {count} iş\n"
        else:
            message += f"❌ <b>Hata:</b> {data.get('error', 'Bilinmeyen hata')}\n"
        
        message += f"\n🎯 <b>ÖZET</b>\n"
        if data.get('status') == 'success':
            message += f"External API'lerden iş ilanları başarıyla çekildi.\n\n"
        else:
            message += f"External API crawl sırasında hata oluştu.\n\n"
        
        message += f"#Buzz2Remote #ExternalAPI #Crawler"
        return message
    
    def _format_distill_crawl_message(self, data: Dict[str, Any]) -> str:
        """Format distill crawl notification message"""
        status_emoji = "✅" if data.get('status') == 'success' else "❌"
        
        # Get current date and time
        current_time = datetime.now()
        date_str = current_time.strftime('%d.%m.%Y')
        time_str = current_time.strftime('%H:%M')
        
        message = f"🔍 <b>DISTILL CRAWL</b>\n\n"
        message += f"🕐 <b>Tarih:</b> {date_str}\n"
        message += f"⏰ <b>Saat:</b> {time_str} UTC\n\n"
        
        message += f"📊 <b>Durum:</b> {data.get('status', 'bilinmiyor').upper()}\n"
        
        if data.get('status') == 'success':
            message += f"🏢 <b>Bulunan Şirketler:</b> {data.get('companies_found', 0):,}\n"
            message += f"📈 <b>Bulunan İşler:</b> {data.get('jobs_found', 0):,}\n"
        else:
            message += f"❌ <b>Hata:</b> {data.get('error', 'Bilinmeyen hata')}\n"
        
        message += f"\n🎯 <b>ÖZET</b>\n"
        if data.get('status') == 'success':
            message += f"Distill crawler başarıyla çalıştı ve yeni veriler toplandı.\n\n"
        else:
            message += f"Distill crawl sırasında hata oluştu.\n\n"
        
        message += f"#Buzz2Remote #DistillCrawler #Companies"
        return message
    
    def _format_daily_stats_message(self, data: Dict[str, Any]) -> str:
        """Format daily statistics notification message"""
        status_emoji = "✅" if data.get('status') == 'success' else "❌"
        
        # Get current date and time
        current_time = datetime.now()
        date_str = current_time.strftime('%d.%m.%Y')
        time_str = current_time.strftime('%H:%M')
        
        message = f"📊 <b>GÜNLÜK İSTATİSTİK RAPORU</b>\n\n"
        message += f"🕐 <b>Tarih:</b> {date_str}\n"
        message += f"⏰ <b>Saat:</b> {time_str} UTC\n\n"
        
        if data.get('status') == 'success':
            message += f"📈 <b>İŞ İLANLARI</b>\n"
            message += f"• Toplam İlan: <b>{data.get('total_jobs', 0):,}</b>\n"
            message += f"• Aktif İlan: <b>{data.get('active_jobs', 0):,}</b>\n"
            message += f"• Bugün Eklenen: <b>{data.get('new_jobs_today', 0):,}</b>\n\n"
            
            message += f"🏢 <b>ŞİRKETLER</b>\n"
            message += f"• Toplam Şirket: <b>{data.get('total_companies', 0):,}</b>\n\n"
            
            message += f"✅ <b>DURUM</b>\n"
            message += f"• Veritabanı: <b>Bağlı</b>\n"
            message += f"• API Servisi: <b>Aktif</b>\n"
            message += f"• Scheduler: <b>Çalışıyor</b>\n\n"
            
            message += f"🎯 <b>ÖZET</b>\n"
            message += f"Buzz2Remote platformu günlük istatistikleri başarıyla toplandı. Tüm sistemler normal çalışıyor.\n\n"
            message += f"#Buzz2Remote #RemoteJobs #DailyStats"
        else:
            message += f"❌ <b>HATA</b>\n"
            message += f"• Hata: {data.get('error', 'Bilinmeyen hata')}\n\n"
            message += f"⚠️ Sistem hatası nedeniyle istatistikler toplanamadı."
        
        return message
    
    def _format_generic_message(self, data: Dict[str, Any]) -> str:
        """Format generic notification message"""
        status_emoji = "📢" if data.get('status') == 'success' else "⚠️" if data.get('status') == 'warning' else "💥"
        status_text = "BAŞARILI" if data.get('status') == 'success' else "UYARI" if data.get('status') == 'warning' else "HATA"
        
        # Get current date and time
        current_time = datetime.now()
        date_str = current_time.strftime('%d.%m.%Y')
        time_str = current_time.strftime('%H:%M')
        
        message = f"{status_emoji} <b>GENEL BİLDİRİM</b>\n\n"
        message += f"🕐 <b>Tarih:</b> {date_str}\n"
        message += f"⏰ <b>Saat:</b> {time_str} UTC\n\n"
        
        message += f"📋 <b>Tip:</b> {data.get('type', 'Bilinmiyor')}\n"
        message += f"📊 <b>Durum:</b> {status_text}\n"
        
        if 'message' in data:
            message += f"💬 <b>Mesaj:</b> {data['message']}\n"
        
        if 'error' in data:
            message += f"❌ <b>Hata:</b> {data['error']}\n"
        
        message += f"\n🎯 <b>ÖZET</b>\n"
        message += f"Buzz2Remote platformundan genel bildirim.\n\n"
        message += f"#Buzz2Remote #Notification #Update"
        return message
    
    async def send_error_notification(self, message: str, error_data: Dict[str, Any] = None) -> bool:
        """
        Send error notification from Sentry to Telegram
        
        Args:
            message: Formatted error message
            error_data: Additional error data from Sentry
        """
        if not self.enabled or not self.application:
            logger.warning("Cannot send error notification: Bot is disabled")
            return False
            
        try:
            # Get notification chat ID from environment
            notification_chat_id = os.getenv('TELEGRAM_CHAT_ID')
            
            if not notification_chat_id:
                logger.warning("TELEGRAM_CHAT_ID not set, cannot send error notification")
                return False
            
            try:
                notification_chat_id = int(notification_chat_id)
            except ValueError:
                logger.error(f"Invalid TELEGRAM_CHAT_ID format: {notification_chat_id}")
                return False
            
            # Send notification
            try:
                await self.application.bot.send_message(
                    chat_id=notification_chat_id,
                    text=message,
                    parse_mode='HTML',
                    disable_web_page_preview=True
                )
                logger.info(f"Error notification sent successfully to chat {notification_chat_id}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to send error notification: {str(e)}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to process error notification: {str(e)}")
            return False
    
    async def send_new_job_notification(self, job_data: Dict[str, Any]) -> bool:
        """
        Send new job notification to Telegram
        
        Args:
            job_data: Dictionary containing job information
        """
        if not self.enabled or not self.application:
            logger.warning("Cannot send new job notification: Bot is disabled")
            return False
            
        try:
            # Format the new job message
            message = self._format_new_job_message(job_data)
            
            # Get notification chat ID from environment
            notification_chat_id = os.getenv('TELEGRAM_CHAT_ID')
            
            if not notification_chat_id:
                logger.warning("TELEGRAM_CHAT_ID not set, cannot send new job notification")
                return False
            
            try:
                notification_chat_id = int(notification_chat_id)
            except ValueError:
                logger.error(f"Invalid TELEGRAM_CHAT_ID format: {notification_chat_id}")
                return False
            
            # Send notification
            try:
                await self.application.bot.send_message(
                    chat_id=notification_chat_id,
                    text=message,
                    parse_mode='HTML'
                )
                logger.info(f"New job notification sent successfully to chat {notification_chat_id}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to send new job notification: {str(e)}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to process new job notification: {str(e)}")
            return False

    def _format_new_job_message(self, data: Dict[str, Any]) -> str:
        """Format new job notification message"""
        # Get current date and time
        current_time = datetime.now()
        date_str = current_time.strftime('%d.%m.%Y')
        time_str = current_time.strftime('%H:%M')
        
        # Remote indicator
        remote_emoji = "🏠" if data.get('is_remote', False) else "🏢"
        remote_text = "Remote" if data.get('is_remote', False) else "On-site"
        
        # Salary formatting
        salary = data.get('salary', 'Not specified')
        if salary and salary != 'Not specified':
            salary_text = f"💰 <b>Maaş:</b> {salary}"
        else:
            salary_text = "💰 <b>Maaş:</b> Belirtilmemiş"
        
        message = f"🆕 <b>YENİ İŞ İLANI EKLENDİ!</b>\n\n"
        message += f"🕐 <b>Tarih:</b> {date_str}\n"
        message += f"⏰ <b>Saat:</b> {time_str} UTC\n\n"
        
        message += f"💼 <b>Pozisyon:</b> {data.get('job_title', 'Bilinmiyor')}\n"
        message += f"🏢 <b>Şirket:</b> {data.get('company', 'Bilinmiyor')}\n"
        message += f"📍 <b>Konum:</b> {data.get('location', 'Bilinmiyor')}\n"
        message += f"📋 <b>İş Türü:</b> {data.get('job_type', 'Bilinmiyor')}\n"
        message += f"{remote_emoji} <b>Çalışma Şekli:</b> {remote_text}\n"
        message += f"{salary_text}\n\n"
        
        message += f"🔗 <b>İlan ID:</b> {data.get('job_id', 'Bilinmiyor')}\n\n"
        
        message += f"🎯 <b>ÖZET</b>\n"
        message += f"Buzz2Remote platformuna yeni bir iş ilanı eklendi. Detayları yukarıda görebilirsiniz.\n\n"
        
        message += f"#Buzz2Remote #NewJob #RemoteJobs #JobAlert"
        return message

    async def send_crawler_notification(self, crawler_data: Dict[str, Any]) -> bool:
        """
        Send crawler status notification to Telegram
        
        Args:
            crawler_data: Dictionary containing crawler information
        """
        if not self.enabled or not self.application:
            logger.warning("Cannot send crawler notification: Bot is disabled")
            return False
            
        try:
            # Format the crawler message
            status_emoji = "🕷️" if crawler_data.get('status') == 'success' else "⚠️" if crawler_data.get('status') == 'warning' else "💥"
            status_text = "BAŞARILI" if crawler_data.get('status') == 'success' else "UYARI" if crawler_data.get('status') == 'warning' else "HATA"
            
            # Get current date and time
            current_time = datetime.now()
            date_str = current_time.strftime('%d.%m.%Y')
            time_str = current_time.strftime('%H:%M')
            
            message = f"{status_emoji} <b>CRAWLER GÜNCELLEMESİ</b>\n\n"
            message += f"🕐 <b>Tarih:</b> {date_str}\n"
            message += f"⏰ <b>Saat:</b> {time_str} UTC\n\n"
            
            message += f"🔧 <b>Servis:</b> {crawler_data.get('service', 'Bilinmiyor')}\n"
            message += f"📊 <b>Durum:</b> {status_text}\n"
            
            if 'companies_processed' in crawler_data:
                message += f"🏢 <b>İşlenen Şirketler:</b> {crawler_data['companies_processed']:,}\n"
            
            if 'jobs_found' in crawler_data:
                message += f"📈 <b>Bulunan İşler:</b> {crawler_data['jobs_found']:,}\n"
            
            if 'new_jobs' in crawler_data:
                message += f"🆕 <b>Yeni İşler:</b> {crawler_data['new_jobs']:,}\n"
            
            if 'disabled_endpoints' in crawler_data and crawler_data['disabled_endpoints']:
                message += f"\n🚫 <b>Devre Dışı Endpoint'ler:</b> {len(crawler_data['disabled_endpoints'])}\n"
                for endpoint in crawler_data['disabled_endpoints'][:5]:  # Show max 5
                    reason = endpoint.get('reason', 'Bilinmiyor')
                    company = endpoint.get('company', 'Bilinmiyor')
                    message += f"• {company}: {reason}\n"
                
                if len(crawler_data['disabled_endpoints']) > 5:
                    message += f"• ... ve {len(crawler_data['disabled_endpoints']) - 5} tane daha\n"
            
            if 'errors' in crawler_data and crawler_data['errors']:
                message += f"\n❌ <b>Hatalar:</b> {len(crawler_data['errors'])}\n"
                for error in crawler_data['errors'][:3]:  # Show max 3 errors
                    message += f"• {error}\n"
                
                if len(crawler_data['errors']) > 3:
                    message += f"• ... ve {len(crawler_data['errors']) - 3} hata daha\n"
            
            if 'duration' in crawler_data:
                message += f"\n⏱️ <b>Süre:</b> {crawler_data['duration']}\n"
            
            message += f"\n🎯 <b>ÖZET</b>\n"
            if crawler_data.get('status') == 'success':
                message += f"Crawler başarıyla çalıştı ve veriler güncellendi.\n\n"
            else:
                message += f"Crawler çalışması sırasında sorunlar oluştu.\n\n"
            
            message += f"#Buzz2Remote #Crawler #Update"
            
            # Get notification chat ID from environment
            notification_chat_id = os.getenv('TELEGRAM_CHAT_ID')
            
            if not notification_chat_id:
                logger.warning("TELEGRAM_CHAT_ID not set, cannot send crawler notification")
                return False
            
            try:
                notification_chat_id = int(notification_chat_id)
            except ValueError:
                logger.error(f"Invalid TELEGRAM_CHAT_ID format: {notification_chat_id}")
                return False
            
            # Send notification
            try:
                await self.application.bot.send_message(
                    chat_id=notification_chat_id,
                    text=message,
                    parse_mode='HTML'
                )
                logger.info(f"Crawler notification sent successfully to chat {notification_chat_id}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to send crawler notification: {str(e)}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to format crawler notification: {str(e)}")
            return False

def init_bot():
    try:
        bot = RemoteJobsBot()
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", bot.start))
        application.add_handler(CommandHandler("help", bot.help))
        application.add_handler(CommandHandler("jobs", bot.jobs))
        application.add_handler(CommandHandler("subscribe", bot.subscribe))
        
        # Profile conversation handler
        profile_conv_handler = ConversationHandler(
            entry_points=[CommandHandler("profile", bot.profile_start)],
            states={
                PROFILE_MENU: [
                    CallbackQueryHandler(bot.create_profile, pattern="^create_profile$"),
                    CallbackQueryHandler(bot.show_profile, pattern="^show_profile$"),
                    CallbackQueryHandler(bot.edit_profile, pattern="^edit_profile$"),
                    CallbackQueryHandler(bot.cancel_profile, pattern="^cancel$"),
                ],
                FIRST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.get_first_name)],
                LAST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.get_last_name)],
                EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.get_email)],
                PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.get_phone)],
                LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.get_location)],
                BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.get_bio)],
                WORK_PREFERENCES: [
                    CallbackQueryHandler(bot.get_work_preferences, pattern="^set_work_preferences$"),
                    CallbackQueryHandler(bot.skip_work_preferences, pattern="^skip_work_preferences$"),
                ],
                WORK_TYPE: [
                    CallbackQueryHandler(bot.get_work_type_remote, pattern="^remote$"),
                    CallbackQueryHandler(bot.get_work_type_hybrid, pattern="^hybrid$"),
                    CallbackQueryHandler(bot.get_work_type_office, pattern="^office$"),
                    CallbackQueryHandler(bot.get_work_type_any, pattern="^any$"),
                ],
                JOB_TYPE: [
                    CallbackQueryHandler(bot.get_job_type_full_time, pattern="^full_time$"),
                    CallbackQueryHandler(bot.get_job_type_part_time, pattern="^part_time$"),
                    CallbackQueryHandler(bot.get_job_type_contract, pattern="^contract$"),
                    CallbackQueryHandler(bot.get_job_type_freelance, pattern="^freelance$"),
                    CallbackQueryHandler(bot.get_job_type_internship, pattern="^internship$"),
                    CallbackQueryHandler(bot.get_job_type_any, pattern="^any$"),
                ],
                SKILL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.get_skill_name)],
                SKILL_LEVEL: [
                    CallbackQueryHandler(bot.get_skill_level, pattern="^(beginner|intermediate|advanced|expert)$"),
                ],
                SKILL_EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.get_skill_experience)],
                ADD_MORE_SKILLS: [
                    CallbackQueryHandler(bot.add_more_skills, pattern="^add_more_skills$"),
                    CallbackQueryHandler(bot.finish_skills, pattern="^finish_skills$"),
                ],
            },
            fallbacks=[CommandHandler("cancel", bot.cancel_profile)],
        )
        application.add_handler(profile_conv_handler)
        
        # Start the bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        return application
    except Exception as e:
        logger.error(f"Error initializing bot: {e}")
        return None

# Global variable to track bot instance
_bot_instance = None

def get_bot_instance():
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = init_bot()
    return _bot_instance 