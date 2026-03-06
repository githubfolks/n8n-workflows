import asyncio
import httpx
import os

async def generate_test_token(base_url="http://localhost:8003"):
    """
    Creates a test user and generates an access token for API testing.
    """
    print(f"[*] Generating test authentication token at {base_url}...")
    
    # We'll use a hardcoded test user for convenience
    test_user = {
        "email": "test_video_pipeline@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. Try to register the user first
        print("[-] Registering test user...")
        reg_resp = await client.post(
            f"{base_url}/api/v1/auth/signup",
            json=test_user
        )
        
        if reg_resp.status_code not in [200, 400]: # 400 likely means user already exists
            print(f"[!] Warning: Registration failed with {reg_resp.status_code}: {reg_resp.text}")
            
        # 2. Login to get the token, API expects Form Data for OAuth2
        print("[-] Logging in...")
        data = {
            "username": test_user["email"],
            "password": test_user["password"]
        }
        
        login_resp = await client.post(
            f"{base_url}/api/v1/auth/login/access-token",
            data=data
        )
        
        if login_resp.status_code == 200:
            token = login_resp.json().get("access_token")
            print(f"[+] Successfully generated token!")
            print(f"\nYour token is:\n{token}\n")
            return token
        else:
            print(f"[-] Failed to login. Status: {login_resp.status_code}")
            print(login_resp.text)
            return None

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate a test token")
    parser.add_argument("--base-url", type=str, default="http://localhost:8003", help="Base URL of the API server")
    args = parser.parse_args()
    
    asyncio.run(generate_test_token(args.base_url))

if __name__ == "__main__":
    main()
