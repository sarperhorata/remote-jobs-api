import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, ContextTypes, filters

from utils.config import TELEGRAM_BOT_TOKEN, TELEGRAM_ENABLED, logger
from models.models import UserProfile, UserProfileCreate, UserProfileUpdate, WorkType, JobType, WorkHours, UserNotificationPreference

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

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
    
    def __init__(self):
        """Initialize the bot with token"""
        if not TELEGRAM_ENABLED:
            logger.warning("Telegram bot is disabled. Set TELEGRAM_BOT_TOKEN environment variable to enable it.")
            self.enabled = False
            self.application = None
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
            f"Hi {user.mention_html()}! I'm the Remote Jobs Monitor bot.\n\n"
            f"I can help you find remote job opportunities and notify you when new jobs matching your profile are available.\n\n"
            f"Use /help to see available commands."
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
        await update.message.reply_text(
            "Here are the commands you can use:\n\n"
            "/start - Start the bot\n"
            "/profile - Create or update your profile\n"
            "/jobs - Browse available jobs\n"
            "/subscribe - Subscribe to job alerts\n"
            "/help - Show this help message"
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
        await update.message.reply_text(
            "🔍 Job Search Options:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Browse All Jobs", callback_data="browse_all_jobs")],
                [InlineKeyboardButton("Browse Matching Jobs", callback_data="browse_matching_jobs")],
                [InlineKeyboardButton("Search Jobs", callback_data="search_jobs")],
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
        await update.message.reply_text(
            "📣 Subscription Options:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Daily Alerts", callback_data="subscribe_daily")],
                [InlineKeyboardButton("Weekly Digest", callback_data="subscribe_weekly")],
                [InlineKeyboardButton("Real-time Alerts (Premium)", callback_data="subscribe_realtime")],
                [InlineKeyboardButton("Unsubscribe", callback_data="unsubscribe")],
            ])
        )
    
    async def profile_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the profile conversation."""
        user = update.effective_user
        user_profile = await self.get_user_profile(user.id)
        
        buttons = []
        
        if user_profile:
            buttons.extend([
                [InlineKeyboardButton("View Profile", callback_data="show_profile")],
                [InlineKeyboardButton("Edit Profile", callback_data="edit_profile")],
            ])
        else:
            buttons.append([InlineKeyboardButton("Create Profile", callback_data="create_profile")])
        
        buttons.append([InlineKeyboardButton("Cancel", callback_data="cancel")])
        
        await update.message.reply_text(
            "Profile Management:",
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
    
    def run(self):
        """Run the bot polling in a blocking way"""
        if not self.enabled or not self.application:
            logger.warning("Cannot run Telegram bot: bot is disabled or not properly initialized")
            return
            
        try:
            logger.info("Starting Telegram bot polling...")
            self.application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True, error_callback=self._error_callback)
        except Exception as e:
            logger.error(f"Error in Telegram bot polling: {str(e)}")
            # Try to restart the bot after a short delay
            time.sleep(5)
            logger.info("Attempting to restart Telegram bot...")
            self.application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True, error_callback=self._error_callback)
            
    def _error_callback(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Log errors caused by updates."""
        logger.error(f"Telegram bot error: {context.error} caused by {update}")
    
    async def run_async(self):
        """Run the bot polling in a non-blocking way"""
        if not self.enabled or not self.application:
            logger.warning("Cannot run Telegram bot: bot is disabled or not properly initialized")
            return
            
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
    
    async def stop(self):
        """Stop the bot"""
        if self.enabled and self.application:
            await self.application.stop()
            logger.info("Telegram bot stopped")

    async def send_deployment_notification(self, deployment_data: Dict[str, Any]) -> bool:
        """
        Sends a deployment notification to all subscribed users
        
        Args:
            deployment_data: Dictionary containing deployment information
                {
                    'environment': str,  # e.g. 'production', 'staging'
                    'status': str,      # e.g. 'success', 'failed'
                    'commit': str,      # commit hash
                    'message': str,     # deployment message
                    'timestamp': str    # ISO format timestamp
                }
        """
        if not self.enabled or not self.application:
            logger.warning("Cannot send deployment notification: Bot is disabled")
            return False
            
        try:
            # Format the deployment message
            status_emoji = "✅" if deployment_data['status'] == 'success' else "❌"
            message = (
                f"{status_emoji} *Deployment Update*\n\n"
                f"*Environment:* {deployment_data['environment']}\n"
                f"*Status:* {deployment_data['status']}\n"
                f"*Commit:* `{deployment_data['commit']}`\n"
                f"*Message:* {deployment_data['message']}\n"
                f"*Time:* {deployment_data['timestamp']}"
            )
            
            # FOR TESTING: Hardcoded subscribed users
            # In a real application, you would fetch this from the database
            subscribed_users = [
                123456789,  # Replace with your Telegram chat ID for testing
                987654321   # Another example chat ID
            ]
            
            # Also get users from the database if available
            try:
                # This is a placeholder for the database query
                # You should implement proper database access here
                from models.models import UserNotificationPreference
                
                # Mock database query result
                db_users = [
                    UserNotificationPreference(user_id=123456789, telegram_chat_id=123456789, notify_on_deployment=True),
                    UserNotificationPreference(user_id=987654321, telegram_chat_id=987654321, notify_on_deployment=True)
                ]
                
                # Add these users to our list if they're not already there
                for user in db_users:
                    if user.notify_on_deployment and user.telegram_chat_id and user.telegram_chat_id not in subscribed_users:
                        subscribed_users.append(user.telegram_chat_id)
                        
            except Exception as e:
                logger.error(f"Failed to get users from database: {str(e)}")
                # Continue with hardcoded users
            
            # Send notification to each subscribed user
            successful_sends = 0
            for user_id in subscribed_users:
                try:
                    await self.application.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                    successful_sends += 1
                    logger.info(f"Deployment notification sent to user {user_id}")
                except Exception as e:
                    logger.error(f"Failed to send deployment notification to user {user_id}: {str(e)}")
                    continue
                    
            if successful_sends > 0:
                logger.info(f"Deployment notification sent to {successful_sends} users")
                return True
            else:
                logger.warning("No deployment notifications were sent successfully")
                return False
            
        except Exception as e:
            logger.error(f"Failed to send deployment notification: {str(e)}")
            return False


# Run the bot if this file is executed directly
if __name__ == "__main__":
    bot = RemoteJobsBot()
    bot.run() 