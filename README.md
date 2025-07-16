# 🚀 Buzz2Remote v2 - AI-Powered Remote Job Platform

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/buzz2remote) 
[![Version](https://img.shields.io/badge/version-2.0.0-blue)](https://github.com/buzz2remote)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Modern, AI-powered remote job platform that connects talented professionals with global opportunities.

## 🌟 Key Features

- **AI-Powered Job Matching** - Smart recommendations based on skills and preferences
- **Multi-Position Search** - Search for up to 10 different job titles simultaneously  
- **Auto-Apply System** - Automated job application with form analysis
- **Real-time Updates** - Live job feeds from 8+ external APIs
- **Advanced Filtering** - Location, salary, company, skills-based filtering
- **Responsive Design** - Optimized for desktop and mobile devices

## 📁 Project Structure v2

```
buzz2remote/
├── backend/           # FastAPI backend application
├── frontend/          # React frontend application  
├── config/            # All configuration files
├── docs/              # Documentation and guides
├── tools/             # Utility scripts and tools
├── scripts/           # Automation and setup scripts
├── data/              # Data files and archives
├── temp/              # Temporary files and builds
├── .git/              # Git repository
├── .github/           # GitHub configuration
├── .venv/             # Python virtual environment
└── README.md          # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB Atlas account
- Environment variables (see `config/`)

### Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r ../config/requirements.txt
uvicorn main:app --reload --port 8001
```

### Frontend Setup  
```bash
cd frontend
npm install
npm run dev  # Starts on port 3000
```

## 🔧 Configuration

All configuration files are located in the `config/` directory:

- `config/.env` - Environment variables
- `config/docker-compose.yml` - Docker configuration
- `config/netlify.toml` - Netlify deployment settings
- `config/nginx.conf` - Nginx configuration
- `config/requirements.txt` - Python dependencies

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- `docs/SETUP_INSTRUCTIONS.md` - Detailed setup guide
- `docs/EXTERNAL_API_INTEGRATION.md` - API integration guide
- `docs/ADMIN_PANEL_IMPROVEMENTS.md` - Admin panel features

## 🛠️ Development Tools

The `tools/` directory contains various utilities:

- Database management scripts
- Test automation tools  
- API integration tools
- Monitoring and health check scripts

## 🌐 Live URLs

- **Production**: https://buzz2remote.com
- **API**: https://buzz2remote-api.onrender.com
- **Admin Panel**: https://buzz2remote.com/admin

## 🔑 Admin Access

- **Email**: admin@buzz2remote.com
- **Password**: Contact administrators

## 🎯 API Features

- **Real-time Job Search** - `/api/jobs/search`
- **Company Statistics** - `/api/companies/statistics`  
- **AI Recommendations** - `/api/ai/recommendations`
- **Auto-Apply System** - `/api/auto-apply/*`
- **Admin Panel** - `/admin/*`

## 📊 Performance

- **Test Coverage**: 90%+ (Frontend & Backend)
- **API Response Time**: <200ms average
- **Database**: MongoDB Atlas (Cloud)
- **CDN**: Netlify Edge

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests: `npm test` (frontend) and `pytest` (backend)
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🏆 Team

Built by the Buzz2Remote development team with ❤️

---

**🚀 Ready to find your next remote opportunity? Visit [Buzz2Remote](https://buzz2remote.com)** # Deploy test Thu Jul 17 00:47:43 +03 2025
