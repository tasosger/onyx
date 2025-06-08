import base64
import json
import uuid
from typing import Any

import requests
from fastapi import Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ee.onyx.configs.app_configs import OAUTH_MICROSOFT_CLIENT_ID, OAUTH_MICROSOFT_CLIENT_SECRET
from ee.onyx.server.oauth.api_router import router
from onyx.auth.users import current_admin_user
from onyx.configs.app_configs import DEV_MODE, WEB_DOMAIN
from onyx.configs.constants import DocumentSource
from onyx.db.credentials import create_credential
from onyx.db.engine import get_current_tenant_id, get_session
from onyx.db.models import User
from onyx.redis.redis_pool import get_redis_client
from onyx.server.documents.models import CredentialBase


class OneDriveOAuth:
    class OAuthSession(BaseModel):
        email: str
        redirect_on_success: str | None 

    CLIENT_ID = OAUTH_MICROSOFT_CLIENT_ID
    CLIENT_SECRET = OAUTH_MICROSOFT_CLIENT_SECRET
    AUTHORITY = "https://login.microsoftonline.com/common"
    TOKEN_URL = f"{AUTHORITY}/oauth2/v2.0/token"
    AUTH_URL = f"{AUTHORITY}/oauth2/v2.0/authorize"
    SCOPE = "Files.Read offline_access"
    REDIRECT_URI = f"{WEB_DOMAIN}/admin/connectors/onedrive/oauth/callback"
    DEV_REDIRECT_URI = f"https://redirectmeto.com/{REDIRECT_URI}"

    @classmethod
    def _generate_oauth_url_helper(cls, redirect_uri: str, state: str) -> str:
        params = {
            "client_id": cls.CLIENT_ID,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": cls.SCOPE,
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{cls.AUTH_URL}?{query_string}"

    @classmethod
    def generate_oauth_url(cls, state: str) -> str:
        return cls._generate_oauth_url_helper(cls.REDIRECT_URI, state)

    @classmethod
    def generate_dev_oauth_url(cls, state: str) -> str:
        return cls._generate_oauth_url_helper(cls.DEV_REDIRECT_URI, state)

    @classmethod
    def session_dump_json(cls, email: str, redirect_on_success: str | None) -> str:
        session = cls.OAuthSession(
            email=email,
            redirect_on_success=redirect_on_success,
        )
        return session.model_dump_json()

    @classmethod
    def parse_session(cls, session_json: str) -> OAuthSession:
        return cls.OAuthSession.model_validate_json(session_json)


@router.post("/connector/onedrive/callback")
def handle_onedrive_oauth_callback(
    code: str,
    state: str,
    user: User = Depends(current_admin_user),
    db_session: Session = Depends(get_session),
    tenant_id: str | None = Depends(get_current_tenant_id),
) -> JSONResponse:
    if not OneDriveOAuth.CLIENT_ID or not OneDriveOAuth.CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="OneDrive client ID or client secret is not configured.",
        )

    r = get_redis_client(tenant_id=tenant_id)

    padded_state = state + "=" * (-len(state) % 4) 
    uuid_bytes = base64.urlsafe_b64decode(padded_state)
    oauth_uuid = uuid.UUID(bytes=uuid_bytes)
    oauth_uuid_str = str(oauth_uuid)

    r_key = f"da_oauth:{oauth_uuid_str}"

    session_json_bytes = r.get(r_key)
    if not session_json_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"OneDrive OAuth failed - OAuth state key not found: key={r_key}",
        )

    session_json = session_json_bytes.decode("utf-8")
    try:
        session = OneDriveOAuth.parse_session(session_json)

        if not DEV_MODE:
            redirect_uri = OneDriveOAuth.REDIRECT_URI
        else:
            redirect_uri = OneDriveOAuth.DEV_REDIRECT_URI

        response = requests.post(
            OneDriveOAuth.TOKEN_URL,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "client_id": OneDriveOAuth.CLIENT_ID,
                "client_secret": OneDriveOAuth.CLIENT_SECRET,
                "code": code,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )

        response.raise_for_status()
        token_response: dict[str, Any] = response.json()

        credential_dict = {
            "token": token_response["access_token"],
            "refresh_token": token_response["refresh_token"],
            "authentication_method": "oauth_interactive",
        }

        credential_info = CredentialBase(
            credential_json=credential_dict,
            admin_public=True,
            source=DocumentSource.ONEDRIVE,
            name="OAuth (interactive)",
        )

        create_credential(credential_info, user, db_session)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"An error occurred during OneDrive OAuth: {str(e)}",
            },
        )
    finally:
        r.delete(r_key)

    return JSONResponse(
        content={
            "success": True,
            "message": "OneDrive OAuth completed successfully.",
            "finalize_url": None,
            "redirect_on_success": session.redirect_on_success,
        }
    ) 