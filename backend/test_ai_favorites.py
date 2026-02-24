import asyncio
import httpx
from app.main import app

async def run_tests():
    from app.services.ai_service import generate_prediction
    
    # 1. Manually trigger an AI prediction for period 01235
    print("Generating Prediction for 01235...")
    await generate_prediction("01235")
    
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # TEST 1: GUEST / FREE PREDICTION MASKING
        print("\nTesting GET /api/v1/predictions/latest (GUEST)")
        res1 = await client.get("/api/v1/predictions/latest")
        print("Status (Guest):", res1.status_code)
        data1 = res1.json()
        print("Response:", data1)
        if "Premium Only" in data1.get("confidence", ""):
            print("=> MASKING WORKED!")
            
        # We need a user to test Favorites and Premium 
        # First let's create a User directly in DB for testing
        from app.core.database import async_session
        from app.models.user import User, UserRole
        from app.core.security import get_password_hash
        
        test_email = "testai@example.com"
        test_pass = "password123"
        async with async_session() as db:
            from sqlalchemy import select
            user = await db.execute(select(User).where(User.email == test_email))
            test_user = user.scalar_one_or_none()
            if not test_user:
                test_user = User(
                    email=test_email,
                    password_hash=get_password_hash(test_pass),
                    role=UserRole.PREMIUM
                )
                db.add(test_user)
                await db.commit()
                print("Created mock premium user.")
                
        # Login to get token
        login_res = await client.post("/api/v1/auth/login", data={"username": test_email, "password": test_pass})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # TEST 2: PREMIUM PREDICTION
        print("\nTesting GET /api/v1/predictions/latest (PREMIUM)")
        res2 = await client.get("/api/v1/predictions/latest", headers=headers)
        print("Status (Premium):", res2.status_code)
        print("Response:", res2.json())
        
        # TEST 3: FAVORITES
        print("\nTesting POST /api/v1/users/favorites")
        new_favs = {"favorite_numbers": [2, 5, 8, 11, 22, 33]}
        res_post = await client.post("/api/v1/users/favorites", json=new_favs, headers=headers)
        print("Status POST:", res_post.status_code)
        print("Response POST:", res_post.json())
        
        print("\nTesting GET /api/v1/users/favorites")
        res_get = await client.get("/api/v1/users/favorites", headers=headers)
        print("Status GET:", res_get.status_code)
        print("Response GET:", res_get.json())

if __name__ == "__main__":
    asyncio.run(run_tests())
