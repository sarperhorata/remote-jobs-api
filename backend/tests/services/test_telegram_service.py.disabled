import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import os
import psutil
from services.telegram_service import TelegramService

class TestTelegramService:
    """Telegram Service testleri"""
    
    @pytest.fixture
    def mock_bot(self):
        """Mock Telegram Bot"""
        mock_bot = Mock()
        mock_bot.send_message = AsyncMock()
        mock_bot.get_me = AsyncMock(return_value=Mock(username="test_bot"))
        return mock_bot
    
    @pytest.fixture
    def mock_updater(self):
        """Mock Telegram Updater"""
        mock_updater = Mock()
        mock_updater.dispatcher = Mock()
        mock_updater.dispatcher.add_handler = Mock()
        mock_updater.start_polling = Mock()
        mock_updater.stop = Mock()
        return mock_updater
    
    @pytest.fixture
    def telegram_service(self, mock_bot, mock_updater):
        """Telegram service instance"""
        with patch('services.telegram_service.Bot', return_value=mock_bot), \
             patch('services.telegram_service.Updater', return_value=mock_updater), \
             patch('services.telegram_service.CommandHandler') as mock_handler:
            
            service = TelegramService()
            service.bot = mock_bot
            service.updater = mock_updater
            return service
    
    @pytest.fixture
    def telegram_service_without_token(self):
        """Token olmadan telegram service instance"""
        with patch.dict(os.environ, {}, clear=True):
            service = TelegramService()
            return service
    
    def test_service_initialization(self, telegram_service):
        """Service başlatma testi"""
        assert telegram_service is not None
        assert hasattr(telegram_service, 'bot')
        assert hasattr(telegram_service, 'updater')
        assert hasattr(telegram_service, 'enabled')
        assert telegram_service.enabled is False
    
    def test_singleton_pattern(self):
        """Singleton pattern testi"""
        service1 = TelegramService()
        service2 = TelegramService()
        
        assert service1 is service2
    
    @patch('services.telegram_service.psutil.process_iter')
    def test_initialization_with_existing_process(self, mock_process_iter):
        """Mevcut process ile başlatma testi"""
        mock_process = Mock()
        mock_process.info = {
            'pid': 12345,
            'name': 'python',
            'cmdline': ['python', 'telegram_service.py']
        }
        mock_process_iter.return_value = [mock_process]
        
        with patch('services.telegram_service.psutil.Process') as mock_process_class:
            mock_current_process = Mock()
            mock_current_process.pid = 67890
            mock_process_class.return_value = mock_current_process
            
            service = TelegramService()
            assert service is not None
    
    @pytest.mark.asyncio
    async def test_start_success(self, telegram_service):
        """Başarılı start testi"""
        with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'test_token'}):
            await telegram_service.start()
            
            assert telegram_service.enabled is True
            telegram_service.updater.start_polling.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_start_without_token(self, telegram_service_without_token):
        """Token olmadan start testi"""
        await telegram_service_without_token.start()
        
        assert telegram_service_without_token.enabled is False
        assert telegram_service_without_token.bot is None
    
    @pytest.mark.asyncio
    async def test_start_already_enabled(self, telegram_service):
        """Zaten enabled olduğunda start testi"""
        telegram_service.enabled = True
        
        await telegram_service.start()
        
        # Should not start again
        telegram_service.updater.start_polling.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_start_error(self, telegram_service):
        """Start hatası testi"""
        with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'test_token'}):
            telegram_service.updater.start_polling.side_effect = Exception("Start error")
            
            with pytest.raises(Exception, match="Start error"):
                await telegram_service.start()
    
    @pytest.mark.asyncio
    async def test_stop_success(self, telegram_service):
        """Başarılı stop testi"""
        telegram_service.enabled = True
        
        await telegram_service.stop()
        
        assert telegram_service.enabled is False
        telegram_service.updater.stop.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_stop_not_enabled(self, telegram_service):
        """Enabled olmadığında stop testi"""
        telegram_service.enabled = False
        
        await telegram_service.stop()
        
        telegram_service.updater.stop.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_stop_error(self, telegram_service):
        """Stop hatası testi"""
        telegram_service.enabled = True
        telegram_service.updater.stop.side_effect = Exception("Stop error")
        
        with pytest.raises(Exception, match="Stop error"):
            await telegram_service.stop()
    
    @pytest.mark.asyncio
    async def test_send_message_success(self, telegram_service):
        """Başarılı mesaj gönderme testi"""
        chat_id = "123456789"
        message = "Test message"
        
        await telegram_service.send_message(chat_id, message)
        
        telegram_service.bot.send_message.assert_called_once_with(
            chat_id=chat_id,
            text=message,
            parse_mode='HTML'
        )
    
    @pytest.mark.asyncio
    async def test_send_message_not_enabled(self, telegram_service):
        """Enabled olmadığında mesaj gönderme testi"""
        telegram_service.enabled = False
        
        result = await telegram_service.send_message("123456789", "Test message")
        
        assert result is False
        telegram_service.bot.send_message.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_send_message_error(self, telegram_service):
        """Mesaj gönderme hatası testi"""
        telegram_service.bot.send_message.side_effect = Exception("Send error")
        
        result = await telegram_service.send_message("123456789", "Test message")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_send_notification_success(self, telegram_service):
        """Başarılı notification gönderme testi"""
        notification_data = {
            "type": "job_alert",
            "title": "New Job Alert",
            "message": "A new job matching your criteria is available",
            "chat_id": "123456789"
        }
        
        result = await telegram_service.send_notification(notification_data)
        
        assert result is True
        telegram_service.bot.send_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_notification_missing_chat_id(self, telegram_service):
        """Chat ID eksik olduğunda notification testi"""
        notification_data = {
            "type": "job_alert",
            "title": "New Job Alert",
            "message": "A new job matching your criteria is available"
        }
        
        result = await telegram_service.send_notification(notification_data)
        
        assert result is False
        telegram_service.bot.send_message.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_send_broadcast_message(self, telegram_service):
        """Broadcast mesaj gönderme testi"""
        message = "Broadcast message"
        chat_ids = ["123456789", "987654321"]
        
        # Mock get_subscribed_users to return chat_ids
        telegram_service.get_subscribed_users = AsyncMock(return_value=chat_ids)
        
        result = await telegram_service.send_broadcast_message(message)
        
        assert result is True
        assert telegram_service.bot.send_message.call_count == 2
    
    @pytest.mark.asyncio
    async def test_send_broadcast_message_no_subscribers(self, telegram_service):
        """Abone olmadığında broadcast mesaj testi"""
        message = "Broadcast message"
        
        telegram_service.get_subscribed_users = AsyncMock(return_value=[])
        
        result = await telegram_service.send_broadcast_message(message)
        
        assert result is False
        telegram_service.bot.send_message.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_bot_info(self, telegram_service):
        """Bot bilgisi get testi"""
        bot_info = await telegram_service.get_bot_info()
        
        assert bot_info is not None
        assert bot_info.username == "test_bot"
        telegram_service.bot.get_me.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_bot_info_not_enabled(self, telegram_service):
        """Enabled olmadığında bot bilgisi testi"""
        telegram_service.enabled = False
        
        bot_info = await telegram_service.get_bot_info()
        
        assert bot_info is None
        telegram_service.bot.get_me.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_start_command_handler(self, telegram_service):
        """Start command handler testi"""
        mock_update = Mock()
        mock_update.effective_chat.id = "123456789"
        mock_context = Mock()
        
        await telegram_service._start_command(mock_update, mock_context)
        
        telegram_service.bot.send_message.assert_called_once()
        call_args = telegram_service.bot.send_message.call_args
        assert "123456789" in str(call_args)
        assert "Welcome" in str(call_args)
    
    @pytest.mark.asyncio
    async def test_help_command_handler(self, telegram_service):
        """Help command handler testi"""
        mock_update = Mock()
        mock_update.effective_chat.id = "123456789"
        mock_context = Mock()
        
        await telegram_service._help_command(mock_update, mock_context)
        
        telegram_service.bot.send_message.assert_called_once()
        call_args = telegram_service.bot.send_message.call_args
        assert "123456789" in str(call_args)
        assert "help" in str(call_args).lower()
    
    @pytest.mark.asyncio
    async def test_subscribe_command_handler(self, telegram_service):
        """Subscribe command handler testi"""
        mock_update = Mock()
        mock_update.effective_chat.id = "123456789"
        mock_context = Mock()
        
        # Mock database operations
        with patch('services.telegram_service.get_db') as mock_get_db:
            mock_db = Mock()
            mock_db.telegram_subscribers = Mock()
            mock_db.telegram_subscribers.find_one = AsyncMock(return_value=None)
            mock_db.telegram_subscribers.insert_one = AsyncMock()
            mock_get_db.return_value = mock_db
            
            await telegram_service._subscribe_command(mock_update, mock_context)
            
            telegram_service.bot.send_message.assert_called_once()
            mock_db.telegram_subscribers.insert_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_unsubscribe_command_handler(self, telegram_service):
        """Unsubscribe command handler testi"""
        mock_update = Mock()
        mock_update.effective_chat.id = "123456789"
        mock_context = Mock()
        
        # Mock database operations
        with patch('services.telegram_service.get_db') as mock_get_db:
            mock_db = Mock()
            mock_db.telegram_subscribers = Mock()
            mock_db.telegram_subscribers.delete_one = AsyncMock(return_value=Mock(deleted_count=1))
            mock_get_db.return_value = mock_db
            
            await telegram_service._unsubscribe_command(mock_update, mock_context)
            
            telegram_service.bot.send_message.assert_called_once()
            mock_db.telegram_subscribers.delete_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_subscribed_users(self, telegram_service):
        """Abone kullanıcıları get testi"""
        with patch('services.telegram_service.get_db') as mock_get_db:
            mock_db = Mock()
            mock_db.telegram_subscribers = Mock()
            mock_cursor = Mock()
            mock_cursor.to_list = AsyncMock(return_value=[
                {"chat_id": "123456789"},
                {"chat_id": "987654321"}
            ])
            mock_db.telegram_subscribers.find = Mock(return_value=mock_cursor)
            mock_get_db.return_value = mock_db
            
            users = await telegram_service.get_subscribed_users()
            
            assert len(users) == 2
            assert "123456789" in users
            assert "987654321" in users
    
    def test_service_methods_exist(self, telegram_service):
        """Service metodlarının varlığını test et"""
        required_methods = [
            'start',
            'stop',
            'send_message',
            'send_notification',
            'send_broadcast_message',
            'get_bot_info',
            'get_subscribed_users',
            '_start_command',
            '_help_command',
            '_subscribe_command',
            '_unsubscribe_command'
        ]
        
        for method in required_methods:
            assert hasattr(telegram_service, method)
            assert callable(getattr(telegram_service, method))
    
    @pytest.mark.asyncio
    async def test_service_integration(self, telegram_service):
        """Service integration testi"""
        # Test full lifecycle
        
        # Start service
        with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'test_token'}):
            await telegram_service.start()
            assert telegram_service.enabled is True
        
        # Send message
        result = await telegram_service.send_message("123456789", "Test message")
        assert result is True
        
        # Get bot info
        bot_info = await telegram_service.get_bot_info()
        assert bot_info is not None
        
        # Stop service
        await telegram_service.stop()
        assert telegram_service.enabled is False 