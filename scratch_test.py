import asyncio
import httpx
from app.db.mongodb import connect_to_mongo, get_database, close_mongo_connection
from app.services.otp_service import otp_service

async def main():
    await connect_to_mongo()
    email = "boppudisanthosh404@gmail.com"
    
    # 1. Send OTP
    await otp_service.send_otp(email, "email", "verification")
    print("OTP sent!")
    
    # 2. Get raw OTP or test verify
    db = get_database()
    otp_doc = await db["otps"].find_one({"channel": "email", "purpose": "verification"}, sort=[("created_at", -1)])
    print("Latest OTP document created_at:", otp_doc["created_at"])
    
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())
