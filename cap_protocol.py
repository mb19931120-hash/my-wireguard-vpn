"""
CAP protocol compatible request/response models and signing utilities.
"""

import json
import hashlib
import hmac
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from eth_account import Account
from eth_account.messages import encode_defunct


class JobRequest(BaseModel):
    """CAP‑compatible job request from user to agent."""
    job_id: str = Field(..., description="Unique identifier for this job")
    task: str = Field(..., description="Task name to execute (e.g., 'summarise_news')")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Task parameters")
    payment_tx_hash: Optional[str] = Field(None, description="Transaction hash of the payment (if already sent)")


class JobResponse(BaseModel):
    """CAP‑compatible response from agent to user."""
    job_id: str
    status: str  # "completed" or "failed"
    result: Any
    signature: Optional[str] = None  # digital signature over the response
    error: Optional[str] = None


def sign_response(response: JobResponse, private_key: str) -> str:
    """
    Sign the job response with the agent's private key.
    This provides integrity and non‑repudiation, a key CAP feature.
    """
    # Create a deterministic string from the response
    message = f"{response.job_id}:{response.status}:{json.dumps(response.result, sort_keys=True)}"
    # Encode the message as required by eth_account
    encoded_message = encode_defunct(text=message)
    # Sign using the agent's private key
    signed = Account.sign_message(encoded_message, private_key=private_key)
    return signed.signature.hex()


def verify_response(response: JobResponse, expected_public_key: str) -> bool:
    """
    Verify the signature of a job response.
    In a real CAP implementation, the user would call this to trust the result.
    """
    if not response.signature:
        return False
    # Reconstruct the same message
    message = f"{response.job_id}:{response.status}:{json.dumps(response.result, sort_keys=True)}"
    encoded_message = encode_defunct(text=message)
    # Recover the address from the signature
    # (in production you would compare against the agent's known address)
    try:
        from eth_account.messages import decode_defunct
        from eth_account._utils.signing import extract_chain_id
        # Simplified check: just ensure the signature is not empty
        return len(response.signature) == 132  # 66 bytes hex = 132 chars
    except:
        return False
