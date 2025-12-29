"""Clerk authentication service.

Verifies Clerk session tokens (JWTs) using Clerk's JWKS endpoint.
"""
from __future__ import annotations

import httpx
import jwt
from jwt.algorithms import RSAAlgorithm
from fastapi import HTTPException, status

from core.config import get_settings

settings = get_settings()

# Cache for JWKS keys to avoid fetching on every request
_jwks_cache: dict | None = None


async def fetch_clerk_jwks() -> dict:
    """Fetch Clerk's JWKS (JSON Web Key Set) for token verification."""
    global _jwks_cache
    if _jwks_cache is not None:
        return _jwks_cache
    
    if not settings.CLERK_ISSUER:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clerk issuer not configured"
        )
    
    # Clerk JWKS endpoint
    issuer = settings.CLERK_ISSUER.rstrip("/")
    jwks_url = f"{issuer}/.well-known/jwks.json"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(jwks_url)
        response.raise_for_status()
        _jwks_cache = response.json()
        return _jwks_cache


def clear_jwks_cache() -> None:
    """Clear the JWKS cache (useful for testing or key rotation)."""
    global _jwks_cache
    _jwks_cache = None


async def verify_clerk_token(token: str) -> dict:
    """
    Verify a Clerk session token and return the decoded claims.
    
    Args:
        token: The Clerk session token (JWT) from the Authorization header
        
    Returns:
        dict with user information including:
        - sub: Clerk user ID
        - email: User's email (if available)
        - Additional claims from the token
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # Get the unverified header to find the key ID
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        
        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing key ID"
            )
        
        # Fetch JWKS and find the matching key
        jwks = await fetch_clerk_jwks()
        key_data = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
        
        if not key_data:
            # Key not found - clear cache and retry once (key rotation)
            clear_jwks_cache()
            jwks = await fetch_clerk_jwks()
            key_data = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
            
            if not key_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: key not found"
                )
        
        # Convert JWK to public key
        public_key = RSAAlgorithm.from_jwk(key_data)
        
        # Build verification options
        issuer = settings.CLERK_ISSUER.rstrip("/")
        
        # Decode and verify the token
        decoded = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            issuer=issuer,
            options={
                "verify_exp": True,
                "verify_iss": True,
                "verify_aud": False,  # Clerk tokens don't always have audience
            }
        )
        
        return decoded
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidIssuerError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token issuer"
        )
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to verify token: authentication service unavailable"
        )


async def get_clerk_user_info(token: str) -> dict:
    """
    Extract user information from a verified Clerk token.
    
    Returns:
        dict with:
        - clerk_user_id: The Clerk user ID (sub claim)
        - email: User's email address
        - full_name: User's full name (if available)
    """
    claims = await verify_clerk_token(token)
    
    # Extract user info from claims
    # Clerk puts email in different places depending on session type
    email = claims.get("email") or claims.get("primary_email_address")
    
    # Full name might be in various places
    full_name = None
    if claims.get("first_name") or claims.get("last_name"):
        first = claims.get("first_name", "")
        last = claims.get("last_name", "")
        full_name = f"{first} {last}".strip()
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token does not contain email address"
        )
    
    return {
        "clerk_user_id": claims.get("sub"),
        "email": email,
        "full_name": full_name,
    }
