import httpx
import sys
import asyncio

async def health_check():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:3002/health", timeout=2.0)
            if response.status_code == 200:
                sys.exit(0)
            else:
                sys.exit(1)
    except Exception:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(health_check())
