# 🚀 Buzz2Remote - Remote Jobs Platform

A comprehensive remote job platform that aggregates opportunities from 471+ companies worldwide with AI-powered features and advanced admin management.

## ✨ Features

### 🤖 AI-Powered Features
- **Enhanced CV Parsing** with OpenAI GPT-4o Mini integration
- **Intelligent Skill Extraction** from resumes and job descriptions
- **Multi-language Support** for international candidates
- **Automatic Profile Completion** with confidence scoring

### 🕷️ Advanced Job Crawling
- **471+ Company Integration** from major remote-first companies
- **Daily Automated Crawling** with intelligent deduplication
- **Multiple Source Aggregation** (Lever, Greenhouse, Workable, etc.)
- **Real-time Job Quality Metrics** and validation

### 👤 User Management
- **Secure Authentication** with JWT tokens and email verification
- **LinkedIn OAuth Integration** for seamless profile import
- **CV Upload & Parsing** with multiple format support (PDF, DOC, DOCX)
- **Profile Image Control** for application compliance

### 📊 Admin Panel
- **Real-time Dashboard** with live statistics and metrics
- **Process Management** with background task monitoring
- **Job & Company Management** with real MongoDB data
- **API Services Monitoring** with rate limiting and status tracking
- **Quick Actions** for crawler, external APIs, and position analysis

### 🔐 Security & Compliance
- **Enterprise-grade Security** with rate limiting and validation
- **GDPR Compliance** with data privacy controls
- **Email Verification** and two-factor authentication support
- **API Key Management** for third-party integrations

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.11+
- **Database**: MongoDB with Atlas/Local fallback
- **AI/ML**: OpenAI GPT-4o Mini, Custom NLP models
- **Authentication**: JWT, OAuth 2.0 (LinkedIn)
- **Admin Panel**: FastAPI + HTML/CSS/JS with real-time monitoring
- **Deployment**: Render, Docker, CI/CD pipeline
- **Monitoring**: Comprehensive logging and error tracking

## 📈 Performance

- **21,000+ Jobs** processed daily
- **471+ Companies** integrated
- **Sub-second API Response** times
- **99.9% Uptime** with monitoring
- **Scalable Architecture** for enterprise use

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- MongoDB (local or Atlas)
- OpenAI API Key (optional, for AI features)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/sarperhorata/buzz2remote.git
cd buzz2remote
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp env.example .env
# Edit .env with your configuration
```

5. **Start MongoDB** (if using local)
```bash
mongod --dbpath /path/to/your/db
```

6. **Run the application**
```bash
cd backend
python main.py
```

The API will be available at `http://localhost:5001`

### Admin Panel Access

- **Dashboard**: `http://localhost:5001/admin/dashboard`
- **Jobs Management**: `http://localhost:5001/admin/jobs`
- **Companies**: `http://localhost:5001/admin/companies`
- **API Services**: `http://localhost:5001/admin/apis`
- **API Documentation**: `http://localhost:5001/docs`

## 📊 Admin Panel Features

### Dashboard
- **Real-time Statistics**: Total jobs, companies, active APIs, daily jobs
- **Recent Jobs**: Latest job postings with source tracking
- **Quick Actions**: One-click crawler, API fetch, and analysis
- **Process Monitoring**: Real-time CPU/memory usage tracking

### Job Management
- **Live Job Data**: Direct MongoDB integration
- **Source Tracking**: Monitor job sources and quality
- **Bulk Operations**: Mass job management capabilities

### Company Management
- **Company Analytics**: Job counts and activity tracking
- **Website Integration**: Direct links to company career pages
- **Growth Metrics**: Company hiring trends

### API Services
- **Rate Limit Monitoring**: Track API usage and quotas
- **Status Dashboard**: Real-time API health monitoring
- **Performance Metrics**: Response times and success rates

## 🔧 Configuration

### Environment Variables

```bash
# Database
MONGODB_URL=mongodb://localhost:27017/buzz2remote

# API Keys
OPENAI_API_KEY=your_openai_api_key
RAPIDAPI_KEY=your_rapidapi_key

# Security
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret

# Application
DEBUG=False
API_HOST=0.0.0.0
API_PORT=5001
```

## 🚀 Deployment

### Render Deployment

1. **Connect your GitHub repository** to Render
2. **Set environment variables** in Render dashboard
3. **Deploy automatically** with the included `render.yaml`

### Manual Deployment

```bash
# Build and run
pip install -r requirements.txt
cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/register` - User registration with AI profile completion
- `POST /api/token` - JWT authentication
- `POST /api/upload-cv-enhanced` - AI-powered CV parsing

### Job Endpoints
- `GET /api/jobs` - Advanced job search with filtering
- `GET /api/jobs/{id}` - Job details with similar recommendations
- `POST /api/jobs/{id}/apply` - Job application submission

### Admin Endpoints
- `GET /admin/dashboard` - Admin dashboard
- `POST /admin/actions/run-crawler` - Trigger job crawler
- `POST /admin/actions/fetch-external-apis` - Fetch from external APIs
- `GET /admin/actions/status/{process_id}` - Monitor process status

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Live Demo**: [https://buzz2remote.netlify.app](https://buzz2remote.netlify.app)
- **API Documentation**: [https://buzz2remote-api.onrender.com/docs](https://buzz2remote-api.onrender.com/docs)
- **Admin Panel**: [https://buzz2remote-api.onrender.com/admin/dashboard](https://buzz2remote-api.onrender.com/admin/dashboard)

## 📞 Support

For support, email support@buzz2remote.com or create an issue on GitHub.

---

**Built with ❤️ for the remote work community** 

## Directory Structure

```
buzz2remote/
├── frontend/           # React frontend
├── backend/           # FastAPI backend
├── admin_panel/       # Admin panel templates and static files
├── nginx.conf         # Nginx configuration
├── docker-compose.yml # Docker Compose configuration
├── setup-ssl.sh       # SSL setup script
└── README.md          # This file
```

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/sarperhorata/buzz2remote.git
cd buzz2remote
```

2. Create a `.env` file in the root directory with the following variables:
```env
MONGODB_URI=mongodb://localhost:27017/buzz2remote
JWT_SECRET=your-secret-key
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

3. Build and start the services:
```bash
docker-compose up -d
```

4. Set up SSL certificates:
```bash
./setup-ssl.sh
```

## Accessing the Services

- Frontend: https://buzz2remote.com
- API Documentation: https://buzz2remote.com/docs
- Admin Panel: https://buzz2remote.com/admin
- API Endpoints: https://buzz2remote.com/api

## Development

1. Frontend development:
```bash
cd frontend
npm install
npm start
```

2. Backend development:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

## Deployment

The application is configured to be deployed on any server with Docker and Docker Compose installed. The nginx configuration handles routing for all services, and SSL certificates are automatically managed by Let's Encrypt.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details 