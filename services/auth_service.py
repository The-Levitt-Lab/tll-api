from fastapi import HTTPException
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
import jwt
from jwt.algorithms import RSAAlgorithm
import httpx

from core.config import get_settings
from schemas.auth import AuthProvider

settings = get_settings()


def verify_google_token(token: str) -> dict:
    # Google's library does its own requests, which are synchronous.
    # To be fully async we'd need to run this in a threadpool, 
    # but for now we focus on Apple since that was the user's issue.
    try:
        # If GOOGLE_CLIENT_ID is not set, we pass None to skip audience check
        audience = settings.GOOGLE_CLIENT_ID if settings.GOOGLE_CLIENT_ID else None
        
        id_info = id_token.verify_oauth2_token(token, google_requests.Request(), audience=audience)
        return {
            "email": id_info["email"], 
            "full_name": id_info.get("name")
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid Google token: {str(e)}")


async def verify_apple_token(token: str) -> dict:
    try:
        # Fetch public keys asynchronously
        apple_keys_url = "https://appleid.apple.com/auth/keys"
        async with httpx.AsyncClient() as client:
            response = await client.get(apple_keys_url)
            response.raise_for_status()
            keys = response.json()["keys"]
        
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        if not kid:
             raise HTTPException(status_code=400, detail="Invalid token header")
        
        key_data = next((k for k in keys if k["kid"] == kid), None)
        if not key_data:
             raise HTTPException(status_code=400, detail="Invalid token key id")

        public_key = RSAAlgorithm.from_jwk(key_data)
        
        audience = settings.APPLE_CLIENT_ID if settings.APPLE_CLIENT_ID else None
        
        options = {"verify_exp": True}
        if not audience:
             options["verify_aud"] = False
             
        decoded = jwt.decode(token, public_key, algorithms=["RS256"], audience=audience, options=options)
        
        return {
            "email": decoded["email"],
            "full_name": None 
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid Apple token: {str(e)}")


async def verify_token(provider: AuthProvider, token: str) -> dict:
    if provider == AuthProvider.GOOGLE:
        return verify_google_token(token)
    elif provider == AuthProvider.APPLE:
        return await verify_apple_token(token)
    elif provider == AuthProvider.DEV:
        if settings.ENV == "production":
             raise HTTPException(status_code=400, detail="Dev login not allowed in production")
        return {
            "email": token,
            "full_name": token.split("@")[0]
        }
    else:
        raise HTTPException(status_code=400, detail="Unsupported provider")
