import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.all_models import Practice

async def verify_db_connection():
    print("Connecting to Database...")
    async with AsyncSessionLocal() as session:
        try:
            # Create a test practice
            print("Creating test practice...")
            new_practice = Practice(name="Test Practice", pms_api_key="test_key_123")
            session.add(new_practice)
            await session.commit()
            print("Successfully inserted Test Practice.")
            
            # Query back
            result = await session.execute(select(Practice).where(Practice.name == "Test Practice"))
            practice = result.scalars().first()
            if practice:
                print(f"Verified Record: ID={practice.id}, Name={practice.name}")
            else:
                print("Failed to retrieve record.")
                
        except Exception as e:
            print(f"Database Error: {e}")

if __name__ == "__main__":
    asyncio.run(verify_db_connection())
