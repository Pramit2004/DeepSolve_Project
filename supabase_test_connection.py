import os
from dotenv import load_dotenv
from supabase import create_client
load_dotenv()

# Initialize client
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

# Test connection
print("✅ Connected to Supabase!")
print(f"Project URL: {url}")
