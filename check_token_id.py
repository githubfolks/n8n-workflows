import os
import sys
import json
import urllib.request
import urllib.parse
from urllib.error import URLError, HTTPError

def load_env(filepath):
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, val = line.split('=', 1)
                os.environ[key] = val

load_env('.env')
access_token = os.environ.get('FACEBOOK_PAGE_ACCESS_TOKEN')
env_page_id = os.environ.get('FACEBOOK_PAGE_ID')

if not access_token:
    print("Error: Required environment variable FACEBOOK_PAGE_ACCESS_TOKEN missing.")
    sys.exit(1)

print(f"Your .env says the FACEBOOK_PAGE_ID should be: {env_page_id}")
print("Checking what Facebook thinks this token belongs to...")

url = f"https://graph.facebook.com/v18.0/me?access_token={access_token}&fields=id,name"
req = urllib.request.Request(url)

try:
    with urllib.request.urlopen(req) as response:
        result = response.read().decode('utf-8')
        data = json.loads(result)
        print("\n--- TOKEN VALIDATION SUCCESS ---")
        print(f"Token belongs to: {data.get('name')} (Type: Page)")
        print(f"Actual Page ID:   {data.get('id')}")
        
        if data.get('id') != env_page_id:
            print(f"\n❌ MISMATCH DETECTED! You are trying to post to ID {env_page_id}, but this token only has permission for {data.get('id')}!")
            print(f"Solution: Update your .env to use FACEBOOK_PAGE_ID={data.get('id')}")
        else:
            print("\n✅ The ID matches correctly!")

except HTTPError as e:
    print(f"\n--- TOKEN VALIDATION FAILED ---")
    print(f"HTTP Error: {e.code} - {e.reason}")
    print(f"Response Body: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Other Error: {str(e)}")
