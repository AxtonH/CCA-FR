"""
Utilities for sending mail through Microsoft Graph using Azure AD application credentials.
"""

import base64
import json
import os
from typing import Dict, Iterable, List, Optional, Tuple, Union

import requests
from msal import ConfidentialClientApplication

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"
DEFAULT_SCOPE = ["https://graph.microsoft.com/.default"]


class AzureEmailConfigError(RuntimeError):
    """Raised when the Azure email configuration is incomplete."""


def _load_azure_config() -> Dict[str, str]:
    """Load required Azure AD configuration values from environment variables."""
    tenant_id = os.getenv("AZURE_TENANT_ID", "").strip()
    client_id = os.getenv("AZURE_CLIENT_ID", "").strip()
    client_secret = os.getenv("AZURE_CLIENT_SECRET", "").strip()

    if not all([tenant_id, client_id, client_secret]):
        raise AzureEmailConfigError(
            "Missing Azure configuration. Ensure AZURE_TENANT_ID, AZURE_CLIENT_ID, and AZURE_CLIENT_SECRET are set."
        )

    return {
        "tenant_id": tenant_id,
        "client_id": client_id,
        "client_secret": client_secret,
    }


def _build_client_app() -> ConfidentialClientApplication:
    """Create an MSAL confidential client application."""
    config = _load_azure_config()
    authority = f"https://login.microsoftonline.com/{config['tenant_id']}"

    return ConfidentialClientApplication(
        config["client_id"],
        authority=authority,
        client_credential=config["client_secret"],
    )


def _get_access_token(scopes: Optional[Iterable[str]] = None) -> str:
    """Acquire an application access token for the provided scopes."""
    client_app = _build_client_app()
    scopes = list(scopes or DEFAULT_SCOPE)

    # Try cached token first
    result = client_app.acquire_token_silent(scopes, account=None)

    if not result:
        result = client_app.acquire_token_for_client(scopes=scopes)

    if "access_token" not in result:
        error = result.get("error_description") or result
        raise RuntimeError(f"Failed to acquire Azure access token: {error}")

    return result["access_token"]


def _normalize_recipients(addresses: Union[str, List[str]]) -> List[Dict[str, Dict[str, str]]]:
    """Convert input email addresses into Graph-compatible recipient objects."""
    if isinstance(addresses, str):
        addresses = [addr.strip() for addr in addresses.split(",") if addr.strip()]

    recipients: List[Dict[str, Dict[str, str]]] = []
    for address in addresses or []:
        if not address:
            continue
        recipients.append({"emailAddress": {"address": address}})
    return recipients


def _normalize_attachments(attachments: Optional[List]) -> List[Dict]:
    """Convert application attachments into Graph fileAttachment objects."""
    graph_attachments: List[Dict] = []

    if not attachments:
        return graph_attachments

    for attachment in attachments:
        raw_bytes: Optional[bytes] = None
        filename: Optional[str] = None

        if isinstance(attachment, dict):
            raw_bytes = attachment.get("data")
            filename = attachment.get("filename")
        elif hasattr(attachment, "read") and hasattr(attachment, "name"):
            attachment.seek(0)
            raw_bytes = attachment.read()
            filename = attachment.name

        if not raw_bytes or not filename:
            continue

        graph_attachments.append(
            {
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": filename,
                "contentType": "application/octet-stream",
                "contentBytes": base64.b64encode(raw_bytes).decode("utf-8"),
            }
        )

    return graph_attachments


def send_email_via_graph(
    sender_email: str,
    recipient_email: str,
    subject: str,
    body: str,
    cc_list: Optional[List[str]] = None,
    attachments: Optional[List] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Send an email using Microsoft Graph.

    Returns a tuple of (success flag, error message if any).
    """
    if not sender_email:
        return False, "Sender email is required for Microsoft Graph."

    token = _get_access_token()

    message_payload = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "HTML",
                "content": body or "",
            },
            "toRecipients": _normalize_recipients(recipient_email),
        },
        "saveToSentItems": True,
    }

    cc_recipients = _normalize_recipients(cc_list or [])
    if cc_recipients:
        message_payload["message"]["ccRecipients"] = cc_recipients

    graph_attachments = _normalize_attachments(attachments)
    if graph_attachments:
        message_payload["message"]["attachments"] = graph_attachments

    url = f"{GRAPH_BASE_URL}/users/{sender_email}/sendMail"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    response = requests.post(url, headers=headers, data=json.dumps(message_payload))

    if response.status_code in (202, 200):
        return True, None

    error_detail = None
    try:
        data = response.json()
        error_detail = data.get("error", {}).get("message") or data
    except Exception:
        error_detail = response.text

    return False, f"Graph sendMail failed ({response.status_code}): {error_detail}"

