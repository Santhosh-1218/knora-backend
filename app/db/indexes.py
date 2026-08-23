from pymongo import IndexModel, ASCENDING
from app.db.mongodb import get_database
from app.core.logging import logger


async def create_mongo_indexes():
    db = get_database()
    logger.info("Initializing MongoDB indexes...")

    # Users Collection Indexes
    user_indexes = [
        IndexModel(
            [("email_normalized", ASCENDING)],
            name="idx_users_email_normalized",
            unique=True,
            sparse=True
        ),
        IndexModel(
            [("mobile", ASCENDING)],
            name="idx_users_mobile",
            unique=True,
            sparse=True
        ),
        IndexModel(
            [("google.sub", ASCENDING)],
            name="idx_users_google_sub",
            unique=True,
            sparse=True
        )
    ]
    await db["users"].create_indexes(user_indexes)

    # OTP Verifications Collection Indexes
    otp_indexes = [
        IndexModel(
            [("identifier_hash", ASCENDING), ("channel", ASCENDING), ("purpose", ASCENDING)],
            name="idx_otp_identifier_channel_purpose"
        ),
        IndexModel(
            [("expires_at", ASCENDING)],
            name="idx_otp_ttl",
            expireAfterSeconds=0
        )
    ]
    await db["otp_verifications"].create_indexes(otp_indexes)

    # Sessions Collection Indexes
    session_indexes = [
        IndexModel(
            [("refresh_token_hash", ASCENDING)],
            name="idx_sessions_refresh_token_hash",
            unique=True
        ),
        IndexModel(
            [("jti", ASCENDING)],
            name="idx_sessions_jti",
            unique=True
        ),
        IndexModel(
            [("user_id", ASCENDING)],
            name="idx_sessions_user_id"
        ),
        IndexModel(
            [("expires_at", ASCENDING)],
            name="idx_sessions_ttl",
            expireAfterSeconds=0
        )
    ]
    await db["sessions"].create_indexes(session_indexes)

    logger.info("MongoDB indexes successfully created.")
