import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

async def test_auth():
    print("🚀 Starting API tests...")
    
    # Use ASGITransport for testing FastAPI app directly without running Uvicorn
    transport = ASGITransport(app=app)
    
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        print("\n1. Registering new user...")
        resp = await ac.post("/api/v1/auth/register", json={"email": "newuser2@vietlott.vn", "password": "123"})
        print(f"Status: {resp.status_code}, Body: {resp.text}")
        
        print("\n2. Logging in...")
        resp = await ac.post("/api/v1/auth/login", data={"username": "newuser2@vietlott.vn", "password": "123"})
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            token = resp.json().get("access_token")
            print(f"Token received: {token[:20]}...")
            
            print("\n3. Accessing /me...")
            resp = await ac.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
            print(f"Status: {resp.status_code}, Body: {resp.json()}")
            
            print("\n4. Accessing premium-only...")
            resp = await ac.get("/api/v1/users/premium-only", headers={"Authorization": f"Bearer {token}"})
            print(f"Status: {resp.status_code}, Body: {resp.text}")

asyncio.run(test_auth())
