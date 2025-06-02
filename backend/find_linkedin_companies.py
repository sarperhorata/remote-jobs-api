import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from pymongo import MongoClient

def find_problematic_companies():
    # Use synchronous client for simplicity
    client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017'))
    db = client['buzz2remote']
    
    # Find companies with LinkedIn icon in their names
    companies = db.jobs.aggregate([
        {
            '$group': {
                '_id': '$company',
                'job_count': {'$sum': 1},
            }
        },
        {
            '$match': {
                '_id': {'$regex': 'linkedin|twitter|instagram|podcast|icon', '$options': 'i'}
            }
        },
        {'$limit': 20}
    ])
    
    print('Found problematic companies:')
    problematic_companies = []
    for company in companies:
        company_name = company["_id"]
        job_count = company["job_count"]
        print(f'Company: "{company_name[:100]}..." | Jobs: {job_count}')
        problematic_companies.append(company_name)
    
    client.close()
    return problematic_companies

if __name__ == "__main__":
    find_problematic_companies() 