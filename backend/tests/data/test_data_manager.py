#!/usr/bin/env python3
"""
Test Data Management System
Comprehensive test data generation, management, and cleanup
"""

import os
import sys
import json
import random
import string
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import asyncio
from bson import ObjectId

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

@dataclass
class TestUser:
    """Test user data structure"""
    email: str
    password: str
    full_name: str
    phone: str
    location: str
    experience_years: int
    skills: List[str]
    resume_url: Optional[str] = None
    profile_completed: bool = True
    email_verified: bool = True
    status: str = "active"

@dataclass
class TestJob:
    """Test job data structure"""
    title: str
    company: str
    description: str
    location: str
    salary_min: int
    salary_max: int
    requirements: List[str]
    benefits: List[str]
    job_type: str
    experience_level: str
    isRemote: bool
    status: str = "active"
    source: str = "test"

@dataclass
class TestCompany:
    """Test company data structure"""
    name: str
    description: str
    website: str
    industry: str
    size: str
    location: str
    founded_year: int
    status: str = "active"

@dataclass
class TestApplication:
    """Test application data structure"""
    user_id: str
    job_id: str
    status: str
    cover_letter: str
    resume_url: Optional[str] = None
    notes: Optional[str] = None

class TestDataGenerator:
    """Generate realistic test data"""
    
    def __init__(self):
        self.job_titles = [
            "Software Engineer", "Senior Developer", "Full Stack Developer",
            "Python Developer", "React Developer", "DevOps Engineer",
            "Data Scientist", "Product Manager", "UX Designer",
            "QA Engineer", "System Administrator", "Cloud Engineer"
        ]
        
        self.companies = [
            "Tech Corp", "Innovation Labs", "Digital Solutions",
            "Cloud Systems", "Data Analytics Inc", "Web Solutions",
            "Mobile Apps Co", "AI Research Lab", "Startup Hub",
            "Enterprise Solutions", "Remote Works", "Global Tech"
        ]
        
        self.locations = [
            "Remote", "New York, NY", "San Francisco, CA", "Austin, TX",
            "Seattle, WA", "Boston, MA", "Denver, CO", "Chicago, IL",
            "Los Angeles, CA", "Miami, FL", "Portland, OR", "Atlanta, GA"
        ]
        
        self.skills = [
            "Python", "JavaScript", "React", "Node.js", "Django",
            "FastAPI", "PostgreSQL", "MongoDB", "Docker", "Kubernetes",
            "AWS", "Azure", "Git", "TypeScript", "Vue.js", "Angular"
        ]
        
        self.industries = [
            "Technology", "Healthcare", "Finance", "Education",
            "E-commerce", "Entertainment", "Real Estate", "Transportation",
            "Manufacturing", "Consulting", "Non-profit", "Government"
        ]
        
        self.company_sizes = [
            "1-10", "11-50", "51-200", "201-500", "501-1000", "1000+"
        ]
    
    def generate_user(self, user_id: Optional[str] = None) -> TestUser:
        """Generate a test user"""
        first_name = random.choice(["John", "Jane", "Mike", "Sarah", "David", "Lisa", "Alex", "Emma"])
        last_name = random.choice(["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller"])
        full_name = f"{first_name} {last_name}"
        email = f"{first_name.lower()}.{last_name.lower()}@example.com"
        
        return TestUser(
            email=email,
            password="TestPass123!",
            full_name=full_name,
            phone=f"+1{random.randint(200, 999)}{random.randint(100, 999)}{random.randint(1000, 9999)}",
            location=random.choice(self.locations),
            experience_years=random.randint(1, 15),
            skills=random.sample(self.skills, random.randint(3, 8)),
            resume_url=f"https://example.com/resumes/{user_id or 'user'}.pdf"
        )
    
    def generate_job(self, company_id: Optional[str] = None) -> TestJob:
        """Generate a test job"""
        title = random.choice(self.job_titles)
        company = random.choice(self.companies)
        
        # Generate realistic salary range
        base_salary = random.randint(60000, 150000)
        salary_min = base_salary - random.randint(5000, 15000)
        salary_max = base_salary + random.randint(10000, 30000)
        
        return TestJob(
            title=title,
            company=company,
            description=f"We are looking for a talented {title.lower()} to join our team...",
            location=random.choice(self.locations),
            salary_min=salary_min,
            salary_max=salary_max,
            requirements=random.sample(self.skills, random.randint(3, 6)),
            benefits=["Health insurance", "Remote work", "Flexible hours", "Professional development"],
            job_type=random.choice(["full-time", "part-time", "contract"]),
            experience_level=random.choice(["entry", "mid-level", "senior", "lead"]),
            isRemote=random.choice([True, False])
        )
    
    def generate_company(self) -> TestCompany:
        """Generate a test company"""
        name = random.choice(self.companies)
        industry = random.choice(self.industries)
        
        return TestCompany(
            name=name,
            description=f"{name} is a leading company in the {industry} industry...",
            website=f"https://{name.lower().replace(' ', '')}.com",
            industry=industry,
            size=random.choice(self.company_sizes),
            location=random.choice(self.locations),
            founded_year=random.randint(1990, 2020)
        )
    
    def generate_application(self, user_id: str, job_id: str) -> TestApplication:
        """Generate a test application"""
        return TestApplication(
            user_id=user_id,
            job_id=job_id,
            status=random.choice(["applied", "reviewing", "interviewing", "offered", "rejected"]),
            cover_letter=f"I am excited to apply for this position...",
            resume_url=f"https://example.com/resumes/{user_id}.pdf",
            notes="Additional notes about the application"
        )

class TestDataManager:
    """Manage test data lifecycle"""
    
    def __init__(self, database_url: str = "mongodb://localhost:27017/test_buzz2remote"):
        self.database_url = database_url
        self.generator = TestDataGenerator()
        self.test_data = {
            'users': [],
            'jobs': [],
            'companies': [],
            'applications': []
        }
        self.data_file = Path(__file__).parent / "test_data_backup.json"
    
    async def setup_test_database(self):
        """Setup test database with initial data"""
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            
            client = AsyncIOMotorClient(self.database_url)
            db = client.get_default_database()
            
            # Clear existing test data
            await self.clear_test_data(db)
            
            # Generate and insert test data
            await self.generate_test_data(db)
            
            print(f"✅ Test database setup completed")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up test database: {e}")
            return False
    
    async def clear_test_data(self, db):
        """Clear existing test data"""
        collections = ['users', 'jobs', 'companies', 'applications']
        
        for collection in collections:
            try:
                # Delete documents with test source or test email pattern
                if collection == 'users':
                    await db[collection].delete_many({"email": {"$regex": "@example.com"}})
                elif collection == 'jobs':
                    await db[collection].delete_many({"source": "test"})
                elif collection == 'companies':
                    await db[collection].delete_many({"name": {"$in": self.generator.companies}})
                else:
                    await db[collection].delete_many({})
                    
                print(f"🧹 Cleared {collection} collection")
                
            except Exception as e:
                print(f"⚠️  Error clearing {collection}: {e}")
    
    async def generate_test_data(self, db):
        """Generate comprehensive test data"""
        print("🔄 Generating test data...")
        
        # Generate companies
        companies = []
        for i in range(10):
            company = self.generator.generate_company()
            company_dict = asdict(company)
            company_dict['_id'] = ObjectId()
            company_dict['created_at'] = datetime.utcnow()
            company_dict['updated_at'] = datetime.utcnow()
            
            result = await db.companies.insert_one(company_dict)
            company_dict['_id'] = str(result.inserted_id)
            companies.append(company_dict)
        
        # Generate users
        users = []
        for i in range(20):
            user = self.generator.generate_user(f"user_{i}")
            user_dict = asdict(user)
            user_dict['_id'] = ObjectId()
            user_dict['password_hash'] = "hashed_password_123"
            user_dict['created_at'] = datetime.utcnow()
            user_dict['updated_at'] = datetime.utcnow()
            user_dict['last_login'] = datetime.utcnow()
            
            result = await db.users.insert_one(user_dict)
            user_dict['_id'] = str(result.inserted_id)
            users.append(user_dict)
        
        # Generate jobs
        jobs = []
        for i in range(50):
            job = self.generator.generate_job()
            job_dict = asdict(job)
            job_dict['_id'] = ObjectId()
            job_dict['company_id'] = ObjectId(random.choice(companies)['_id'])
            job_dict['posted_date'] = datetime.utcnow() - timedelta(days=random.randint(0, 30))
            job_dict['created_at'] = datetime.utcnow()
            job_dict['updated_at'] = datetime.utcnow()
            job_dict['external_id'] = f"ext_{i}"
            
            result = await db.jobs.insert_one(job_dict)
            job_dict['_id'] = str(result.inserted_id)
            jobs.append(job_dict)
        
        # Generate applications
        applications = []
        for i in range(30):
            user = random.choice(users)
            job = random.choice(jobs)
            
            application = self.generator.generate_application(user['_id'], job['_id'])
            app_dict = asdict(application)
            app_dict['_id'] = ObjectId()
            app_dict['applied_date'] = datetime.utcnow() - timedelta(days=random.randint(0, 14))
            app_dict['created_at'] = datetime.utcnow()
            app_dict['updated_at'] = datetime.utcnow()
            
            result = await db.applications.insert_one(app_dict)
            app_dict['_id'] = str(result.inserted_id)
            applications.append(app_dict)
        
        # Store test data for cleanup
        self.test_data = {
            'users': users,
            'jobs': jobs,
            'companies': companies,
            'applications': applications
        }
        
        # Save test data backup
        await self.save_test_data_backup()
        
        print(f"✅ Generated test data:")
        print(f"   📊 Companies: {len(companies)}")
        print(f"   👥 Users: {len(users)}")
        print(f"   💼 Jobs: {len(jobs)}")
        print(f"   📝 Applications: {len(applications)}")
    
    async def save_test_data_backup(self):
        """Save test data backup to file"""
        try:
            # Convert ObjectId to string for JSON serialization
            backup_data = {}
            for collection, items in self.test_data.items():
                backup_data[collection] = []
                for item in items:
                    item_copy = item.copy()
                    if '_id' in item_copy:
                        item_copy['_id'] = str(item_copy['_id'])
                    backup_data[collection].append(item_copy)
            
            with open(self.data_file, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            print(f"💾 Test data backup saved to {self.data_file}")
            
        except Exception as e:
            print(f"⚠️  Error saving test data backup: {e}")
    
    async def load_test_data_backup(self):
        """Load test data from backup file"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
                    self.test_data = json.load(f)
                print(f"📂 Test data backup loaded from {self.data_file}")
                return True
            else:
                print(f"⚠️  Test data backup file not found: {self.data_file}")
                return False
                
        except Exception as e:
            print(f"❌ Error loading test data backup: {e}")
            return False
    
    async def cleanup_test_data(self):
        """Clean up test data from database"""
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            
            client = AsyncIOMotorClient(self.database_url)
            db = client.get_default_database()
            
            # Clear test data
            await self.clear_test_data(db)
            
            # Clear backup file
            if self.data_file.exists():
                self.data_file.unlink()
            
            print(f"🧹 Test data cleanup completed")
            return True
            
        except Exception as e:
            print(f"❌ Error cleaning up test data: {e}")
            return False
    
    def get_test_user(self, index: int = 0) -> Optional[Dict]:
        """Get a test user by index"""
        if self.test_data['users'] and index < len(self.test_data['users']):
            return self.test_data['users'][index]
        return None
    
    def get_test_job(self, index: int = 0) -> Optional[Dict]:
        """Get a test job by index"""
        if self.test_data['jobs'] and index < len(self.test_data['jobs']):
            return self.test_data['jobs'][index]
        return None
    
    def get_test_company(self, index: int = 0) -> Optional[Dict]:
        """Get a test company by index"""
        if self.test_data['companies'] and index < len(self.test_data['companies']):
            return self.test_data['companies'][index]
        return None
    
    def get_test_application(self, index: int = 0) -> Optional[Dict]:
        """Get a test application by index"""
        if self.test_data['applications'] and index < len(self.test_data['applications']):
            return self.test_data['applications'][index]
        return None
    
    def get_random_test_user(self) -> Optional[Dict]:
        """Get a random test user"""
        if self.test_data['users']:
            return random.choice(self.test_data['users'])
        return None
    
    def get_random_test_job(self) -> Optional[Dict]:
        """Get a random test job"""
        if self.test_data['jobs']:
            return random.choice(self.test_data['jobs'])
        return None
    
    def get_test_data_summary(self) -> Dict:
        """Get summary of test data"""
        return {
            'users_count': len(self.test_data['users']),
            'jobs_count': len(self.test_data['jobs']),
            'companies_count': len(self.test_data['companies']),
            'applications_count': len(self.test_data['applications']),
            'backup_file': str(self.data_file) if self.data_file.exists() else None
        }

class TestDataFixture:
    """Pytest fixture for test data management"""
    
    def __init__(self, database_url: str = "mongodb://localhost:27017/test_buzz2remote"):
        self.manager = TestDataManager(database_url)
    
    async def setup(self):
        """Setup test data"""
        return await self.manager.setup_test_database()
    
    async def cleanup(self):
        """Cleanup test data"""
        return await self.manager.cleanup_test_data()
    
    def get_manager(self) -> TestDataManager:
        """Get the test data manager"""
        return self.manager

# Pytest fixtures
import pytest

@pytest.fixture(scope="session")
async def test_data_manager():
    """Test data manager fixture"""
    manager = TestDataManager()
    await manager.setup_test_database()
    yield manager
    await manager.cleanup_test_data()

@pytest.fixture
def test_user(test_data_manager):
    """Test user fixture"""
    return test_data_manager.get_random_test_user()

@pytest.fixture
def test_job(test_data_manager):
    """Test job fixture"""
    return test_data_manager.get_random_test_job()

@pytest.fixture
def test_company(test_data_manager):
    """Test company fixture"""
    return test_data_manager.get_test_company()

@pytest.fixture
def test_application(test_data_manager):
    """Test application fixture"""
    return test_data_manager.get_test_application()

def main():
    """Main entry point for test data management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Data Management")
    parser.add_argument("--setup", action="store_true", help="Setup test database")
    parser.add_argument("--cleanup", action="store_true", help="Cleanup test data")
    parser.add_argument("--summary", action="store_true", help="Show test data summary")
    parser.add_argument("--database", default="mongodb://localhost:27017/test_buzz2remote", help="Database URL")
    
    args = parser.parse_args()
    
    async def run():
        manager = TestDataManager(args.database)
        
        if args.setup:
            print("🚀 Setting up test database...")
            await manager.setup_test_database()
            
        elif args.cleanup:
            print("🧹 Cleaning up test data...")
            await manager.cleanup_test_data()
            
        elif args.summary:
            await manager.load_test_data_backup()
            summary = manager.get_test_data_summary()
            print("📊 Test Data Summary:")
            for key, value in summary.items():
                print(f"   {key}: {value}")
        
        else:
            print("Please specify an action: --setup, --cleanup, or --summary")
    
    asyncio.run(run())

if __name__ == "__main__":
    main()