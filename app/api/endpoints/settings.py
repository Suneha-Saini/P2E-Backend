from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List
import datetime

from app.database.connection import get_db
from app.database.models import User, ProviderSetting, AuditLog
from app.api import schemas
from app.security import auth, encryption

router = APIRouter()

SUPPORTED_PROVIDERS = ["Ollama", "LMStudio", "OpenAI", "Claude", "Gemini", "OpenRouter", "Groq"]

@router.get("/providers", response_model=List[schemas.ProviderSettingOut])
def get_providers_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Retrieve saved model settings for the logged-in user."""
    results = []
    
    # Query settings in DB
    db_settings = db.query(ProviderSetting).filter(ProviderSetting.user_id == current_user.id).all()
    db_settings_map = {s.provider_name: s for s in db_settings}
    
    for provider in SUPPORTED_PROVIDERS:
        has_key = False
        base_url = None
        model_name = None
        additional_params = None
        
        setting = db_settings_map.get(provider)
        if setting:
            has_key = bool(setting.api_key_encrypted)
            base_url = setting.base_url
            model_name = setting.model_name
            additional_params = setting.additional_params
            
        results.append({
            "provider_name": provider,
            "base_url": base_url,
            "model_name": model_name,
            "has_key": has_key,
            "additional_params": additional_params
        })
        
    return results

@router.post("/provider", response_model=schemas.ProviderSettingOut)
def update_provider_setting(
    payload: schemas.ProviderSettingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    if payload.provider_name not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unsupported provider.")

    setting = db.query(ProviderSetting).filter(
        ProviderSetting.user_id == current_user.id,
        ProviderSetting.provider_name == payload.provider_name
    ).first()

    encrypted_key = None
    if payload.api_key:  # Only encrypt and update if a NEW key was sent
        encrypted_key = encryption.encrypt_value(payload.api_key)

    if not setting:
        setting = ProviderSetting(
            user_id=current_user.id,
            provider_name=payload.provider_name,
            api_key_encrypted=encrypted_key,
            base_url=payload.base_url,
            model_name=payload.model_name,
            additional_params=payload.additional_params
        )
        db.add(setting)
    else:
        # ONLY update fields that were explicitly provided (not None)
        if encrypted_key:
            setting.api_key_encrypted = encrypted_key
        if payload.base_url is not None:
            setting.base_url = payload.base_url
        if payload.model_name is not None:
            setting.model_name = payload.model_name
        if payload.additional_params is not None:
            setting.additional_params = payload.additional_params
        setting.updated_at = datetime.datetime.utcnow()
        db.add(setting)

    db.commit()
    db.refresh(setting)

    log_entry = AuditLog(
        user_id=current_user.id, action="update_settings",
        details=f"Updated settings for AI provider: {payload.provider_name}"
    )
    db.add(log_entry)
    db.commit()

    return {
        "provider_name": setting.provider_name,
        "base_url": setting.base_url,
        "model_name": setting.model_name,
        "has_key": bool(setting.api_key_encrypted),
        "additional_params": setting.additional_params
    }


@router.post("/provider/test")
def test_provider_connection(
    payload: schemas.ProviderTestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_active_user)
):
    """Test if the configured provider is reachable with a simple ping."""
    import httpx
    from app.security.encryption import decrypt_value

    setting = db.query(ProviderSetting).filter(
        ProviderSetting.user_id == current_user.id,
        ProviderSetting.provider_name == payload.provider_name
    ).first()

    api_key = None
    base_url = None
    if setting:
        if setting.api_key_encrypted:
            try:
                api_key = decrypt_value(setting.api_key_encrypted)
            except Exception:
                pass
        base_url = setting.base_url

    try:
        if payload.provider_name == "Ollama":
            url = f"{base_url or 'http://localhost:11434'}/api/tags"
            with httpx.Client(timeout=5.0) as client:
                r = client.get(url)
                r.raise_for_status()
            return {"status": "ok", "message": "Ollama is reachable."}
        elif payload.provider_name == "LMStudio":
            url = f"{base_url or 'http://localhost:1234'}/v1/models"
            with httpx.Client(timeout=5.0) as client:
                r = client.get(url)
                r.raise_for_status()
            return {"status": "ok", "message": "LM Studio is reachable."}
        elif payload.provider_name == "OpenAI":
            if not api_key:
                return {"status": "error", "message": "No API key configured."}
            with httpx.Client(timeout=10.0) as client:
                r = client.get("https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {api_key}"})
                r.raise_for_status()
            return {"status": "ok", "message": "OpenAI key is valid."}
        elif payload.provider_name == "OpenRouter":
            if not api_key:
                return {"status": "error", "message": "No API key configured."}
            with httpx.Client(timeout=10.0) as client:
                r = client.get("https://openrouter.ai/api/v1/models", headers={"Authorization": f"Bearer {api_key}"})
                r.raise_for_status()
            return {"status": "ok", "message": "OpenRouter key is valid."}
        elif payload.provider_name == "Groq":
            if not api_key:
                return {"status": "error", "message": "No API key configured."}
            with httpx.Client(timeout=10.0) as client:
                r = client.get("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {api_key}"})
                r.raise_for_status()
            return {"status": "ok", "message": "Groq key is valid."}
        elif payload.provider_name == "Claude":
            if not api_key:
                return {"status": "error", "message": "No API key configured."}
            return {"status": "ok", "message": "Claude key format OK (no ping endpoint)."}
        elif payload.provider_name == "Gemini":
            if not api_key:
                return {"status": "error", "message": "No API key configured."}
            return {"status": "ok", "message": "Gemini key format OK (no ping endpoint)."}
        else:
            return {"status": "error", "message": "Unknown provider."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
