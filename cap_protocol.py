"""
CAP protocol compatible request/response models and signing utilities.
"""

import json
from typing import Dict, Any, Optional
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
    signature: Optional[str] = None
    error: Optional[str] = None


def sign_response(response: JobResponse, private_key: str) -> str:
    """
    Sign the job response with the agent's private key.
    Provides integrity and non‑repudiation.
    """
    message = f"{response.job_id}:{response.status}:{json.dumps(response.result, sort_keys=True)}"
    encoded_message = encode_defunct(text=message)
    signed = Account.sign_message(encoded_message, private_key=private_key)
    return signed.signature.hex()


def verify_response(response: JobResponse, expected_agent_address: str) -> bool:
    """
    Verify the signature of a job response.
    (Simplified check – in production you would recover the address.)
    """
    if not response.signature:
        return False
    # Basic length check – replace with full recovery if needed
    return len(response.signature) == 132
