from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import httpx
import asyncio
import logging
from datetime import datetime, timedelta
import json
import os
from pydantic import BaseModel

from ..core.config import settings
from ..middleware.auth_middleware import get_current_user
from ..models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/glassdoor", tags=["glassdoor"])

# Glassdoor API Configuration
GLASSDOOR_API_KEY = os.getenv("GLASSDOOR_API_KEY", "demo_key")
GLASSDOOR_PARTNER_ID = os.getenv("GLASSDOOR_PARTNER_ID", "demo_partner")
GLASSDOOR_BASE_URL = "https://api.glassdoor.com/api/api.htm"

# Pydantic models for request/response
class GlassdoorCompanyRequest(BaseModel):
    company: str
    location: Optional[str] = None

class GlassdoorReviewRequest(BaseModel):
    company: str
    page: int = 1
    limit: int = 10
    rating: Optional[int] = None
    jobTitle: Optional[str] = None
    location: Optional[str] = None
    employmentStatus: Optional[str] = None
    sentiment: Optional[str] = None

class GlassdoorSearchRequest(BaseModel):
    query: str
    page: int = 1
    limit: int = 10
    location: Optional[str] = None
    industry: Optional[str] = None

class ReviewSubmitRequest(BaseModel):
    company: str
    rating: int
    title: str
    pros: str
    cons: str
    advice: Optional[str] = None
    jobTitle: str
    location: str
    employmentStatus: str

class ReviewRateRequest(BaseModel):
    helpful: bool

# Mock data for development (when Glassdoor API is not available)
MOCK_COMPANY_DATA = {
    "Google": {
        "id": "google",
        "name": "Google",
        "website": "https://google.com",
        "industry": "Technology",
        "size": "100,000+ employees",
        "founded": "1998",
        "revenue": "$307B+",
        "headquarters": "Mountain View, CA",
        "mission": "To organize the world's information and make it universally accessible and useful",
        "values": ["Innovation", "User Focus", "Transparency", "Diversity", "Excellence"],
        "benefits": ["Health Insurance", "401k", "Remote Work", "Free Food", "Gym Membership"],
        "workLifeBalance": 4.1,
        "cultureAndValues": 4.3,
        "careerOpportunities": 4.5,
        "compensationAndBenefits": 4.4,
        "seniorManagement": 3.8,
        "overallRating": 4.2,
        "totalReviews": 12500,
        "recommendToFriend": 87,
        "ceoApproval": 94,
        "ceoName": "Sundar Pichai",
        "ceoImage": "https://example.com/sundar.jpg"
    },
    "Microsoft": {
        "id": "microsoft",
        "name": "Microsoft",
        "website": "https://microsoft.com",
        "industry": "Technology",
        "size": "200,000+ employees",
        "founded": "1975",
        "revenue": "$198B+",
        "headquarters": "Redmond, WA",
        "mission": "To empower every person and every organization on the planet to achieve more",
        "values": ["Innovation", "Diversity", "Inclusion", "Sustainability", "Trust"],
        "benefits": ["Health Insurance", "401k", "Remote Work", "Stock Options", "Professional Development"],
        "workLifeBalance": 4.0,
        "cultureAndValues": 4.2,
        "careerOpportunities": 4.3,
        "compensationAndBenefits": 4.1,
        "seniorManagement": 3.9,
        "overallRating": 4.1,
        "totalReviews": 8900,
        "recommendToFriend": 82,
        "ceoApproval": 91,
        "ceoName": "Satya Nadella",
        "ceoImage": "https://example.com/satya.jpg"
    }
}

MOCK_REVIEWS = {
    "Google": [
        {
            "id": "review-1",
            "author": "Anonymous Employee",
            "title": "Amazing company culture and benefits",
            "pros": "Great benefits, smart colleagues, innovative projects, excellent compensation",
            "cons": "Sometimes long hours, high pressure environment",
            "advice": "Be prepared to work hard but you'll be rewarded well",
            "rating": 5,
            "date": "2024-01-15",
            "jobTitle": "Software Engineer",
            "location": "Mountain View, CA",
            "employmentStatus": "Full-time",
            "helpfulCount": 45,
            "isVerified": True,
            "sentiment": "positive"
        },
        {
            "id": "review-2",
            "author": "Anonymous Employee",
            "title": "Great place to grow your career",
            "pros": "Excellent learning opportunities, great mentorship, cutting-edge technology",
            "cons": "Can be overwhelming for new employees, fast-paced environment",
            "advice": "Take advantage of all the learning resources available",
            "rating": 4,
            "date": "2024-01-10",
            "jobTitle": "Product Manager",
            "location": "San Francisco, CA",
            "employmentStatus": "Full-time",
            "helpfulCount": 32,
            "isVerified": True,
            "sentiment": "positive"
        }
    ],
    "Microsoft": [
        {
            "id": "review-3",
            "author": "Anonymous Employee",
            "title": "Good work-life balance and benefits",
            "pros": "Flexible work hours, good benefits, stable company",
            "cons": "Sometimes bureaucratic processes, slower decision making",
            "advice": "Be patient with processes and focus on collaboration",
            "rating": 4,
            "date": "2024-01-12",
            "jobTitle": "Software Engineer",
            "location": "Redmond, WA",
            "employmentStatus": "Full-time",
            "helpfulCount": 28,
            "isVerified": True,
            "sentiment": "positive"
        }
    ]
}

async def call_glassdoor_api(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Call Glassdoor API with proper authentication and error handling"""
    try:
        # Add required Glassdoor API parameters
        params.update({
            "v": "1",
            "format": "json",
            "t.p": GLASSDOOR_PARTNER_ID,
            "t.k": GLASSDOOR_API_KEY,
            "userip": "0.0.0.0",
            "useragent": "Mozilla/5.0"
        })
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(GLASSDOOR_BASE_URL, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Glassdoor API error: {response.status_code} - {response.text}")
                return None
                
    except Exception as e:
        logger.error(f"Error calling Glassdoor API: {str(e)}")
        return None

@router.get("/company")
async def get_company_info(
    company: str = Query(..., description="Company name"),
    location: Optional[str] = Query(None, description="Company location"),
    current_user: User = Depends(get_current_user)
):
    """Get company information from Glassdoor"""
    try:
        # Try to get real data from Glassdoor API
        params = {
            "action": "employers",
            "q": company,
            "l": location or ""
        }
        
        api_data = await call_glassdoor_api("employers", params)
        
        if api_data and api_data.get("response", {}).get("employers"):
            # Process real Glassdoor data
            employer = api_data["response"]["employers"][0]
            return {
                "id": employer.get("id"),
                "name": employer.get("name"),
                "website": employer.get("website"),
                "industry": employer.get("industry"),
                "size": employer.get("numberOfRatings"),
                "founded": employer.get("yearFounded"),
                "revenue": employer.get("revenue"),
                "headquarters": employer.get("headquarters"),
                "mission": employer.get("mission"),
                "values": employer.get("values", []),
                "benefits": employer.get("benefits", []),
                "workLifeBalance": employer.get("workLifeBalanceRating", 0),
                "cultureAndValues": employer.get("cultureAndValuesRating", 0),
                "careerOpportunities": employer.get("careerOpportunitiesRating", 0),
                "compensationAndBenefits": employer.get("compensationAndBenefitsRating", 0),
                "seniorManagement": employer.get("seniorLeadershipRating", 0),
                "overallRating": employer.get("overallRating", 0),
                "totalReviews": employer.get("numberOfRatings", 0),
                "recommendToFriend": employer.get("recommendToFriendPercentage", 0),
                "ceoApproval": employer.get("ceoRating", 0),
                "ceoName": employer.get("ceoName"),
                "ceoImage": employer.get("ceoImage")
            }
        
        # Fallback to mock data
        company_key = company.title()
        if company_key in MOCK_COMPANY_DATA:
            return MOCK_COMPANY_DATA[company_key]
        
        # Return generic mock data
        return {
            "id": company.lower().replace(" ", "-"),
            "name": company,
            "website": f"https://{company.lower().replace(' ', '')}.com",
            "industry": "Technology",
            "size": "1000-5000 employees",
            "founded": "2010",
            "revenue": "$100M - $500M",
            "headquarters": "San Francisco, CA",
            "mission": f"To innovate and create value for {company} customers",
            "values": ["Innovation", "Excellence", "Collaboration"],
            "benefits": ["Health Insurance", "401k", "Remote Work"],
            "workLifeBalance": 4.0,
            "cultureAndValues": 4.2,
            "careerOpportunities": 4.1,
            "compensationAndBenefits": 4.0,
            "seniorManagement": 3.8,
            "overallRating": 4.0,
            "totalReviews": 500,
            "recommendToFriend": 80,
            "ceoApproval": 85
        }
        
    except Exception as e:
        logger.error(f"Error getting company info: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get company information")

@router.get("/reviews")
async def get_company_reviews(
    company: str = Query(..., description="Company name"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Reviews per page"),
    rating: Optional[int] = Query(None, ge=1, le=5, description="Filter by rating"),
    jobTitle: Optional[str] = Query(None, description="Filter by job title"),
    location: Optional[str] = Query(None, description="Filter by location"),
    employmentStatus: Optional[str] = Query(None, description="Filter by employment status"),
    sentiment: Optional[str] = Query(None, description="Filter by sentiment"),
    current_user: User = Depends(get_current_user)
):
    """Get company reviews from Glassdoor"""
    try:
        # Try to get real data from Glassdoor API
        params = {
            "action": "reviews",
            "t.p": GLASSDOOR_PARTNER_ID,
            "t.k": GLASSDOOR_API_KEY,
            "userip": "0.0.0.0",
            "useragent": "Mozilla/5.0",
            "v": "1",
            "format": "json",
            "employerId": company,
            "jobTitle": jobTitle or "",
            "location": location or "",
            "employmentStatus": employmentStatus or "",
            "page": page,
            "limit": limit
        }
        
        api_data = await call_glassdoor_api("reviews", params)
        
        if api_data and api_data.get("response", {}).get("reviews"):
            # Process real Glassdoor reviews
            reviews_data = api_data["response"]["reviews"]
            reviews = []
            
            for review in reviews_data:
                # Apply filters
                if rating and review.get("rating") != rating:
                    continue
                if sentiment and review.get("sentiment") != sentiment:
                    continue
                
                reviews.append({
                    "id": review.get("id"),
                    "author": review.get("reviewerName", "Anonymous"),
                    "title": review.get("reviewTitle"),
                    "pros": review.get("pros"),
                    "cons": review.get("cons"),
                    "advice": review.get("advice"),
                    "rating": review.get("rating"),
                    "date": review.get("reviewDate"),
                    "jobTitle": review.get("jobTitle"),
                    "location": review.get("location"),
                    "employmentStatus": review.get("employmentStatus"),
                    "helpfulCount": review.get("helpfulCount", 0),
                    "isVerified": review.get("isVerified", False),
                    "sentiment": review.get("sentiment", "neutral")
                })
            
            return {
                "reviews": reviews,
                "total": len(reviews),
                "page": page,
                "totalPages": (len(reviews) + limit - 1) // limit
            }
        
        # Fallback to mock data
        company_key = company.title()
        if company_key in MOCK_REVIEWS:
            reviews = MOCK_REVIEWS[company_key]
        else:
            # Generate generic mock reviews
            reviews = [
                {
                    "id": f"review-{i}",
                    "author": "Anonymous Employee",
                    "title": f"Review {i} for {company}",
                    "pros": "Good benefits, flexible hours, great team",
                    "cons": "Sometimes long hours, high pressure",
                    "advice": "Be prepared to work hard",
                    "rating": 4,
                    "date": "2024-01-15",
                    "jobTitle": "Software Engineer",
                    "location": "San Francisco, CA",
                    "employmentStatus": "Full-time",
                    "helpfulCount": 10,
                    "isVerified": True,
                    "sentiment": "positive"
                }
                for i in range(1, 6)
            ]
        
        # Apply filters
        if rating:
            reviews = [r for r in reviews if r["rating"] == rating]
        if sentiment:
            reviews = [r for r in reviews if r["sentiment"] == sentiment]
        
        # Pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_reviews = reviews[start_idx:end_idx]
        
        return {
            "reviews": paginated_reviews,
            "total": len(reviews),
            "page": page,
            "totalPages": (len(reviews) + limit - 1) // limit
        }
        
    except Exception as e:
        logger.error(f"Error getting company reviews: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get company reviews")

@router.get("/culture")
async def get_company_culture(
    company: str = Query(..., description="Company name"),
    current_user: User = Depends(get_current_user)
):
    """Get company culture metrics from Glassdoor"""
    try:
        # Get company info first
        company_info = await get_company_info(company, None, current_user)
        
        # Generate culture metrics based on company info
        culture_metrics = {
            "overallRating": company_info.get("overallRating", 4.0),
            "totalReviews": company_info.get("totalReviews", 500),
            "categories": {
                "workLifeBalance": company_info.get("workLifeBalance", 4.0),
                "cultureAndValues": company_info.get("cultureAndValues", 4.0),
                "careerOpportunities": company_info.get("careerOpportunities", 4.0),
                "compensationAndBenefits": company_info.get("compensationAndBenefits", 4.0),
                "seniorManagement": company_info.get("seniorManagement", 4.0)
            },
            "trends": [
                {
                    "month": (datetime.now() - timedelta(days=30)).strftime("%Y-%m"),
                    "rating": company_info.get("overallRating", 4.0) - 0.1,
                    "reviewCount": max(1, company_info.get("totalReviews", 500) // 12)
                },
                {
                    "month": datetime.now().strftime("%Y-%m"),
                    "rating": company_info.get("overallRating", 4.0),
                    "reviewCount": max(1, company_info.get("totalReviews", 500) // 12)
                }
            ],
            "topBenefits": company_info.get("benefits", ["Health Insurance", "401k", "Remote Work"]),
            "topPros": ["Great culture", "Flexible hours", "Good pay", "Smart colleagues"],
            "topCons": ["Long hours", "High pressure", "Fast-paced environment"]
        }
        
        return culture_metrics
        
    except Exception as e:
        logger.error(f"Error getting company culture: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get company culture")

@router.get("/search")
async def search_companies(
    query: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Results per page"),
    location: Optional[str] = Query(None, description="Filter by location"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    current_user: User = Depends(get_current_user)
):
    """Search companies on Glassdoor"""
    try:
        # Try to get real data from Glassdoor API
        params = {
            "action": "employers",
            "q": query,
            "l": location or "",
            "page": page,
            "limit": limit
        }
        
        api_data = await call_glassdoor_api("employers", params)
        
        if api_data and api_data.get("response", {}).get("employers"):
            # Process real Glassdoor search results
            employers = api_data["response"]["employers"]
            companies = []
            
            for employer in employers:
                if industry and employer.get("industry") != industry:
                    continue
                    
                companies.append({
                    "id": employer.get("id"),
                    "name": employer.get("name"),
                    "website": employer.get("website"),
                    "industry": employer.get("industry"),
                    "size": employer.get("numberOfRatings"),
                    "founded": employer.get("yearFounded"),
                    "revenue": employer.get("revenue"),
                    "headquarters": employer.get("headquarters"),
                    "overallRating": employer.get("overallRating", 0),
                    "totalReviews": employer.get("numberOfRatings", 0)
                })
            
            return {
                "companies": companies,
                "total": len(companies),
                "page": page,
                "totalPages": (len(companies) + limit - 1) // limit
            }
        
        # Fallback to mock search results
        mock_companies = list(MOCK_COMPANY_DATA.values())
        filtered_companies = [
            company for company in mock_companies
            if query.lower() in company["name"].lower()
        ]
        
        # Apply industry filter
        if industry:
            filtered_companies = [
                company for company in filtered_companies
                if company["industry"].lower() == industry.lower()
            ]
        
        # Pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_companies = filtered_companies[start_idx:end_idx]
        
        return {
            "companies": paginated_companies,
            "total": len(filtered_companies),
            "page": page,
            "totalPages": (len(filtered_companies) + limit - 1) // limit
        }
        
    except Exception as e:
        logger.error(f"Error searching companies: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search companies")

@router.get("/statistics")
async def get_review_statistics(
    company: str = Query(..., description="Company name"),
    current_user: User = Depends(get_current_user)
):
    """Get review statistics for a company"""
    try:
        # Get company info and reviews
        company_info = await get_company_info(company, None, current_user)
        reviews_data = await get_company_reviews(company, 1, 100, None, None, None, None, None, current_user)
        
        # Calculate statistics
        reviews = reviews_data["reviews"]
        ratings = [review["rating"] for review in reviews]
        
        rating_distribution = {}
        for rating in range(1, 6):
            rating_distribution[rating] = ratings.count(rating)
        
        # Generate trends
        recent_trends = [
            {
                "month": (datetime.now() - timedelta(days=60)).strftime("%Y-%m"),
                "averageRating": company_info.get("overallRating", 4.0) - 0.1,
                "reviewCount": max(1, company_info.get("totalReviews", 500) // 12)
            },
            {
                "month": (datetime.now() - timedelta(days=30)).strftime("%Y-%m"),
                "averageRating": company_info.get("overallRating", 4.0) - 0.05,
                "reviewCount": max(1, company_info.get("totalReviews", 500) // 12)
            },
            {
                "month": datetime.now().strftime("%Y-%m"),
                "averageRating": company_info.get("overallRating", 4.0),
                "reviewCount": max(1, company_info.get("totalReviews", 500) // 12)
            }
        ]
        
        return {
            "totalReviews": company_info.get("totalReviews", 500),
            "averageRating": company_info.get("overallRating", 4.0),
            "ratingDistribution": rating_distribution,
            "recentTrends": recent_trends
        }
        
    except Exception as e:
        logger.error(f"Error getting review statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get review statistics")

@router.post("/reviews")
async def submit_review(
    review_data: ReviewSubmitRequest,
    current_user: User = Depends(get_current_user)
):
    """Submit a review for a company"""
    try:
        # In a real implementation, you would save this to your database
        # For now, we'll just return a success response
        
        review_id = f"review-{datetime.now().timestamp()}"
        
        logger.info(f"User {current_user.id} submitted review for {review_data.company}")
        
        return {
            "success": True,
            "reviewId": review_id,
            "message": "Review submitted successfully"
        }
        
    except Exception as e:
        logger.error(f"Error submitting review: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit review")

@router.post("/reviews/{review_id}/rate")
async def rate_review(
    review_id: str,
    rate_data: ReviewRateRequest,
    current_user: User = Depends(get_current_user)
):
    """Rate a review as helpful or not helpful"""
    try:
        # In a real implementation, you would update the review rating in your database
        # For now, we'll just return a success response
        
        logger.info(f"User {current_user.id} rated review {review_id} as {'helpful' if rate_data.helpful else 'not helpful'}")
        
        return {
            "success": True,
            "helpfulCount": 15  # Mock count
        }
        
    except Exception as e:
        logger.error(f"Error rating review: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to rate review")

@router.get("/compare")
async def compare_companies(
    companies: str = Query(..., description="Comma-separated list of company names"),
    current_user: User = Depends(get_current_user)
):
    """Compare multiple companies"""
    try:
        company_names = [name.strip() for name in companies.split(",")]
        
        if len(company_names) < 2:
            raise HTTPException(status_code=400, detail="At least 2 companies required for comparison")
        
        if len(company_names) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 companies allowed for comparison")
        
        # Get company data for each company
        companies_data = []
        for company_name in company_names:
            try:
                company_info = await get_company_info(company_name, None, current_user)
                companies_data.append(company_info)
            except Exception as e:
                logger.warning(f"Failed to get data for {company_name}: {str(e)}")
                continue
        
        if len(companies_data) < 2:
            raise HTTPException(status_code=400, detail="Could not get data for at least 2 companies")
        
        # Create comparison data
        comparison = {
            "overallRating": [c.get("overallRating", 0) for c in companies_data],
            "workLifeBalance": [c.get("workLifeBalance", 0) for c in companies_data],
            "cultureAndValues": [c.get("cultureAndValues", 0) for c in companies_data],
            "careerOpportunities": [c.get("careerOpportunities", 0) for c in companies_data],
            "compensationAndBenefits": [c.get("compensationAndBenefits", 0) for c in companies_data],
            "seniorManagement": [c.get("seniorManagement", 0) for c in companies_data]
        }
        
        return {
            "companies": companies_data,
            "comparison": comparison
        }
        
    except Exception as e:
        logger.error(f"Error comparing companies: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to compare companies") 