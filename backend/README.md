# Buzz2Remote Backend

## Overview
Backend API for Buzz2Remote job aggregation platform.

## Features
- Job CRUD operations
- Search and filtering
- Authentication
- Payment processing
- Admin panel

## Quick Start

### Prerequisites
- Python 3.11+
- MongoDB (local or Atlas)
- OpenAI API Key (optional)

### Installation
1. Install dependencies: `pip install -r ../config/requirements.txt`
2. Configure environment variables
3. Run the application: `uvicorn main:app --reload --port 8001`

## Testing
Run tests: `python -m pytest tests/`

## API Documentation
Access at: `http://localhost:5000/docs` 