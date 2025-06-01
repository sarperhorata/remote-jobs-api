#!/usr/bin/env python3
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

async def check_companies():
    client = AsyncIOMotorClient('mongodb://localhost:27017/')
    db = client['buzz2remote']
    count = await db.companies.count_documents({})
    print(f'Companies count: {count}')
    
    # Show some sample data
    if count > 0:
        companies = await db.companies.find({}).limit(3).to_list(length=3)
        for company in companies:
            print(f'Company: {company.get("name", "No name")}')
    else:
        # Let's create some sample companies
        sample_companies = [
            {
                'name': 'Driivz', 
                'website': 'https://driivz.com', 
                'location': 'Remote', 
                'industry': 'EV Technology', 
                'size': '100-500', 
                'description': 'Leading EV charging platform',
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                'name': 'AmplHire', 
                'website': 'https://amplhire.com', 
                'location': 'Paris, France', 
                'industry': 'Recruitment', 
                'size': '10-50',
                'description': 'Specialized recruitment agency',
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                'name': 'TechCorp', 
                'website': 'https://techcorp.com', 
                'location': 'Remote', 
                'industry': 'Technology', 
                'size': '500+',
                'description': 'Leading technology company',
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
        ]
        
        result = await db.companies.insert_many(sample_companies)
        print(f'Inserted {len(result.inserted_ids)} companies')
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_companies()) 