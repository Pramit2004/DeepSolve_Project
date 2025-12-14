"""
LinkedIn Scraper Test Script
Tests multiple methods to fetch LinkedIn company data

Methods:
1. Proxycurl API (Recommended)
2. RapidAPI LinkedIn Scraper
3. Custom Selenium Scraper (Advanced)
"""

import requests
import json
from typing import Dict, Optional
import os
from datetime import datetime

# ============================================================================
# METHOD 1: Proxycurl API (RECOMMENDED - Most Reliable)
# ============================================================================

def fetch_with_proxycurl(company_url: str, api_key: str) -> Optional[Dict]:
    """
    Fetch company data using Proxycurl API
    Sign up at: https://nubela.co/proxycurl/
    Free tier: 10 credits
    """
    print("🔍 Attempting to fetch with Proxycurl API...")
    
    endpoint = "https://nubela.co/proxycurl/api/v2/linkedin/company"
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    params = {
        'url': company_url,
        'categories': 'include',
        'funding_data': 'include',
        'extra': 'include',
        'exit_data': 'include',
        'acquisitions': 'include',
        'use_cache': 'if-present'
    }
    
    try:
        response = requests.get(endpoint, params=params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Successfully fetched data with Proxycurl!")
            return {
                'method': 'proxycurl',
                'success': True,
                'data': data,
                'timestamp': datetime.now().isoformat()
            }
        else:
            print(f"❌ Proxycurl API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Proxycurl Exception: {str(e)}")
        return None


# ============================================================================
# METHOD 2: RapidAPI LinkedIn Scraper
# ============================================================================

def fetch_with_rapidapi(company_url: str, api_key: str) -> Optional[Dict]:
    """
    Fetch company data using RapidAPI
    Sign up at: https://rapidapi.com/
    Search for "LinkedIn Company" scrapers
    """
    print("🔍 Attempting to fetch with RapidAPI...")
    
    # Example with "LinkedIn Company Profile" API
    endpoint = "https://linkedin-data-api.p.rapidapi.com/get-company-details"
    
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "linkedin-data-api.p.rapidapi.com"
    }
    
    params = {"url": company_url}
    
    try:
        response = requests.get(endpoint, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Successfully fetched data with RapidAPI!")
            return {
                'method': 'rapidapi',
                'success': True,
                'data': data,
                'timestamp': datetime.now().isoformat()
            }
        else:
            print(f"❌ RapidAPI Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ RapidAPI Exception: {str(e)}")
        return None


# ============================================================================
# METHOD 3: Custom Selenium Scraper (Advanced - Requires Setup)
# ============================================================================

def fetch_with_selenium(company_url: str, headless: bool = True) -> Optional[Dict]:
    """
    Custom Selenium scraper
    Requires: pip install selenium webdriver-manager
    Note: This may require LinkedIn login credentials
    """
    print("🔍 Attempting to fetch with Selenium scraper...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        import time
        
        # Setup Chrome options
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        # Initialize driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print(f"📍 Navigating to: {company_url}")
        driver.get(company_url)
        time.sleep(5)  # Wait for page load
        
        # Extract data
        company_data = {}
        
        try:
            # Company Name
            company_name = driver.find_element(By.CSS_SELECTOR, "h1.org-top-card-summary__title").text
            company_data['name'] = company_name
            print(f"✓ Found company name: {company_name}")
        except:
            print("⚠ Could not find company name")
        
        try:
            # Description
            description = driver.find_element(By.CSS_SELECTOR, "p.org-top-card-summary__tagline").text
            company_data['description'] = description
            print(f"✓ Found description")
        except:
            print("⚠ Could not find description")
        
        try:
            # Followers
            followers = driver.find_element(By.CSS_SELECTOR, "div.org-top-card-summary-info-list__info-item").text
            company_data['followers'] = followers
            print(f"✓ Found followers: {followers}")
        except:
            print("⚠ Could not find followers")
        
        try:
            # Industry
            industry = driver.find_element(By.CSS_SELECTOR, "div.org-page-details__definition-text").text
            company_data['industry'] = industry
            print(f"✓ Found industry: {industry}")
        except:
            print("⚠ Could not find industry")
        
        # Get page source for further parsing if needed
        page_source = driver.page_source
        
        driver.quit()
        
        if company_data:
            print("✅ Successfully scraped data with Selenium!")
            return {
                'method': 'selenium',
                'success': True,
                'data': company_data,
                'timestamp': datetime.now().isoformat()
            }
        else:
            print("❌ No data extracted")
            return None
            
    except ImportError:
        print("❌ Selenium not installed. Run: pip install selenium webdriver-manager")
        return None
    except Exception as e:
        print(f"❌ Selenium Exception: {str(e)}")
        return None


# ============================================================================
# TEST RUNNER
# ============================================================================

def test_all_methods(company_url: str = "https://www.linkedin.com/company/deepsolv/"):
    """
    Test all scraping methods
    """
    print("=" * 80)
    print("🚀 LINKEDIN SCRAPER TEST")
    print("=" * 80)
    print(f"\nTarget: {company_url}\n")
    
    results = []
    
    # Get API keys from environment or use placeholders
    proxycurl_key = os.getenv('PROXYCURL_API_KEY', 'YOUR_PROXYCURL_API_KEY')
    rapidapi_key = os.getenv('RAPIDAPI_KEY', 'YOUR_RAPIDAPI_KEY')
    
    # Test Method 1: Proxycurl
    print("\n" + "=" * 80)
    print("METHOD 1: PROXYCURL API")
    print("=" * 80)
    if proxycurl_key != 'YOUR_PROXYCURL_API_KEY':
        result1 = fetch_with_proxycurl(company_url, proxycurl_key)
        if result1:
            results.append(result1)
    else:
        print("⚠ Proxycurl API key not set")
        print("Sign up at: https://nubela.co/proxycurl/")
        print("Set environment variable: PROXYCURL_API_KEY")
    
    # Test Method 2: RapidAPI
    print("\n" + "=" * 80)
    print("METHOD 2: RAPIDAPI")
    print("=" * 80)
    if rapidapi_key != 'YOUR_RAPIDAPI_KEY':
        result2 = fetch_with_rapidapi(company_url, rapidapi_key)
        if result2:
            results.append(result2)
    else:
        print("⚠ RapidAPI key not set")
        print("Sign up at: https://rapidapi.com/")
        print("Set environment variable: RAPIDAPI_KEY")
    
    # Test Method 3: Selenium (commented out by default, requires browser)
    print("\n" + "=" * 80)
    print("METHOD 3: SELENIUM SCRAPER")
    print("=" * 80)
    print("⚠ Selenium scraper disabled by default")
    print("To enable: Uncomment the line below and install selenium")
    # result3 = fetch_with_selenium(company_url)
    # if result3:
    #     results.append(result3)
    
    # Display results
    print("\n" + "=" * 80)
    print("📊 RESULTS SUMMARY")
    print("=" * 80)
    
    if results:
        print(f"\n✅ Successfully fetched data using {len(results)} method(s)")
        for idx, result in enumerate(results, 1):
            print(f"\n--- Result {idx} ({result['method'].upper()}) ---")
            print(json.dumps(result['data'], indent=2)[:500] + "...")
    else:
        print("\n❌ No successful results")
        print("\n💡 NEXT STEPS:")
        print("1. Sign up for Proxycurl: https://nubela.co/proxycurl/ (Recommended)")
        print("2. Get your API key from the dashboard")
        print("3. Set environment variable: export PROXYCURL_API_KEY='your_key'")
        print("4. Run this script again")
    
    return results


# ============================================================================
# EXAMPLE: How to use in your application
# ============================================================================

def example_usage():
    """
    Example of how to integrate this into your FastAPI application
    """
    print("\n" + "=" * 80)
    print("📝 EXAMPLE USAGE IN YOUR APPLICATION")
    print("=" * 80)
    
    example_code = '''
# In your FastAPI application:

from linkedin_scraper import fetch_with_proxycurl

@app.get("/api/v1/pages/{page_id}")
async def get_page(page_id: str):
    # Check if data exists in database
    page = db.query(Page).filter(Page.page_id == page_id).first()
    
    if page:
        # Return from cache/database
        return page
    else:
        # Fetch from LinkedIn
        company_url = f"https://www.linkedin.com/company/{page_id}/"
        data = fetch_with_proxycurl(company_url, PROXYCURL_API_KEY)
        
        if data and data['success']:
            # Store in database
            new_page = Page(**data['data'])
            db.add(new_page)
            db.commit()
            return new_page
        else:
            raise HTTPException(status_code=404, detail="Page not found")
'''
    print(example_code)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Test with default company
    test_all_methods("https://www.linkedin.com/company/deepsolv/")
    
    # Show example usage
    example_usage()
    
    print("\n" + "=" * 80)
    print("✨ TEST COMPLETE")
    print("=" * 80)
    print("\nTo test with your own company:")
    print("  python linkedin_scraper_test.py")
    print("\nOr in Python:")
    print("  from linkedin_scraper_test import test_all_methods")
    print("  test_all_methods('https://www.linkedin.com/company/your-company/')")