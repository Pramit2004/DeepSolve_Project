# 🚀 LinkedIn Insights Microservice

## 📋 Table of Contents

- [Features]
- [Tech Stack]
- [Architecture]
- [Prerequisites]
- [Installation]
- [Configuration]
- [Quick Start]
- [API Documentation]
- [Testing]
- [Troubleshooting]
- [Project Structure]
- [Contributing]
- [License]

---

## ✨ Features

### Core Features ✅
- 🔍 **LinkedIn Company Scraping**
  - Company profile (name, description, website, industry)
  - Follower count and employee count
  - Recent posts (15-25 posts)
  - Employee profiles
  - Post comments

- 💾 **Supabase Database Integration**
  - Persistent storage with relationships
  - PostgreSQL with proper schema design
  - Automatic data normalization

- 🔎 **Advanced Filtering**
  - Filter by follower count range (20k-40k)
  - Search by company name
  - Filter by industry
  - Pagination support

- 🤖 **AI-Powered Insights** (Bonus)
  - Company analysis using Google Gemini 2.0 Flash
  - Follower demographics analysis
  - Content strategy insights
  - Engagement metrics

- ⚡ **Performance Optimizations** (Bonus)
  - Async API operations
  - Efficient database queries
  - Smart caching strategies

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.109.0
- **Language**: Python 3.11+
- **Database**: Supabase (PostgreSQL)
- **Web Scraping**: Selenium + ChromeDriver
- **AI**: Google Gemini 2.0 Flash

### Key Libraries
```
fastapi==0.109.0
uvicorn==0.27.0
supabase==2.3.4
selenium==4.16.0
google-generativeai==0.3.2
pydantic==2.5.3
python-dotenv==1.0.0
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   API Layer  │  │   Services   │  │  AI Service  │      │
│  │  (Routes)    │→ │  (Scraper)   │→ │   (Gemini)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         ↓                  ↓                                 │
│  ┌──────────────────────────────────────────┐              │
│  │          Supabase Database                │              │
│  │  (pages, posts, employees, comments)      │              │
│  └──────────────────────────────────────────┘              │
│                                                               │
└─────────────────────────────────────────────────────────────┘
         ↓                                    ↓
    ┌─────────┐                          ┌─────────┐
    │LinkedIn │                          │ Gemini  │
    │  Pages  │                          │   API   │
    └─────────┘                          └─────────┘
```

### Database Schema

```sql
pages (1) ──────> (*) posts (1) ──────> (*) comments
  │
  └──────────────> (*) employees
```

---

## 📦 Prerequisites

Before you begin, ensure you have:

1. **Python 3.11+** installed
   ```bash
   python --version  # Should show 3.11 or higher
   ```

2. **Google Chrome** browser installed

3. **Supabase Account** (Free)
   - Sign up at [supabase.com](https://supabase.com)

4. **Google Gemini API Key** (Free)
   - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

5. **LinkedIn Account**
   - For scraping (preferably a test account)
   - 2FA disabled (or handle manually during login)

---

## 🚀 Installation

### Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd linkedin-insights
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Setup Supabase Database

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Create a new project (wait 2-3 minutes)
3. Go to **SQL Editor**
4. Open `supabase_schema.sql` and copy all SQL
5. Paste in SQL Editor and click **Run**
6. Verify tables created: `pages`, `posts`, `comments`, `employees`

### Step 5: Get API Keys

#### Supabase Keys:
1. Go to **Settings → API**
2. Copy:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: `eyJhbGci...`

#### Gemini API Key:
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click **Create API Key**
3. Copy the key (starts with `AIzaSy...`)

---

## ⚙️ Configuration

### Create .env File

```bash
# Copy example file
cp .env.example .env

# Edit with your credentials
nano .env  # or use any text editor
```

### .env Configuration

```bash
# Supabase (REQUIRED)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJ...

# LinkedIn Credentials (REQUIRED)
LINKEDIN_EMAIL=your.email@example.com
LINKEDIN_PASSWORD=your_password

# Google Gemini AI (REQUIRED for AI summaries)
GEMINI_API_KEY=AIzaSy...

# Application Settings
PORT=8000
HOST=0.0.0.0
DEBUG=True
```

---

## 🎯 Quick Start

### Option 1: Test Scraper First (Recommended)

```bash
# Run diagnostic
python diagnose.py

# Test scraper
python test_scraper.py
```

This will:
- ✅ Check all dependencies
- ✅ Test LinkedIn login
- ✅ Scrape 3 test companies
- ✅ Save debug screenshots

### Option 2: Start API Directly

```bash
# Run the application
python main.py
```

You should see:
```
✅ Connected to Supabase
✅ Gemini AI initialized
🚀 LinkedIn Insights API v2.0
📍 Server: http://localhost:8000
📚 API Docs: http://localhost:8000/docs
```

### Access the Application

- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

---

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication
No authentication required (for now)

---

### Endpoints

#### 1. Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "database": "Supabase",
  "ai": "Gemini"
}
```

---

#### 2. Get Company Page

```http
GET /api/v1/pages/{page_id}
```

**Parameters:**
- `page_id` (path): LinkedIn company ID (e.g., "google", "microsoft")
- `include_posts` (query): Include posts (default: true)
- `include_employees` (query): Include employees (default: true)
- `force_rescrape` (query): Re-scrape even if in DB (default: false)

**Example:**
```bash
curl http://localhost:8000/api/v1/pages/google
```

**Response:**
```json
{
  "id": "uuid",
  "page_id": "google",
  "name": "Google",
  "url": "https://www.linkedin.com/company/google/",
  "description": "A problem isn't truly solved until it's solved for all...",
  "industry": "Software Development",
  "followers_count": 30500000,
  "employees_count": 150000,
  "website": "https://www.google.com",
  "posts": [...],
  "employees": [...]
}
```

---

#### 3. List All Pages (with Filters)

```http
GET /api/v1/pages
```

**Query Parameters:**
- `skip`: Offset for pagination (default: 0)
- `limit`: Max results (default: 10, max: 100)
- `min_followers`: Minimum follower count
- `max_followers`: Maximum follower count
- `industry`: Filter by industry (partial match)
- `name_search`: Search by name (partial match)

**Examples:**

```bash
# Get all pages
curl http://localhost:8000/api/v1/pages

# Filter by follower range (20k-40k)
curl "http://localhost:8000/api/v1/pages?min_followers=20000&max_followers=40000"

# Search by name
curl "http://localhost:8000/api/v1/pages?name_search=tech"

# Filter by industry
curl "http://localhost:8000/api/v1/pages?industry=software"

# Pagination
curl "http://localhost:8000/api/v1/pages?skip=10&limit=20"
```

---

#### 4. Get Company Posts

```http
GET /api/v1/pages/{page_id}/posts
```

**Parameters:**
- `skip`: Offset (default: 0)
- `limit`: Max results (default: 15, max: 25)

**Example:**
```bash
curl http://localhost:8000/api/v1/pages/google/posts
```

**Response:**
```json
[
  {
    "id": "uuid",
    "page_id": "page_uuid",
    "post_id": "google_post_1",
    "content": "Exciting news from Google...",
    "posted_at": "2024-12-10T10:00:00",
    "likes_count": 15000,
    "comments_count": 250,
    "shares_count": 0,
    "post_url": "https://linkedin.com/posts/..."
  }
]
```

---

#### 5. Get Company Employees

```http
GET /api/v1/pages/{page_id}/employees
```

**Parameters:**
- `skip`: Offset (default: 0)
- `limit`: Max results (default: 50, max: 100)

**Example:**
```bash
curl http://localhost:8000/api/v1/pages/google/employees
```

---

#### 6. Generate AI Summary ⭐

```http
POST /api/v1/pages/{page_id}/summary
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/pages/google/summary
```

**Response:**
```json
{
  "page_id": "google",
  "page_name": "Google",
  "summary": "Google is a leading technology company...",
  "follower_analysis": "With over 30M followers, Google has one of the largest corporate presences on LinkedIn...",
  "content_analysis": "Posts regularly with a mix of product updates, company culture, and industry insights...",
  "engagement_insights": "Average engagement of 15K+ likes per post with strong community interaction...",
  "page_type": "Highly active enterprise presence with consistent engagement",
  "generated_at": "2024-12-14T10:00:00"
}
```

---

#### 7. Get Page Statistics

```http
GET /api/v1/stats/{page_id}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/stats/google
```

**Response:**
```json
{
  "page_id": "google",
  "page_name": "Google",
  "in_database": true,
  "counts": {
    "posts": 15,
    "employees": 20,
    "comments": 0
  },
  "company_info": {
    "followers": 30500000,
    "employees_count": 150000,
    "industry": "Software Development"
  }
}
```

---

#### 8. Debug Endpoint

```http
GET /api/v1/debug/{page_id}
```

Check if scraper is working properly.

---

## 🧪 Testing

### Manual Testing

```bash
# 1. Test health
curl http://localhost:8000/health

# 2. Scrape a company
curl http://localhost:8000/api/v1/pages/google

# 3. List all companies
curl http://localhost:8000/api/v1/pages

# 4. Filter by followers
curl "http://localhost:8000/api/v1/pages?min_followers=1000000"

# 5. Get posts
curl http://localhost:8000/api/v1/pages/google/posts

# 6. Generate AI summary
curl -X POST http://localhost:8000/api/v1/pages/google/summary
```

### Using Postman

1. Import `postman_collection.json` (if provided)
2. Set environment variable `base_url` = `http://localhost:8000`
3. Run requests

### Automated Tests

```bash
# Run test suite
pytest

# Run with coverage
pytest --cov=app tests/
```

---

## 🐛 Troubleshooting

### Common Issues

#### Issue 1: "Company page not found"

**Symptoms:**
```
❌ Company page not found
❌ Failed to scrape meta
```

**Solutions:**
1. **Run diagnostic:**
   ```bash
   python diagnose.py
   ```

2. **Test scraper with visible browser:**
   ```bash
   python test_scraper.py
   ```

3. **Check if logged in:**
   - LinkedIn login might have failed
   - 2FA verification needed
   - Increase wait time in `login()` method

4. **Try with headless=False:**
   - See what's actually happening
   - Check if you're being redirected

---

#### Issue 2: Data not storing in Supabase

**Symptoms:**
```
⚠️ No data returned from insert
```

**Solutions:**
1. **Check Supabase connection:**
   ```bash
   # Test connection
   python -c "from supabase import create_client; import os; from dotenv import load_dotenv; load_dotenv(); client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY')); print('✅ Connected')"
   ```

2. **Verify table structure:**
   - Go to Supabase → Table Editor
   - Check if tables exist: pages, posts, employees, comments

3. **Check for data type mismatches:**
   - Look at console errors
   - Verify field types match schema

---

#### Issue 3: ChromeDriver errors

**Symptoms:**
```
SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version XX
```

**Solutions:**
```bash
# Update webdriver-manager
pip install --upgrade webdriver-manager

# Or manually download matching ChromeDriver
# https://chromedriver.chromium.org/downloads
```

---

#### Issue 4: AI Summary not working

**Symptoms:**
```
⚠️ GEMINI_API_KEY not set
```

**Solutions:**
1. Check `.env` file has `GEMINI_API_KEY`
2. Get new key from https://makersuite.google.com/app/apikey
3. Verify key starts with `AIzaSy...`
4. Restart application after adding key

---

#### Issue 5: Followers showing wrong value

**Symptoms:**
```
followers_count: null
or
followers: "Software Development"
```

**Solutions:**
- ✅ Use the updated `linkedin_custom_scraper.py`
- CSS selectors have been fixed
- Re-scrape with `force_rescrape=true`

---

### Debug Mode

Enable debug mode to save screenshots and HTML:

```python
# In linkedin_custom_scraper.py
data = scraper.scrape_company_page("google", debug=True)
```

This creates:
- `google_debug.png` - Screenshot of what scraper sees
- `google_source.html` - Full HTML source

---

## 📁 Project Structure

```
linkedin-insights/
├── main.py                      # FastAPI application
├── linkedin_custom_scraper.py   # Selenium scraper
├── requirements.txt             # Python dependencies
├── .env                        # Environment variables (not in git)
├── .env.example                # Example env file
├── supabase_schema.sql         # Database schema
├── diagnose.py                 # Diagnostic script
├── test_scraper.py             # Test scraper script
├── README.md                   # This file
├── SETUP_GUIDE.md             # Detailed setup guide
└── postman_collection.json    # Postman API collection (optional)
```

---

## 🔐 Security & Best Practices

### Environment Variables
- ✅ Never commit `.env` file to git
- ✅ Use `.env.example` as template
- ✅ Rotate API keys regularly

### LinkedIn Scraping
- ⚠️ Use a test account, not your main account
- ⚠️ Respect rate limits
- ⚠️ Add delays between requests
- ⚠️ LinkedIn may block automated access

### Database
- ✅ Use Row Level Security (RLS) in Supabase
- ✅ Keep Supabase key secure
- ✅ Regular backups

### API Security (Production)
- 🔒 Add authentication (JWT tokens)
- 🔒 Implement rate limiting
- 🔒 Use HTTPS
- 🔒 Input validation

---

## 🚀 Deployment

### Deploy to Heroku

```bash
# Login
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set SUPABASE_URL=your_url
heroku config:set SUPABASE_KEY=your_key
heroku config:set LINKEDIN_EMAIL=your_email
heroku config:set LINKEDIN_PASSWORD=your_password
heroku config:set GEMINI_API_KEY=your_key

# Deploy
git push heroku main
```

### Deploy to Railway

1. Connect GitHub repo
2. Add environment variables
3. Deploy automatically

### Deploy to Render

1. Connect GitHub repo
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables

---

## 📊 Performance Considerations

### Scraping Performance
- Async operations throughout
- Parallel scraping for multiple companies
- Smart caching to avoid re-scraping

### Database Performance
- Indexed columns for fast queries
- Efficient joins with proper relationships
- Pagination to limit large responses

### API Performance
- FastAPI's async capabilities
- Background tasks for long operations
- Response compression

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8
- Add docstrings
- Write tests for new features
- Update README for API changes

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.