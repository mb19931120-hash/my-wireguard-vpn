"""
Testnet payment verification for CAP settlement.
"""

import os
import time
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL", "https://rpc.sepolia.org")
AGENT_PRIVATE_KEY = os.getenv("AGENT_PRIVATE_KEY")
USER_WALLET_ADDRESS = os.getenv("USER_WALLET_ADDRESS")
REQUIRED_PAYMENT = int(os.getenv("REQUIRED_PAYMENT", "1000000000000000"))

# Derive agent's wallet address from its private key
if AGENT_PRIVATE_KEY:
    w3_local = Web3()
    agent_account = w3_local.eth.account.from_key(AGENT_PRIVATE_KEY)
    AGENT_ADDRESS = agent_account.address
else:
    AGENT_ADDRESS = None

w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL))


def verify_payment_by_tx(tx_hash: str) -> bool:
    """Verify that a transaction hash is a valid payment from user to agent."""
    if not w3.is_connected() or not AGENT_ADDRESS or not USER_WALLET_ADDRESS:
        return False

    try:
        tx = w3.eth.get_transaction(tx_hash)
        if (tx["from"].lower() == USER_WALLET_ADDRESS.lower() and
            tx["to"].lower() == AGENT_ADDRESS.lower() and
            tx["value"] >= REQUIRED_PAYMENT):
            time.sleep(3)  # wait a few seconds for confirmation
            return True
    except Exception as e:
        print(f"Error checking transaction: {e}")
    return False


def verify_payment_wait_for_transfer(timeout_seconds: int = 60) -> bool:
    """Wait for a payment from USER_WALLET_ADDRESS to AGENT_ADDRESS."""
    if not w3.is_connected() or not AGENT_ADDRESS or not USER_WALLET_ADDRESS:
        return False

    start_block = w3.eth.block_number
    end_time = time.time() + timeout_seconds

    while time.time() < end_time:
        current_block = w3.eth.block_number
        for block_num in range(start_block, current_block + 1):
            block = w3.eth.get_block(block_num, full_transactions=True)
            for tx in block.transactions:
                if (tx["from"].lower() == USER_WALLET_ADDRESS.lower() and
                    tx["to"] and tx["to"].lower() == AGENT_ADDRESS.lower() and
                    tx["value"] >= REQUIRED_PAYMENT):
                    return True
        start_block = current_block + 1
        time.sleep(5)
    return False
