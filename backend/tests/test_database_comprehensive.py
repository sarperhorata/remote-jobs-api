import pytest
from unittest.mock import Mock, patch, AsyncMock
from database.db import get_database, init_database

class TestDatabaseOperations:
    @pytest.mark.asyncio
    @patch("database.db.get_database_client")
    async def test_get_database_success(self, mock_client):
        mock_db = Mock()
        mock_client.return_value = Mock()
        mock_client.return_value.__getitem__ = Mock(return_value=mock_db)
        
        db = await get_database()
        assert db is not None
        
    @pytest.mark.asyncio
    async def test_init_database(self):
        with patch("database.db.ensure_indexes") as mock_ensure:
            mock_ensure.return_value = AsyncMock()
            await init_database()
            assert True
