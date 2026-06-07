"""
Main AI agent logic: receives a CAP job, verifies payment, executes the task.
"""

import os
from dotenv import load_dotenv
from tasks import TASK_REGISTRY
from payment import verify_payment_by_tx, verify_payment_wait_for_transfer
from cap_protocol import JobRequest, JobResponse, sign_response

load_dotenv()

# Load agent configuration
AGENT_PRIVATE_KEY = os.getenv("AGENT_PRIVATE_KEY")


def process_job(job: JobRequest) -> JobResponse:
    """
    Core agent function:
    1. Check payment (if required)
    2. Execute the requested task
    3. Return signed response
    """
    # Step 1: payment verification
    if job.payment_tx_hash:
        paid = verify_payment_by_tx(job.payment_tx_hash)
    else:
        # If no tx hash provided, wait for any transfer from the registered user
        paid = verify_payment_wait_for_transfer()

    if not paid:
        return JobResponse(
            job_id=job.job_id,
            status="failed",
            result=None,
            error="Payment not confirmed on testnet"
        )

    # Step 2: execute the task
    if job.task not in TASK_REGISTRY:
        return JobResponse(
            job_id=job.job_id,
            status="failed",
            result=None,
            error=f"Unknown task: {job.task}"
        )

    try:
        task_func = TASK_REGISTRY[job.task]
        result = task_func(job.parameters)
        response = JobResponse(
            job_id=job.job_id,
            status="completed",
            result=result,
        )
    except Exception as e:
        response = JobResponse(
            job_id=job.job_id,
            status="failed",
            result=None,
            error=str(e)
        )

    # Step 3: sign the response (CAP compatibility)
    if AGENT_PRIVATE_KEY:
        signature = sign_response(response, AGENT_PRIVATE_KEY)
        response.signature = signature

    return response
