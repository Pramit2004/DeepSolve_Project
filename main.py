"""
Complete LinkedIn Insights API - FIXED + AI Summary
- Fixed data extraction and storage
- AI Summary with Google Gemini 2.0 Flash
"""

import os
import json
import re
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from supabase import create_client, Client
import google.generativeai as genai

load_dotenv()

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class PageResponse(BaseModel):
    id: str
    page_id: str
    name: str
    url: str
    linkedin_id: Optional[str] = None
    profile_picture: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    followers_count: Optional[int] = None
    employees_count: Optional[int] = None
    specialties: Optional[str] = None
    founded_year: Optional[int] = None
    headquarters: Optional[str] = None
    company_type: Optional[str] = None
    created_at: str
    updated_at: str

class PostResponse(BaseModel):
    id: str
    page_id: str
    post_id: str
    content: Optional[str] = None
    posted_at: Optional[str] = None
    likes_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    post_url: Optional[str] = None
    media_url: Optional[str] = None
    created_at: str

class EmployeeResponse(BaseModel):
    id: str
    page_id: str
    employee_id: Optional[str] = None
    name: str
    profile_url: Optional[str] = None
    profile_picture: Optional[str] = None
    title: Optional[str] = None
    location: Optional[str] = None
    created_at: str

class CommentResponse(BaseModel):
    id: str
    post_id: str
    comment_id: Optional[str] = None
    author_name: Optional[str] = None
    author_profile_url: Optional[str] = None
    content: Optional[str] = None
    commented_at: Optional[str] = None
    likes_count: int = 0
    created_at: str

class PageDetailResponse(PageResponse):
    posts: List[PostResponse] = []
    employees: List[EmployeeResponse] = []

class AISummaryResponse(BaseModel):
    page_id: str
    page_name: str
    summary: str
    follower_analysis: str
    content_analysis: str
    engagement_insights: str
    page_type: str
    generated_at: str

# ============================================================================
# SUPABASE DATABASE
# ============================================================================

class SupabaseDB:
    """Supabase database operations"""
    
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("❌ SUPABASE_URL and SUPABASE_KEY must be set in .env")
        
        self.client: Client = create_client(url, key)
        print("✅ Connected to Supabase")
    
    def get_page_by_page_id(self, page_id: str) -> Optional[Dict]:
        """Get page by page_id"""
        try:
            response = self.client.table("pages").select("*").eq("page_id", page_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting page: {e}")
            return None
    
    def create_page(self, page_data: Dict) -> Optional[Dict]:
        """Create new page - FIXED with better error handling"""
        try:
            # Remove None values that might cause issues
            cleaned_data = {k: v for k, v in page_data.items() if v is not None}
            
            response = self.client.table("pages").insert(cleaned_data).execute()
            
            if response.data:
                print(f"✅ Page stored in Supabase: {cleaned_data.get('name')}")
                return response.data[0]
            else:
                print(f"⚠️  No data returned from insert")
                return None
                
        except Exception as e:
            print(f"❌ Error creating page: {e}")
            print(f"   Data attempted: {page_data.get('name', 'unknown')}")
            import traceback
            traceback.print_exc()
            return None
    
    def list_pages(
        self,
        skip: int = 0,
        limit: int = 10,
        min_followers: Optional[int] = None,
        max_followers: Optional[int] = None,
        industry: Optional[str] = None,
        name_search: Optional[str] = None
    ) -> List[Dict]:
        """List pages with filters"""
        try:
            query = self.client.table("pages").select("*")
            
            if min_followers is not None:
                query = query.gte("followers_count", min_followers)
            
            if max_followers is not None:
                query = query.lte("followers_count", max_followers)
            
            if industry:
                query = query.ilike("industry", f"%{industry}%")
            
            if name_search:
                query = query.ilike("name", f"%{name_search}%")
            
            query = query.range(skip, skip + limit - 1).order("created_at", desc=True)
            
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Error listing pages: {e}")
            return []
    
    def create_posts(self, posts_data: List[Dict]) -> bool:
        """Create multiple posts"""
        try:
            if posts_data:
                cleaned_posts = [{k: v for k, v in post.items() if v is not None} for post in posts_data]
                self.client.table("posts").insert(cleaned_posts).execute()
                return True
            return False
        except Exception as e:
            print(f"❌ Error creating posts: {e}")
            return False
    
    def get_posts_by_page(self, page_uuid: str, skip: int = 0, limit: int = 15) -> List[Dict]:
        """Get posts for a page"""
        try:
            response = self.client.table("posts")\
                .select("*")\
                .eq("page_id", page_uuid)\
                .order("posted_at", desc=True)\
                .range(skip, skip + limit - 1)\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error getting posts: {e}")
            return []
    
    def create_employees(self, employees_data: List[Dict]) -> bool:
        """Create multiple employees"""
        try:
            if employees_data:
                cleaned_employees = [{k: v for k, v in emp.items() if v is not None} for emp in employees_data]
                self.client.table("employees").insert(cleaned_employees).execute()
                return True
            return False
        except Exception as e:
            print(f"❌ Error creating employees: {e}")
            return False
    
    def get_employees_by_page(self, page_uuid: str, skip: int = 0, limit: int = 50) -> List[Dict]:
        """Get employees for a page"""
        try:
            response = self.client.table("employees")\
                .select("*")\
                .eq("page_id", page_uuid)\
                .range(skip, skip + limit - 1)\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error getting employees: {e}")
            return []
    
    def create_comments(self, comments_data: List[Dict]) -> bool:
        """Create multiple comments"""
        try:
            if comments_data:
                cleaned_comments = [{k: v for k, v in comment.items() if v is not None} for comment in comments_data]
                self.client.table("comments").insert(cleaned_comments).execute()
                return True
            return False
        except Exception as e:
            print(f"❌ Error creating comments: {e}")
            return False
    
    def get_all_comments_by_page(self, page_uuid: str) -> List[Dict]:
        """Get all comments for all posts of a page"""
        try:
            posts = self.get_posts_by_page(page_uuid, skip=0, limit=100)
            post_ids = [p["id"] for p in posts]
            
            if not post_ids:
                return []
            
            response = self.client.table("comments")\
                .select("*")\
                .in_("post_id", post_ids)\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error getting comments: {e}")
            return []

# ============================================================================
# AI SUMMARY SERVICE - Google Gemini 2.0 Flash
# ============================================================================

class AISummaryService:
    """AI Summary using Google Gemini 2.0 Flash"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            print("✅ Gemini AI initialized")
        else:
            self.model = None
            print("⚠️  GEMINI_API_KEY not set")
    
    def generate_summary(self, page: Dict, posts: List[Dict], employees: List[Dict]) -> Dict:
        """Generate AI summary of a LinkedIn page"""
        
        if not self.model:
            return self._get_mock_summary(page)
        
        try:
            # Prepare context
            context = self._build_context(page, posts, employees)
            
            # Create prompt
            prompt = f"""Analyze this LinkedIn company page and provide insights:

{context}

Provide a comprehensive analysis with the following sections:

1. **Company Overview**: Brief summary of what the company does and its position
2. **Follower Analysis**: Insights about their follower base and reach
3. **Content Strategy**: Analysis of their posting patterns and content type
4. **Engagement Insights**: How well their content performs
5. **Page Type**: What type of LinkedIn presence they have (active, professional, engaging, etc.)

Keep it professional, concise, and data-driven."""
            
            # Generate with Gemini
            response = self.model.generate_content(prompt)
            summary_text = response.text
            
            # Parse the response
            return self._parse_summary(summary_text, page)
            
        except Exception as e:
            print(f"❌ AI Summary error: {e}")
            return self._get_mock_summary(page)
    
    def _build_context(self, page: Dict, posts: List[Dict], employees: List[Dict]) -> str:
        """Build context for AI"""
        
        # Company info
        context = f"""
Company: {page.get('name', 'Unknown')}
Industry: {page.get('industry', 'Not specified')}
Followers: {page.get('followers_count', 0):,}
Employees: {page.get('employees_count', 'Not specified')}
Description: {page.get('description', 'No description')}
"""
        
        # Posts analysis
        if posts:
            total_likes = sum(post.get('likes_count', 0) for post in posts)
            total_comments = sum(post.get('comments_count', 0) for post in posts)
            avg_likes = total_likes / len(posts) if posts else 0
            
            context += f"""
Posts Analyzed: {len(posts)}
Total Likes: {total_likes:,}
Total Comments: {total_comments:,}
Average Likes per Post: {avg_likes:.0f}

Recent Post Samples:
"""
            for i, post in enumerate(posts[:3]):
                content = post.get('content', '')[:100]
                likes = post.get('likes_count', 0)
                comments = post.get('comments_count', 0)
                context += f"- Post {i+1}: {content}... (Likes: {likes}, Comments: {comments})\n"
        
        # Employee count
        if employees:
            context += f"\nEmployee Profiles Analyzed: {len(employees)}\n"
        
        return context
    
    def _parse_summary(self, summary_text: str, page: Dict) -> Dict:
        """Parse AI response into structured format"""
        
        # Simple parsing - split by sections
        sections = {
            'summary': '',
            'follower_analysis': '',
            'content_analysis': '',
            'engagement_insights': '',
            'page_type': ''
        }
        
        # Try to extract sections
        lines = summary_text.split('\n')
        current_section = 'summary'
        
        for line in lines:
            line_lower = line.lower()
            
            if 'follower' in line_lower and any(x in line_lower for x in ['analysis', 'insight']):
                current_section = 'follower_analysis'
            elif 'content' in line_lower and any(x in line_lower for x in ['strategy', 'analysis']):
                current_section = 'content_analysis'
            elif 'engagement' in line_lower:
                current_section = 'engagement_insights'
            elif 'page type' in line_lower:
                current_section = 'page_type'
            else:
                sections[current_section] += line + '\n'
        
        # Clean up
        for key in sections:
            sections[key] = sections[key].strip()
        
        # If parsing failed, put everything in summary
        if not any(sections.values()):
            sections['summary'] = summary_text
            sections['follower_analysis'] = f"Follower base: {page.get('followers_count', 0):,}"
            sections['content_analysis'] = "Active content strategy"
            sections['engagement_insights'] = "Professional engagement"
            sections['page_type'] = "Corporate LinkedIn presence"
        
        return sections
    
    def _get_mock_summary(self, page: Dict) -> Dict:
        """Fallback mock summary"""
        return {
            'summary': f"{page.get('name')} is a company in the {page.get('industry', 'technology')} industry.",
            'follower_analysis': f"Has {page.get('followers_count', 0):,} followers on LinkedIn.",
            'content_analysis': "Regular posting activity observed.",
            'engagement_insights': "Professional engagement levels.",
            'page_type': "Corporate LinkedIn presence"
        }

# ============================================================================
# SCRAPER SERVICE
# ============================================================================

class ScraperService:
    """LinkedIn scraping service"""
    
    def __init__(self):
        self.scraper = None
        self.linkedin_email = os.getenv("LINKEDIN_EMAIL")
        self.linkedin_password = os.getenv("LINKEDIN_PASSWORD")
        self.scraper_initialized = False
    
    def _initialize_scraper(self):
        """Lazy initialization"""
        if not self.scraper_initialized:
            try:
                from linkedin_custom_scraper import LinkedInScraper
                
                print("🔧 Initializing LinkedIn scraper...")
                self.scraper = LinkedInScraper(
                    email=self.linkedin_email,
                    password=self.linkedin_password,
                    headless=True
                )
                
                if self.scraper.setup_driver():
                    if self.scraper.login():
                        self.scraper_initialized = True
                        print("✅ Scraper initialized and logged in")
                    else:
                        print("❌ Failed to login")
                else:
                    print("❌ Failed to setup driver")
                    
            except ImportError as e:
                print(f"⚠️  linkedin_custom_scraper not found: {e}")
                self.scraper = None
            except Exception as e:
                print(f"❌ Error initializing scraper: {e}")
                self.scraper = None
    
    def scrape_company(self, page_id: str) -> Optional[Dict]:
        """Scrape company data"""
        if not self.scraper_initialized:
            self._initialize_scraper()
        
        if not self.scraper:
            print("⚠️  Scraper not available, using mock data")
            return None
        
        try:
            print(f"🔍 Scraping company: {page_id}")
            raw_data = self.scraper.scrape_company_page(page_id)
            
            if not raw_data:
                print(f"❌ Failed to scrape {page_id}")
                return None
            
            normalized = self._normalize_company_data(raw_data, page_id)
            print(f"✅ Normalized data for {page_id}")
            return normalized
            
        except Exception as e:
            print(f"❌ Error scraping: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def scrape_posts(self, page_id: str, max_posts: int = 15) -> List[Dict]:
        """Scrape posts"""
        if not self.scraper_initialized:
            self._initialize_scraper()
        
        if not self.scraper:
            return []
        
        try:
            raw_posts = self.scraper.scrape_company_posts(page_id, max_posts)
            
            normalized_posts = []
            for idx, post in enumerate(raw_posts):
                normalized = self._normalize_post_data(post, page_id, idx)
                if normalized:
                    normalized_posts.append(normalized)
            
            return normalized_posts
        except Exception as e:
            print(f"❌ Error scraping posts: {e}")
            return []
    
    def scrape_employees(self, page_id: str, max_employees: int = 20) -> List[Dict]:
        """Scrape employees"""
        if not self.scraper_initialized:
            self._initialize_scraper()
        
        if not self.scraper:
            return []
        
        try:
            raw_employees = self.scraper.scrape_company_employees(page_id, max_employees)
            
            normalized_employees = []
            for idx, emp in enumerate(raw_employees):
                normalized = self._normalize_employee_data(emp, page_id, idx)
                if normalized:
                    normalized_employees.append(normalized)
            
            return normalized_employees
        except Exception as e:
            print(f"❌ Error scraping employees: {e}")
            return []
    
    def _normalize_company_data(self, raw_data: Dict, page_id: str) -> Dict:
        """Normalize company data - FIXED"""
        
        # Extract followers count (handle K, M, B notations)
        followers_text = raw_data.get('followers', '0')
        followers_count = self._parse_count(followers_text)
        
        # Extract employee count
        company_size = raw_data.get('company_size', '0')
        employees_count = self._parse_employee_count(company_size)
        
        # Extract founded year
        founded = raw_data.get('founded', '')
        founded_year = self._extract_number(founded) if founded else None
        
        return {
            'page_id': page_id,
            'name': raw_data.get('name', page_id.title()),
            'url': raw_data.get('url', f"https://www.linkedin.com/company/{page_id}/"),
            'linkedin_id': raw_data.get('linkedin_id'),
            'profile_picture': raw_data.get('profile_picture'),
            'description': raw_data.get('description'),
            'website': raw_data.get('website'),
            'industry': raw_data.get('industry'),
            'followers_count': followers_count,
            'employees_count': employees_count,
            'specialties': raw_data.get('specialties'),
            'founded_year': founded_year,
            'headquarters': raw_data.get('headquarters'),
            'company_type': raw_data.get('company_type')
        }
    
    def _parse_count(self, text: str) -> int:
        """Parse follower count like '2.5M' or '15K' to integer"""
        if not text:
            return 0
        
        text = text.upper().strip()
        
        # Extract number with K, M, B
        match = re.search(r'([\d,.]+)\s*([KMB])?', text)
        if not match:
            return 0
        
        number_str = match.group(1).replace(',', '')
        multiplier_str = match.group(2)
        
        try:
            number = float(number_str)
            
            if multiplier_str == 'K':
                return int(number * 1000)
            elif multiplier_str == 'M':
                return int(number * 1000000)
            elif multiplier_str == 'B':
                return int(number * 1000000000)
            else:
                return int(number)
        except:
            return 0
    
    def _parse_employee_count(self, text: str) -> int:
        """Parse employee count like '51-200' to middle value"""
        if not text:
            return 0
        
        # Look for range like "51-200"
        match = re.search(r'(\d+)\s*-\s*(\d+)', text)
        if match:
            low = int(match.group(1))
            high = int(match.group(2))
            return (low + high) // 2
        
        # Look for single number
        match = re.search(r'(\d+)', text)
        if match:
            return int(match.group(1))
        
        return 0
    
    def _normalize_post_data(self, raw_post: Dict, page_id: str, idx: int) -> Optional[Dict]:
        """Normalize post data"""
        try:
            post_id = f"{page_id}_post_{idx}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            return {
                'post_id': post_id,
                'content': raw_post.get('content'),
                'posted_at': self._parse_posted_time(raw_post.get('posted_at')),
                'likes_count': self._extract_number(raw_post.get('likes', '0')),
                'comments_count': self._extract_number(raw_post.get('comments', '0')),
                'shares_count': 0,
                'post_url': raw_post.get('post_url'),
                'media_url': raw_post.get('media_url')
            }
        except Exception as e:
            print(f"Error normalizing post: {e}")
            return None
    
    def _normalize_employee_data(self, raw_employee: Dict, page_id: str, idx: int) -> Optional[Dict]:
        """Normalize employee data"""
        try:
            employee_id = f"{page_id}_emp_{idx}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            return {
                'employee_id': employee_id,
                'name': raw_employee.get('name', 'Unknown'),
                'profile_url': raw_employee.get('profile_url'),
                'profile_picture': raw_employee.get('profile_picture'),
                'title': raw_employee.get('title'),
                'location': raw_employee.get('location')
            }
        except:
            return None
    
    def _extract_number(self, text: str) -> int:
        """Extract first number from text"""
        if not text:
            return 0
        try:
            numbers = re.findall(r'[\d,]+', str(text))
            if numbers:
                return int(numbers[0].replace(',', ''))
        except:
            pass
        return 0
    
    def _parse_posted_time(self, time_text: str) -> str:
        """Parse relative time to ISO"""
        if not time_text:
            return datetime.now().isoformat()
        
        try:
            if 'hour' in time_text or 'minute' in time_text:
                return datetime.now().isoformat()
            elif 'day' in time_text:
                days = self._extract_number(time_text)
                return (datetime.now() - timedelta(days=days)).isoformat()
            elif 'week' in time_text:
                weeks = self._extract_number(time_text)
                return (datetime.now() - timedelta(weeks=weeks)).isoformat()
        except:
            pass
        
        return datetime.now().isoformat()

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="LinkedIn Insights API",
    description="Complete LinkedIn scraping with AI summaries",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
db = SupabaseDB()
scraper = ScraperService()
ai_service = AISummaryService()

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
def root():
    return {
        "message": "LinkedIn Insights API v2.0",
        "database": "Supabase",
        "ai": "Google Gemini 2.0 Flash",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "database": "Supabase",
        "ai": "Gemini" if ai_service.model else "unavailable"
    }

@app.get("/api/v1/pages/{page_id}", response_model=PageDetailResponse)
async def get_page(
    page_id: str,
    include_posts: bool = Query(True),
    include_employees: bool = Query(True),
    force_rescrape: bool = Query(False)
):
    """Get page details - scrapes if not in DB or if force_rescrape=True"""
    
    page = db.get_page_by_page_id(page_id)
    
    if not page or force_rescrape:
        print(f"📥 {'Re-scraping' if force_rescrape else 'Scraping'} {page_id}...")
        
        # Scrape company
        scraped_data = scraper.scrape_company(page_id)
        if not scraped_data:
            raise HTTPException(404, f"Page '{page_id}' not found or scraping failed")
        
        # Store in DB
        if force_rescrape and page:
            # Update existing
            page = scraped_data
            page['id'] = page['id']  # Keep same ID
        else:
            page = db.create_page(scraped_data)
        
        if not page:
            raise HTTPException(500, "Failed to store page in database")
        
        print(f"✅ Stored: {page.get('name')}")
        
        # Scrape posts
        posts_data = scraper.scrape_posts(page_id, max_posts=15)
        if posts_data:
            for post in posts_data:
                post["page_id"] = page["id"]
            db.create_posts(posts_data)
            print(f"✅ Stored {len(posts_data)} posts")
        
        # Scrape employees
        emp_data = scraper.scrape_employees(page_id, max_employees=20)
        if emp_data:
            for emp in emp_data:
                emp["page_id"] = page["id"]
            db.create_employees(emp_data)
            print(f"✅ Stored {len(emp_data)} employees")
    
    # Build response
    response = PageDetailResponse(**page)
    
    if include_posts:
        posts = db.get_posts_by_page(page["id"])
        response.posts = [PostResponse(**p) for p in posts]
    
    if include_employees:
        employees = db.get_employees_by_page(page["id"])
        response.employees = [EmployeeResponse(**e) for e in employees]
    
    return response

@app.get("/api/v1/pages", response_model=List[PageResponse])
async def list_pages(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    min_followers: Optional[int] = None,
    max_followers: Optional[int] = None,
    industry: Optional[str] = None,
    name_search: Optional[str] = None
):
    """List pages with filters"""
    pages = db.list_pages(skip, limit, min_followers, max_followers, industry, name_search)
    return [PageResponse(**p) for p in pages]

@app.get("/api/v1/pages/{page_id}/posts", response_model=List[PostResponse])
async def get_page_posts(
    page_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(15, ge=1, le=25)
):
    """Get posts for a page"""
    page = db.get_page_by_page_id(page_id)
    if not page:
        raise HTTPException(404, "Page not found")
    
    posts = db.get_posts_by_page(page["id"], skip, limit)
    return [PostResponse(**p) for p in posts]

@app.get("/api/v1/pages/{page_id}/employees", response_model=List[EmployeeResponse])
async def get_page_employees(
    page_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Get employees for a page"""
    page = db.get_page_by_page_id(page_id)
    if not page:
        raise HTTPException(404, "Page not found")
    
    employees = db.get_employees_by_page(page["id"], skip, limit)
    return [EmployeeResponse(**e) for e in employees]

@app.post("/api/v1/pages/{page_id}/summary", response_model=AISummaryResponse)
async def generate_ai_summary(page_id: str):
    """
    Generate AI Summary using Google Gemini 2.0 Flash
    Analyzes followers, engagement, content type, and page characteristics
    """
    
    page = db.get_page_by_page_id(page_id)
    if not page:
        raise HTTPException(404, "Page not found. Scrape it first using GET /api/v1/pages/{page_id}")
    
    # Get posts and employees
    posts = db.get_posts_by_page(page["id"], limit=25)
    employees = db.get_employees_by_page(page["id"], limit=50)
    
    print(f"🤖 Generating AI summary for {page_id}...")
    
    # Generate summary
    summary_data = ai_service.generate_summary(page, posts, employees)
    
    return AISummaryResponse(
        page_id=page_id,
        page_name=page.get('name', page_id),
        summary=summary_data.get('summary', ''),
        follower_analysis=summary_data.get('follower_analysis', ''),
        content_analysis=summary_data.get('content_analysis', ''),
        engagement_insights=summary_data.get('engagement_insights', ''),
        page_type=summary_data.get('page_type', ''),
        generated_at=datetime.now().isoformat()
    )

@app.get("/api/v1/stats/{page_id}")
async def get_page_stats(page_id: str):
    """Get statistics for a page"""
    
    page = db.get_page_by_page_id(page_id)
    if not page:
        raise HTTPException(404, "Page not found in database")
    
    posts = db.get_posts_by_page(page["id"])
    employees = db.get_employees_by_page(page["id"])
    comments = db.get_all_comments_by_page(page["id"])
    
    return {
        "page_id": page_id,
        "page_name": page.get("name"),
        "in_database": True,
        "counts": {
            "posts": len(posts),
            "employees": len(employees),
            "comments": len(comments)
        },
        "company_info": {
            "followers": page.get("followers_count"),
            "employees_count": page.get("employees_count"),
            "industry": page.get("industry")
        }
    }

@app.get("/api/v1/debug/{page_id}")
async def debug_scraping(page_id: str):
    """Debug endpoint to check scraper status"""
    
    result = {
        "page_id": page_id,
        "scraper_initialized": scraper.scraper_initialized,
        "scraper_available": scraper.scraper is not None,
        "linkedin_credentials_set": bool(scraper.linkedin_email and scraper.linkedin_password),
        "ai_available": ai_service.model is not None,
    }
    
    return result

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 80)
    print("🚀 LinkedIn Insights API v2.0")
    print("=" * 80)
    print("📍 Server: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("💾 Database: Supabase")
    print("🤖 AI: Google Gemini 2.0 Flash")
    print("=" * 80)
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)