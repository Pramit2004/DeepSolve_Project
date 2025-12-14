"""
FIXED LinkedIn Custom Scraper - Accurate Data Extraction
Properly extracts ALL fields with correct CSS selectors
"""

import os
import time
import json
import re
from typing import Dict, List, Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

load_dotenv()


class LinkedInScraper:
    """Fixed LinkedIn Scraper with accurate data extraction"""
    
    def __init__(self, headless: bool = False, email: str = None, password: str = None):
        self.email = email or os.getenv("LINKEDIN_EMAIL")
        self.password = password or os.getenv("LINKEDIN_PASSWORD")
        self.driver = None
        self.headless = headless
        self.logged_in = False
        
    def setup_driver(self):
        """Setup Chrome driver with options"""
        print("🔧 Setting up Chrome driver...")
        
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--disable-gpu")
        
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            
            print("✅ Chrome driver setup complete")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup driver: {str(e)}")
            return False
    
    def login(self) -> bool:
        """Login to LinkedIn"""
        if not self.email or not self.password:
            print("❌ LinkedIn credentials not provided")
            return False
        
        print("🔐 Logging in to LinkedIn...")
        
        try:
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(2)
            
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.clear()
            email_field.send_keys(self.email)
            
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(self.password)
            
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            time.sleep(60)  # Wait for manual verification if needed
            
            if "feed" in self.driver.current_url or "mynetwork" in self.driver.current_url:
                print("✅ Successfully logged in!")
                self.logged_in = True
                return True
            else:
                if "checkpoint" in self.driver.current_url:
                    print("⚠️  Security checkpoint - waiting 60 seconds...")
                    time.sleep(60)
                    return True
                print("❌ Login failed")
                return False
                
        except Exception as e:
            print(f"❌ Login failed: {str(e)}")
            return False
    
    def scrape_company_page(self, page_id: str, debug: bool = False) -> Optional[Dict]:
        """
        FIXED: Scrape company page with accurate field extraction
        Args:
            page_id: Company page ID
            debug: If True, save screenshot and page source for debugging
        """
        company_url = f"https://www.linkedin.com/company/{page_id}/"
        print(f"\n🔍 Scraping: {company_url}")
        
        try:
            self.driver.get(company_url)
            time.sleep(5)
            
            # Better page validation - check for actual company elements instead
            # Don't just check for "404" text as it might appear in other content
            
            # DEBUG: Save page info
            if debug:
                try:
                    self.driver.save_screenshot(f"{page_id}_debug.png")
                    with open(f"{page_id}_source.html", 'w', encoding='utf-8') as f:
                        f.write(self.driver.page_source)
                    print(f"  📸 Debug files saved: {page_id}_debug.png, {page_id}_source.html")
                except:
                    pass
            
            self._scroll_page(scrolls=5)
            
            company_data = {
                'page_id': page_id,
                'url': company_url,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Company Name - CRITICAL: If this fails, page doesn't exist
            name_found = False
            try:
                name = self.driver.find_element(By.CSS_SELECTOR, "h1.org-top-card-summary__title").text.strip()
                company_data['name'] = name
                name_found = True
                print(f"  ✓ Name: {name}")
            except:
                try:
                    name = self.driver.find_element(By.XPATH, "//h1[contains(@class, 'top-card')]").text.strip()
                    company_data['name'] = name
                    name_found = True
                    print(f"  ✓ Name: {name}")
                except:
                    try:
                        # One more attempt with broader search
                        name = self.driver.find_element(By.XPATH, "//h1").text.strip()
                        if name and len(name) > 0:
                            company_data['name'] = name
                            name_found = True
                            print(f"  ✓ Name: {name}")
                    except:
                        pass
            
            # If no name found, page doesn't exist
            if not name_found:
                print("❌ Company page not found - could not find company name")
                return None
            
            # Description/Tagline
            try:
                description = self.driver.find_element(By.CSS_SELECTOR, "p.org-top-card-summary__tagline").text.strip()
                company_data['description'] = description
                print(f"  ✓ Description: {description[:50]}...")
            except:
                try:
                    description = self.driver.find_element(By.XPATH, "//p[contains(@class, 'tagline')]").text.strip()
                    company_data['description'] = description
                    print(f"  ✓ Description: {description[:50]}...")
                except:
                    print("  ⚠ Could not find description")
            
            # Followers - FIXED
            try:
                # Method 1: Look for followers specifically
                followers_elem = self.driver.find_element(By.XPATH, "//*[contains(text(), 'followers') or contains(text(), 'Followers')]")
                followers_text = followers_elem.text.strip()
                company_data['followers'] = self._extract_followers(followers_text)
                print(f"  ✓ Followers: {company_data['followers']}")
            except:
                try:
                    # Method 2: Get first info item
                    info_items = self.driver.find_elements(By.CSS_SELECTOR, "div.org-top-card-summary-info-list__info-item")
                    for item in info_items:
                        text = item.text.strip()
                        if 'follower' in text.lower():
                            company_data['followers'] = self._extract_followers(text)
                            print(f"  ✓ Followers: {company_data['followers']}")
                            break
                except:
                    print("  ⚠ Could not find followers")
            
            # Website
            try:
                website = self.driver.find_element(By.CSS_SELECTOR, "a[data-test-id='about-us__website']").get_attribute("href")
                company_data['website'] = website
                print(f"  ✓ Website: {website}")
            except:
                try:
                    website = self.driver.find_element(By.CSS_SELECTOR, "a.org-top-card-primary-actions__action").get_attribute("href")
                    company_data['website'] = website
                    print(f"  ✓ Website: {website}")
                except:
                    print("  ⚠ Could not find website")
            
            # Profile Picture
            try:
                profile_pic = self.driver.find_element(By.CSS_SELECTOR, "img.org-top-card-primary-content__logo").get_attribute("src")
                company_data['profile_picture'] = profile_pic
                print(f"  ✓ Profile picture found")
            except:
                print("  ⚠ Could not find profile picture")
            
            # Scroll to "About" section
            self.driver.execute_script("window.scrollTo(0, 800);")
            time.sleep(3)
            
            # Industry, Company Size, HQ, Founded - FIXED
            try:
                # Find all dt/dd pairs
                detail_items = self.driver.find_elements(By.XPATH, "//dt[@class='org-page-details__label']")
                
                for item in detail_items:
                    label = item.text.strip().lower()
                    try:
                        value = item.find_element(By.XPATH, "./following-sibling::dd[1]").text.strip()
                        
                        if 'industry' in label:
                            company_data['industry'] = value
                            print(f"  ✓ Industry: {value}")
                        elif 'company size' in label or 'size' in label:
                            company_data['company_size'] = value
                            print(f"  ✓ Size: {value}")
                        elif 'headquarters' in label or 'hq' in label:
                            company_data['headquarters'] = value
                            print(f"  ✓ HQ: {value}")
                        elif 'founded' in label:
                            company_data['founded'] = value
                            print(f"  ✓ Founded: {value}")
                        elif 'specialties' in label:
                            company_data['specialties'] = value
                            print(f"  ✓ Specialties: {value[:50]}...")
                    except:
                        continue
                        
            except Exception as e:
                print(f"  ⚠ Could not extract all details: {str(e)}")
                
                # Fallback method
                try:
                    details = self.driver.find_elements(By.CSS_SELECTOR, "div.org-page-details__definition-text")
                    if len(details) >= 1:
                        company_data['industry'] = details[0].text.strip()
                    if len(details) >= 2:
                        company_data['company_size'] = details[1].text.strip()
                    if len(details) >= 3:
                        company_data['headquarters'] = details[2].text.strip()
                    if len(details) >= 5:
                        company_data['founded'] = details[4].text.strip()
                except:
                    pass
            
            print(f"✅ Successfully scraped {page_id}")
            return company_data
            
        except Exception as e:
            print(f"❌ Error scraping company page: {str(e)}")
            
            # Check if it's actually a 404 or just scraping error
            if "404" in self.driver.page_source or "This page doesn't exist" in self.driver.page_source:
                print("❌ Page actually doesn't exist (404)")
            else:
                print("⚠️  Page exists but scraping failed - try again or check selectors")
            
            import traceback
            traceback.print_exc()
            return None
    
    def scrape_company_posts(self, page_id: str, max_posts: int = 15) -> List[Dict]:
        """Scrape posts with post URLs"""
        posts_url = f"https://www.linkedin.com/company/{page_id}/posts/"
        print(f"\n📄 Scraping posts: {posts_url}")
        
        try:
            self.driver.get(posts_url)
            time.sleep(4)
            
            posts = []
            
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            post_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.feed-shared-update-v2")
            print(f"  Found {len(post_elements)} posts")
            
            for idx, post_elem in enumerate(post_elements[:max_posts]):
                try:
                    post_data = {}
                    
                    # Get post URL - IMPORTANT for comments
                    try:
                        post_link = post_elem.find_element(By.CSS_SELECTOR, "a[data-test-link='permalink']")
                        post_data['post_url'] = post_link.get_attribute('href')
                    except:
                        try:
                            post_link = post_elem.find_element(By.XPATH, ".//a[contains(@href, '/posts/')]")
                            post_data['post_url'] = post_link.get_attribute('href')
                        except:
                            post_data['post_url'] = None
                    
                    # Content
                    try:
                        content = post_elem.find_element(By.CSS_SELECTOR, "span.break-words").text.strip()
                        post_data['content'] = content
                    except:
                        post_data['content'] = None
                    
                    # Posted time
                    try:
                        time_elem = post_elem.find_element(By.CSS_SELECTOR, "span.feed-shared-actor__sub-description")
                        post_data['posted_at'] = time_elem.text.strip()
                    except:
                        post_data['posted_at'] = None
                    
                    # Likes
                    try:
                        likes = post_elem.find_element(By.CSS_SELECTOR, "span.social-details-social-counts__reactions-count").text.strip()
                        post_data['likes'] = likes
                    except:
                        post_data['likes'] = "0"
                    
                    # Comments
                    try:
                        comments = post_elem.find_element(By.CSS_SELECTOR, "button.social-details-social-counts__comments").text.strip()
                        post_data['comments'] = comments
                    except:
                        post_data['comments'] = "0"
                    
                    posts.append(post_data)
                    content_preview = post_data['content'][:50] if post_data['content'] else 'N/A'
                    print(f"  ✓ Post {idx + 1}: {content_preview}...")
                    
                except Exception as e:
                    print(f"  ⚠ Error parsing post {idx + 1}: {str(e)}")
                    continue
            
            print(f"✅ Scraped {len(posts)} posts")
            return posts
            
        except Exception as e:
            print(f"❌ Error scraping posts: {str(e)}")
            return []
    
    def scrape_company_employees(self, page_id: str, max_employees: int = 20) -> List[Dict]:
        """Scrape employees"""
        people_url = f"https://www.linkedin.com/company/{page_id}/people/"
        print(f"\n👥 Scraping employees: {people_url}")
        
        try:
            self.driver.get(people_url)
            time.sleep(4)
            
            employees = []
            
            for _ in range(2):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            employee_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.org-people-profile-card")
            print(f"  Found {len(employee_elements)} employees")
            
            for idx, emp_elem in enumerate(employee_elements[:max_employees]):
                try:
                    employee_data = {}
                    
                    try:
                        name = emp_elem.find_element(By.CSS_SELECTOR, "div.org-people-profile-card__profile-title").text.strip()
                        employee_data['name'] = name
                    except:
                        employee_data['name'] = None
                    
                    try:
                        title = emp_elem.find_element(By.CSS_SELECTOR, "div.artdeco-entity-lockup__subtitle").text.strip()
                        employee_data['title'] = title
                    except:
                        employee_data['title'] = None
                    
                    try:
                        profile_url = emp_elem.find_element(By.CSS_SELECTOR, "a[href*='/in/']").get_attribute("href")
                        employee_data['profile_url'] = profile_url
                    except:
                        employee_data['profile_url'] = None
                    
                    if employee_data.get('name'):
                        employees.append(employee_data)
                        print(f"  ✓ Employee {idx + 1}: {employee_data.get('name', 'N/A')}")
                    
                except Exception as e:
                    print(f"  ⚠ Error parsing employee {idx + 1}: {str(e)}")
                    continue
            
            print(f"✅ Scraped {len(employees)} employees")
            return employees
            
        except Exception as e:
            print(f"❌ Error scraping employees: {str(e)}")
            return []
    
    def _extract_followers(self, text: str) -> str:
        """Extract follower count from text"""
        # Remove everything except numbers, commas, K, M, B
        text = text.upper()
        match = re.search(r'([\d,]+\.?\d*[KMB]?)\s*FOLLOW', text)
        if match:
            return match.group(1).strip()
        
        match = re.search(r'([\d,]+\.?\d*[KMB]?)', text)
        if match:
            return match.group(1).strip()
        
        return text
    
    def _scroll_page(self, scrolls: int = 5):
        """Scroll page to load content"""
        for i in range(scrolls):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            print("🔒 Browser closed")