"""Persists predictions to Supabase using the user's JWT token."""
import logging
from typing import Optional
from supabase import create_client

log = logging.getLogger(__name__)

async def save_prediction(result, source: str, token: str, settings) -> Optional[str]:
    try:
        client = create_client(settings.supabase_url, settings.supabase_service_role_key)
        user_response = client.auth.get_user(token)
        if not user_response or not user_response.user:
            log.warning("Could not resolve user from token.")
            return None
        user_id = user_response.user.id
        row = {
            "user_id": user_id, "category": result.category,
            "confidence": result.confidence, "is_uncertain": result.is_uncertain,
            "recommendation": result.recommendation, "hardware_command": result.hardware_command,
            "source": source, "model_version": result.model_version,
        }
        response = client.table("predictions").insert(row).execute()
        if response.data:
            return response.data[0]["id"]
    except Exception as e:
        log.warning(f"Failed to save prediction: {e}")
    return None
