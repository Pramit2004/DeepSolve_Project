# 🚀 LinkedIn Insights Microservice

A robust, scalable FastAPI-based microservice for fetching and analyzing LinkedIn company page data.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Deployment](#deployment)

---

## ✨ Features

### Mandatory Features ✅
- ✅ Multi-method LinkedIn scraping (Proxycurl API, RapidAPI, Custom Selenium)
- ✅ PostgreSQL database with proper entity relationships
- ✅ RESTful API with pagination and filtering
- ✅ Fetch company details, posts, comments, and employees
- ✅ Advanced filtering (follower range, industry, name search)
- ✅ Postman collection included

### Bonus Features 🎁
- ✅ AI-powered company summaries (OpenAI/Anthropic)
- ✅ Async programming throughout
- ✅ Redis caching with configurable TTL
- ✅ Docker containerization
- ✅ Cloud storage support (AWS S3, Google Cloud Storage)
- ✅ Comprehensive error handling
- ✅ Health check endpoints

---

## 🏗️ Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│      FastAPI Application        │
│  ┌──────────────────────────┐  │
│  │   API Routes Layer       │  │
│  └──────────┬───────────────┘  │
│             │                   │
│  ┌──────────▼───────────────┐  │
│  │   Business Logic Layer   │  │
│  │  • ScraperService        │  │
│  │  • CacheService          │  │
│  │  • AISummaryService      │  │
│  └──────────┬───────────────┘  │
│             │                   │
│  ┌──────────▼───────────────┐  │
│  │   Data Access Layer      │  │
│  │  • SQLAlchemy Models     │  │
│  └──────────┬───────────────┘  │
└─────────────┼───────────────────┘
              │
     ┌────────┴────────┐
     ▼                 ▼
┌─────────┐      ┌─────────┐
│PostgreSQL│      │  Redis  │
└─────────┘      └─────────┘
```

### Database Schema

```sql
pages (1) ──────> (*) posts (1) ──────> (*) comments
  │
  └──────────────> (*) employees
```

---

## 📦 Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)
- LinkedIn API Key (Proxycurl recommended)

---

## 🔧 Installation

### Option 1: Local Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd linkedin-insights

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python -c "from main import Base, engine; Base.metadata.create_all(bind=engine)"

# Run the application
python main.py
```

### Option 2: Docker Setup (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd linkedin-insights

# Create .env file
cp .env.example .env
# Edit .env with your API keys

# Build and run with Docker Compose
docker-compose up --build

# Access the API at http://localhost:8000
```

---

## ⚙️ Configuration

### Required Environment Variables

Create a `.env` file with the following:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/linkedin_insights

# Redis
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=300

# API Keys (at least one required)
PROXYCURL_API_KEY=your_proxycurl_key_here
RAPIDAPI_KEY=your_rapidapi_key_here

# AI Services (optional - for bonus features)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Application
SCRAPING_METHOD=proxycurl
DEBUG=True
PORT=8000
```

### Getting API Keys

1. **Proxycurl (Recommended)** - https://nubela.co/proxycurl/
   - Sign up for free tier (10 credits)
   - Most reliable for LinkedIn data
   
2. **RapidAPI** - https://rapidapi.com/
   - Search for "LinkedIn" scrapers
   - Multiple options available

---

## 🚀 Usage

### Quick Start

```bash
# Start the server
python main.py

# Or with uvicorn directly
uvicorn main:app --reload

# Access API documentation
http://localhost:8000/docs
```

### Test the Scraper First

Before running the full application, test if your API can fetch LinkedIn data:

```bash
# Run the test script
python linkedin_scraper_test.py

# Or test specific company
python -c "from linkedin_scraper_test import test_all_methods; test_all_methods('https://www.linkedin.com/company/deepsolv/')"
```

---

## 📡 API Endpoints

### Core Endpoints

#### 1. Get Page Details
```http
GET /api/v1/pages/{page_id}
```

**Parameters:**
- `page_id` (path): LinkedIn company page ID (e.g., "deepsolv")
- `include_posts` (query): Include posts (default: true)
- `include_employees` (query): Include employees (default: false)

**Example:**
```bash
curl http://localhost:8000/api/v1/pages/deepsolv
```

**Response:**
```json
{
  "id": 1,
  "page_id": "deepsolv",
  "name": "DeepSolv",
  "url": "https://www.linkedin.com/company/deepsolv/",
  "description": "AI-powered solutions...",
  "industry": "Technology",
  "followers_count": 15000,
  "employees_count": 50,
  "posts": [...],
  "employees": [...]
}
```

#### 2. List Pages with Filters
```http
GET /api/v1/pages
```

**Parameters:**
- `skip` (query): Pagination offset (default: 0)
- `limit` (query): Max results (default: 10, max: 100)
- `min_followers` (query): Minimum follower count
- `max_followers` (query): Maximum follower count
- `industry` (query): Filter by industry
- `name_search` (query): Search by name

**Example:**
```bash
# Find pages with 20k-40k followers
curl "http://localhost:8000/api/v1/pages?min_followers=20000&max_followers=40000"

# Search by name
curl "http://localhost:8000/api/v1/pages?name_search=tech"

# Filter by industry
curl "http://localhost:8000/api/v1/pages?industry=software"
```

#### 3. Get Page Posts
```http
GET /api/v1/pages/{page_id}/posts
```

**Parameters:**
- `skip` (query): Pagination offset (default: 0)
- `limit` (query): Max results (default: 15, max: 25)

**Example:**
```bash
curl http://localhost:8000/api/v1/pages/deepsolv/posts
```

#### 4. Get Page Employees
```http
GET /api/v1/pages/{page_id}/employees
```

**Example:**
```bash
curl http://localhost:8000/api/v1/pages/deepsolv/employees
```

#### 5. Generate AI Summary (Bonus)
```http
POST /api/v1/pages/{page_id}/summary
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/pages/deepsolv/summary
```

**Response:**
```json
{
  "page_id": "deepsolv",
  "summary": "DeepSolv is a technology company...",
  "follower_analysis": "Total followers: 15,000",
  "content_type": "Professional content",
  "engagement_insights": "High engagement on technical posts",
  "generated_at": "2024-12-13T10:30:00"
}
```

#### 6. Health Check
```http
GET /health
```

#### 7. Clear Cache
```http
POST /api/v1/cache/clear
```

---

## 🧪 Testing

### Manual Testing with cURL

```bash
# Test health endpoint
curl http://localhost:8000/health

# Fetch a company page
curl http://localhost:8000/api/v1/pages/microsoft

# Filter pages by followers
curl "http://localhost:8000/api/v1/pages?min_followers=10000&max_followers=50000"

# Get posts for a page
curl http://localhost:8000/api/v1/pages/microsoft/posts
```

### Testing with Postman

1. Import the `postman_collection.json` file
2. Set environment variables:
   - `BASE_URL`: `http://localhost:8000`
3. Run the collection

### Automated Tests

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

---

## 🐳 Docker Deployment

### Build and Run

```bash
# Build the image
docker build -t linkedin-insights .

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Docker Hub Deployment

```bash
# Tag the image
docker tag linkedin-insights yourusername/linkedin-insights:latest

# Push to Docker Hub
docker push yourusername/linkedin-insights:latest
```

---

## 🌐 Cloud Deployment

### Deploy to Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Add Redis
heroku addons:create heroku-redis:hobby-dev

# Set environment variables
heroku config:set PROXYCURL_API_KEY=your_key

# Deploy
git push heroku main
```

### Deploy to AWS ECS/Fargate

1. Push Docker image to ECR
2. Create ECS task definition
3. Configure RDS for PostgreSQL
4. Configure ElastiCache for Redis
5. Deploy using ECS service

### Deploy to Google Cloud Run

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/linkedin-insights

# Deploy
gcloud run deploy linkedin-insights \
  --image gcr.io/PROJECT_ID/linkedin-insights \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## 📊 Performance & Caching

### Caching Strategy

- **Cache TTL**: 5 minutes (configurable)
- **Cache Keys**: `page:{page_id}`
- **Cache Storage**: Redis

### Performance Tips

1. Enable caching for frequently accessed pages
2. Use pagination for large result sets
3. Use `include_posts=false` if posts aren't needed
4. Configure connection pooling for database

---

## 🔒 Security Best Practices

1. **API Keys**: Never commit API keys to git
2. **Environment Variables**: Use `.env` for local, secrets management for production
3. **Rate Limiting**: Implement rate limiting for production
4. **CORS**: Configure CORS properly for your frontend
5. **Authentication**: Add JWT authentication for production use

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Database Connection Error
```bash
# Check if PostgreSQL is running
docker-compose ps
# Or
psql -U postgres -h localhost
```

#### 2. Redis Connection Error
```bash
# Check Redis
redis-cli ping
```

#### 3. Scraping Fails
```bash
# Test scraper directly
python linkedin_scraper_test.py
```

#### 4. API Key Invalid
- Verify API key in `.env`
- Check API credit balance
- Test API key directly with curl

---

## 📈 Monitoring

### Health Checks

```bash
# Application health
curl http://localhost:8000/health

# Database health
docker-compose exec db pg_isready

# Redis health
docker-compose exec redis redis-cli ping
```

### Logs

```bash
# Application logs
docker-compose logs -f api

# Database logs
docker-compose logs -f db

# All logs
docker-compose logs -f
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

---

## 📝 License

MIT License - see LICENSE file for details

---

## 🙏 Acknowledgments

- FastAPI framework
- Proxycurl API
- SQLAlchemy ORM
- Redis caching

---

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Email: your.email@example.com

---

## 🎯 Next Steps

1. **Test the scraper** with `linkedin_scraper_test.py`
2. **Set up API keys** in `.env`
3. **Run the application** with Docker or locally
4. **Access API docs** at `http://localhost:8000/docs`
5. **Test endpoints** with Postman or cURL
6. **Deploy to cloud** when ready

---

**Built with ❤️ for the GenAI Developer Intern Assignment**