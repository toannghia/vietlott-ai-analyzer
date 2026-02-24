import asyncio
import httpx
from app.main import app

async def run_tests():
    # We will use httpx ASGITransport to test directly against FastAPI without full uvicorn
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        print("Testing GET /api/v1/stats/frequency")
        res1 = await client.get("/api/v1/stats/frequency")
        print("Status:", res1.status_code)
        data1 = res1.json()
        print(f"Returned {len(data1.get('data', []))} items. First 3:", data1.get('data', [])[:3])
        
        print("\nTesting GET /api/v1/stats/gaps")
        res2 = await client.get("/api/v1/stats/gaps")
        print("Status:", res2.status_code)
        data2 = res2.json()
        print(f"Returned {len(data2.get('data', []))} items. First 3:", data2.get('data', [])[:3])

if __name__ == "__main__":
    asyncio.run(run_tests())
