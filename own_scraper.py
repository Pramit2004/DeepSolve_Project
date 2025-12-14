# from linkedin_custom_scraper import LinkedInScraper

# # Initialize scraper
# scraper = LinkedInScraper(
#     email="pramitmangukiya14@gmail.com",
#     password="pramitPpm@2004",
#     headless=False  # Set to True to hide browser
# )

# # Setup and login
# scraper.setup_driver()
# scraper.login()

# # Scrape a company
# company_data = scraper.scrape_company_page("deepsolv")
# print(company_data)

# # Scrape posts
# posts = scraper.scrape_company_posts("deepsolv", max_posts=10)
# print(posts)

# # Scrape employees
# employees = scraper.scrape_company_employees("deepsolv", max_employees=20)
# print(employees)

# # Close when done
# scraper.close()