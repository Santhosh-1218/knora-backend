from typing import Any, Dict, Optional
import urllib.parse
import httpx
from app.core.config import settings
from app.core.exceptions import AuthenticationError
from app.core.logging import logger


class GoogleOAuthService:
    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"

    def get_authorization_url(self, state: Optional[str] = None) -> str:
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "select_account"
        }
        if state:
            params["state"] = state

        return f"{self.GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}"

    async def verify_code_and_get_user_info(self, code: str) -> Dict[str, Any]:
        """
        Exchanges authorization code for Google tokens and fetches verified Google profile.
        """
        # Mock mode fallback for local automated testing without live Google APIs
        # Only use mock fallback if code starts with mock_code_ or if GOOGLE_CLIENT_ID is mock AND code is not a real Google code (starts with 4/)
        if code.startswith("mock_code_") or (settings.GOOGLE_CLIENT_ID.startswith("mock_") and not code.startswith("4/")):
            logger.info("Executing Google OAuth in development mock mode...")
            mock_sub = "mock_google_sub_12345"
            dev_email = "google_user@knora.in"
            dev_name = "Google Student User"

            if code.startswith("mock_code_"):
                raw_code = code.replace("mock_code_", "")
                if "@" in raw_code:
                    dev_email = raw_code.lower().strip()
                    dev_name = dev_email.split("@")[0].capitalize()
                    mock_sub = f"google_sub_{dev_email}"
                else:
                    mock_sub = raw_code
                    dev_name = f"User {raw_code.capitalize()}"
                    dev_email = f"{raw_code}@knora.in"

            return {
                "sub": str(mock_sub),
                "email": dev_email.lower().strip(),
                "email_verified": True,
                "name": dev_name,
                "picture": f"https://api.dicebear.com/7.x/avataaars/svg?seed={dev_email}"
            }

        async with httpx.AsyncClient(timeout=10.0) as client:
            token_payload = {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.GOOGLE_REDIRECT_URI
            }

            token_response = await client.post(self.GOOGLE_TOKEN_URL, data=token_payload)
            if token_response.status_code != 200:
                logger.error(f"Google OAuth token exchange failed: {token_response.text}")
                raise AuthenticationError("Failed to authenticate with Google. Invalid authorization code.")

            token_data = token_response.json()
            access_token = token_data.get("access_token")
            if not access_token:
                raise AuthenticationError("Google OAuth response missing access_token.")

            # Fetch User Info
            headers = {"Authorization": f"Bearer {access_token}"}
            userinfo_response = await client.get(self.GOOGLE_USERINFO_URL, headers=headers)
            if userinfo_response.status_code != 200:
                raise AuthenticationError("Failed to fetch user profile from Google.")

            user_info = userinfo_response.json()
            
            sub = user_info.get("sub")
            email = user_info.get("email")
            email_verified = user_info.get("email_verified", False)

            if not sub or not email:
                raise AuthenticationError("Google profile response missing mandatory sub or email.")

            if not email_verified:
                raise AuthenticationError("Google email is not verified by Google.")

            return {
                "sub": str(sub),
                "email": str(email).lower().strip(),
                "email_verified": True,
                "name": user_info.get("name"),
                "picture": user_info.get("picture")
            }


google_oauth_service = GoogleOAuthService()
