import asyncio
import httpx
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.main import app
from httpx import AsyncClient

async def test_registration():
    async with AsyncClient(app=app, base_url='http://test') as client:
        user_data = {
            'email': 'test@example.com',
            'password': 'testpassword123',
            'name': 'Test User'
        }
        
        # First registration
        response1 = await client.post('/api/register', json=user_data)
        print(f'First registration: {response1.status_code}')
        print(f'Response 1: {response1.text}')
        
        # Second registration with same email
        response2 = await client.post('/api/register', json=user_data)
        print(f'Second registration: {response2.status_code}')
        print(f'Response 2: {response2.text}')

if __name__ == '__main__':
    asyncio.run(test_registration()) 