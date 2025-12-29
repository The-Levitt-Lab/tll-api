"""Clerk webhook handlers for user sync.

Clerk sends webhook events when users are created, updated, or deleted.
This enables real-time sync between Clerk and our database.

To set up:
1. Go to Clerk Dashboard > Webhooks
2. Add endpoint: https://your-api.com/api/v1/webhooks/clerk
3. Select events: user.created, user.updated, user.deleted
4. Copy the signing secret to CLERK_WEBHOOK_SECRET env var
"""
from __future__ import annotations

import hashlib
import hmac
import logging
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from db.session import get_db_session
from repositories import get_user_by_clerk_id, get_user_by_email, update_user
from repositories.user_repository import create_user, _generate_unique_username
from schemas.user import UserCreate

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter()


async def verify_clerk_webhook(
    request: Request,
    svix_id: str | None = Header(None, alias="svix-id"),
    svix_timestamp: str | None = Header(None, alias="svix-timestamp"),
    svix_signature: str | None = Header(None, alias="svix-signature"),
) -> bytes:
    """
    Verify the Clerk webhook signature using Svix headers.
    
    Clerk uses Svix for webhook delivery, which signs payloads using HMAC-SHA256.
    """
    if not settings.CLERK_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook secret not configured"
        )
    
    if not all([svix_id, svix_timestamp, svix_signature]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Svix headers"
        )
    
    body = await request.body()
    
    # Construct the signed payload
    signed_payload = f"{svix_id}.{svix_timestamp}.{body.decode('utf-8')}"
    
    # Extract the secret (remove "whsec_" prefix if present)
    secret = settings.CLERK_WEBHOOK_SECRET
    if secret.startswith("whsec_"):
        secret = secret[6:]
    
    # Decode the base64 secret
    import base64
    try:
        secret_bytes = base64.b64decode(secret)
    except Exception:
        # If it's not base64, use it as-is
        secret_bytes = secret.encode()
    
    # Compute expected signature
    expected_sig = hmac.new(
        secret_bytes,
        signed_payload.encode(),
        hashlib.sha256
    ).digest()
    expected_sig_b64 = base64.b64encode(expected_sig).decode()
    
    # svix-signature can contain multiple signatures (versioned)
    # Format: "v1,<sig1> v1,<sig2>"
    signatures = svix_signature.split(" ")
    valid = False
    for sig in signatures:
        if "," in sig:
            version, sig_value = sig.split(",", 1)
            if version == "v1":
                if hmac.compare_digest(sig_value, expected_sig_b64):
                    valid = True
                    break
    
    if not valid:
        logger.warning(f"Invalid webhook signature. ID: {svix_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )
    
    return body


@router.post("/clerk")
async def handle_clerk_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    body: bytes = Depends(verify_clerk_webhook),
) -> dict[str, Any]:
    """
    Handle Clerk webhook events.
    
    Supported events:
    - user.created: Create user in our database
    - user.updated: Update user info (email, name)
    - user.deleted: Deactivate user (soft delete)
    """
    import json
    
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    
    event_type = payload.get("type")
    data = payload.get("data", {})
    
    logger.info(f"Received Clerk webhook: {event_type}")
    
    if event_type == "user.created":
        await handle_user_created(db, data)
    elif event_type == "user.updated":
        await handle_user_updated(db, data)
    elif event_type == "user.deleted":
        await handle_user_deleted(db, data)
    else:
        logger.debug(f"Ignoring unhandled event type: {event_type}")
    
    return {"received": True}


async def handle_user_created(db: AsyncSession, data: dict) -> None:
    """Handle user.created event - create user in our database."""
    clerk_user_id = data.get("id")
    if not clerk_user_id:
        logger.warning("user.created event missing user ID")
        return
    
    # Check if user already exists (could happen if they logged in before webhook arrived)
    existing = await get_user_by_clerk_id(db, clerk_user_id)
    if existing:
        logger.debug(f"User {clerk_user_id} already exists, skipping creation")
        return
    
    # Extract email from email_addresses array
    email = _extract_primary_email(data)
    if not email:
        logger.warning(f"user.created event for {clerk_user_id} has no email")
        return
    
    # Check by email as fallback (user might have logged in before we had clerk_user_id tracking)
    existing_by_email = await get_user_by_email(db, email)
    if existing_by_email:
        # Backfill clerk_user_id
        if not existing_by_email.clerk_user_id:
            existing_by_email.clerk_user_id = clerk_user_id
            await update_user(db, existing_by_email)
            logger.info(f"Backfilled clerk_user_id for user {email}")
        return
    
    # Build full name
    first_name = data.get("first_name") or ""
    last_name = data.get("last_name") or ""
    full_name = f"{first_name} {last_name}".strip() or email.split("@")[0]
    
    # Create the user
    user_in = UserCreate(email=email, full_name=full_name, clerk_user_id=clerk_user_id)
    
    try:
        from services.user_service import create_user_service
        await create_user_service(db, user_in)
        logger.info(f"Created user from webhook: {email} ({clerk_user_id})")
    except Exception as e:
        logger.error(f"Failed to create user from webhook: {e}")
        # Don't raise - webhook should return 200 to prevent retries


async def handle_user_updated(db: AsyncSession, data: dict) -> None:
    """Handle user.updated event - update user info in our database."""
    clerk_user_id = data.get("id")
    if not clerk_user_id:
        return
    
    user = await get_user_by_clerk_id(db, clerk_user_id)
    if not user:
        # User doesn't exist in our DB yet - might not have logged in
        # We could create them here, but let's wait for first login
        logger.debug(f"user.updated for unknown user {clerk_user_id}, ignoring")
        return
    
    # Update email if changed
    new_email = _extract_primary_email(data)
    if new_email and new_email != user.email:
        user.email = new_email
    
    # Update name if changed
    first_name = data.get("first_name") or ""
    last_name = data.get("last_name") or ""
    new_full_name = f"{first_name} {last_name}".strip()
    if new_full_name and new_full_name != user.full_name:
        user.full_name = new_full_name
    
    await update_user(db, user)
    logger.info(f"Updated user from webhook: {user.email}")


async def handle_user_deleted(db: AsyncSession, data: dict) -> None:
    """Handle user.deleted event - soft delete (deactivate) the user."""
    clerk_user_id = data.get("id")
    if not clerk_user_id:
        return
    
    user = await get_user_by_clerk_id(db, clerk_user_id)
    if not user:
        logger.debug(f"user.deleted for unknown user {clerk_user_id}, ignoring")
        return
    
    # Soft delete - just mark as inactive
    user.is_active = False
    await update_user(db, user)
    logger.info(f"Deactivated user from webhook: {user.email}")


def _extract_primary_email(data: dict) -> str | None:
    """Extract the primary email address from Clerk user data."""
    email_addresses = data.get("email_addresses", [])
    primary_email_id = data.get("primary_email_address_id")
    
    # Try to find the primary email
    for email_obj in email_addresses:
        if email_obj.get("id") == primary_email_id:
            return email_obj.get("email_address")
    
    # Fallback to first verified email
    for email_obj in email_addresses:
        if email_obj.get("verification", {}).get("status") == "verified":
            return email_obj.get("email_address")
    
    # Fallback to first email
    if email_addresses:
        return email_addresses[0].get("email_address")
    
    return None

