#!/usr/bin/env python3
"""
Telegram Bot Manager - Single Instance Management
Bu module Telegram bot'unu single instance olarak yönetir ve conflict'leri önler.
"""

import os
import fcntl
import atexit
import logging
from pathlib import Path
from typing import Optional
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class TelegramBotManager:
    """Telegram Bot Single Instance Manager"""
    
    def __init__(self):
        self.bot_instance = None
        self.lock_file = None
        self.lock_fd = None
        self.is_locked = False
        
        # Lock file path
        self.lock_path = Path("/tmp/buzz2remote_telegram_bot.lock")
        
    def acquire_lock(self) -> bool:
        """Acquire exclusive lock for bot instance"""
        try:
            # Create lock file
            self.lock_fd = os.open(str(self.lock_path), os.O_CREAT | os.O_WRONLY | os.O_TRUNC)
            
            # Try to acquire exclusive lock
            fcntl.flock(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            
            # Write PID to lock file
            os.write(self.lock_fd, str(os.getpid()).encode())
            os.fsync(self.lock_fd)
            
            self.is_locked = True
            logger.info(f"🔒 Telegram bot lock acquired (PID: {os.getpid()})")
            
            # Register cleanup on exit
            atexit.register(self.release_lock)
            
            return True
            
        except (OSError, IOError) as e:
            logger.warning(f"⚠️  Could not acquire Telegram bot lock: {e}")
            if self.lock_fd:
                try:
                    os.close(self.lock_fd)
                except:
                    pass
                self.lock_fd = None
            return False
    
    def release_lock(self):
        """Release the exclusive lock"""
        if self.is_locked and self.lock_fd:
            try:
                fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
                os.close(self.lock_fd)
                
                # Remove lock file
                if self.lock_path.exists():
                    self.lock_path.unlink()
                    
                logger.info("🔓 Telegram bot lock released")
                
            except Exception as e:
                logger.error(f"Error releasing lock: {e}")
            finally:
                self.lock_fd = None
                self.is_locked = False
    
    def check_existing_instance(self) -> Optional[int]:
        """Check if another bot instance is running"""
        if not self.lock_path.exists():
            return None
            
        try:
            with open(self.lock_path, 'r') as f:
                pid_str = f.read().strip()
                if pid_str:
                    pid = int(pid_str)
                    
                    # Check if process is still running
                    try:
                        os.kill(pid, 0)  # Signal 0 just checks if process exists
                        return pid
                    except ProcessLookupError:
                        # Process doesn't exist, remove stale lock file
                        self.lock_path.unlink()
                        logger.info("🧹 Removed stale lock file")
                        return None
                        
        except (ValueError, IOError) as e:
            logger.warning(f"Error checking existing instance: {e}")
            return None
    
    async def start_bot(self):
        """Start Telegram bot with single instance protection"""
        
        # Check if bot is disabled
        if not os.getenv("TELEGRAM_BOT_TOKEN"):
            logger.info("📴 Telegram bot disabled (no token provided)")
            return None
            
        # Production environment check for Render
        if os.getenv('ENVIRONMENT') == 'production':
            # In production, check for multiple instances more aggressively
            try:
                import psutil
                current_pid = os.getpid()
                
                # Look for other Python processes that might be running our bot
                bot_processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['name'] == 'python' and proc.info['pid'] != current_pid:
                            cmdline = ' '.join(proc.info['cmdline'] or [])
                            if 'telegram_bot' in cmdline or 'bot_manager' in cmdline:
                                bot_processes.append(proc.info['pid'])
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                if bot_processes:
                    logger.warning(f"⚠️  Found other potential bot processes: {bot_processes}. Skipping bot start to avoid conflicts.")
                    return None
            except ImportError:
                logger.info("psutil not available, using basic process checking")
                
        # Check for existing instance
        existing_pid = self.check_existing_instance()
        if existing_pid:
            logger.warning(f"⚠️  Another Telegram bot instance is running (PID: {existing_pid})")
            return None
            
        # Try to acquire lock
        if not self.acquire_lock():
            logger.warning("⚠️  Could not acquire lock, another instance might be starting")
            return None
            
        try:
            # Import and start bot
            from .bot import RemoteJobsBot
            
            self.bot_instance = RemoteJobsBot()
            
            if self.bot_instance.enabled:
                # Start bot in background
                logger.info("🤖 Starting Telegram bot...")
                bot_task = asyncio.create_task(self.bot_instance.run_async())
                
                # Send startup notification
                startup_data = {
                    'environment': 'production' if os.getenv('ENVIRONMENT') == 'production' else 'development',
                    'status': 'success',
                    'commit': os.getenv('RENDER_GIT_COMMIT', 'unknown')[:8],
                    'message': f'Backend service started successfully (PID: {os.getpid()})',
                    'timestamp': datetime.now().isoformat(),
                    'services': ['MongoDB Atlas', 'FastAPI', 'Telegram Bot', 'Scheduler Service'],
                    'instance': 'single-managed'
                }
                
                await self.bot_instance.send_deployment_notification(startup_data)
                logger.info("✅ Telegram bot started successfully!")
                
                return self.bot_instance
            else:
                logger.warning("📴 Telegram bot is disabled in configuration")
                self.release_lock()
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to start Telegram bot: {e}")
            self.release_lock()
            return None
    
    async def stop_bot(self):
        """Stop the bot and release resources"""
        if self.bot_instance and hasattr(self.bot_instance, 'stop'):
            try:
                await self.bot_instance.stop()
                logger.info("🛑 Telegram bot stopped")
            except Exception as e:
                logger.error(f"Error stopping bot: {e}")
        
        self.release_lock()

# Global bot manager instance
bot_manager = TelegramBotManager()

async def get_managed_bot():
    """Get managed Telegram bot instance"""
    return await bot_manager.start_bot()

async def stop_managed_bot():
    """Stop managed Telegram bot instance"""
    await bot_manager.stop_bot() 