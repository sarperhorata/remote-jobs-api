# Buzz2Remote

Buzz2Remote is a platform that helps users find remote job opportunities by crawling various job boards and company career pages.

## Features

- Automated job scraping from multiple sources
- API for fetching job listings
- User authentication and profile management
- Dashboard to track job applications
- Mobile-friendly responsive design

## Tech Stack

### Backend
- Python 3.11
- FastAPI
- MongoDB (optional)
- Redis for caching
- JWT authentication

### Frontend
- React 18
- TypeScript
- React Query
- React Router
- Material UI components

## Setup

### Prerequisites
- Python 3.11 or higher
- Node.js 14 or higher
- npm or yarn

### Backend Setup
1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Copy the example environment file and configure it:
   ```
   cp .env.example .env
   ```

5. Run the server:
   ```
   uvicorn main:app --reload
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   # or
   yarn install
   ```

3. Create a `.env` file with the following content:
   ```
   REACT_APP_API_URL=http://localhost:5000
   ```

4. Start the development server:
   ```
   npm start
   # or
   yarn start
   ```

## Deployment

The project is set up for automatic deployment:
- Backend: Render
- Frontend: Netlify
- Continuous Integration: GitHub Actions

## Current Status

The project has been successfully set up with:

1. **Backend**: FastAPI application running on port 5001
   - API documentation available at http://localhost:5001/docs
   - Health check endpoint implemented

2. **Frontend**: React application running on port 3000
   - Connected to the backend API
   - Basic pages and components created

## Next Steps

1. **Backend Development**:
   - Implement authentication endpoints (login, register)
   - Set up database integration
   - Create job crawling functionality

2. **Frontend Development**:
   - Complete user authentication flow
   - Implement job listing and filtering
   - Create user profile and dashboard

3. **Deployment**:
   - Configure CI/CD with GitHub Actions
   - Deploy backend to Render
   - Deploy frontend to Netlify
   - Set up automatic deployments

## Accessing the Application

- Backend API: http://localhost:5001
- Frontend: http://localhost:3000
- API Documentation: http://localhost:5001/docs

## License

This project is licensed under the MIT License - see the LICENSE file for details. 