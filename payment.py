"""
Testnet payment verification for CAP settlement.
Uses web3.py to check if the required payment has been made.
"""

import os
import time
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL", "https://rpc.sepolia.org")
AGENT_PRIVATE_KEY = os.getenv("AGENT_PRIVATE_KEY")
USER_WALLET_ADDRESS = os.getenv("USER_WALLET_ADDRESS")
REQUIRED_PAYMENT = int(os.getenv("REQUIRED_PAYMENT", "1000000000000000"))  # wei

# Derive agent's wallet address from its private key
if AGENT_PRIVATE_KEY:
    w3_local = Web3()
    agent_account = w3_local.eth.account.from_key(AGENT_PRIVATE_KEY)
    AGENT_ADDRESS = agent_account.address
else:
    AGENT_ADDRESS = None

w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL))


def verify_payment_by_tx(tx_hash: str) -> bool:
    """
    Verify that a given transaction hash corresponds to a payment
    from USER_WALLET_ADDRESS to AGENT_ADDRESS with sufficient value.
    """
    if not w3.is_connected():
        print("⚠️  Cannot connect to Sepolia testnet")
        return False

    if not AGENT_ADDRESS or not USER_WALLET_ADDRESS:
        print("⚠️  Missing agent or user address")
        return False

    try:
        tx = w3.eth.get_transaction(tx_hash)
        # Check sender, recipient and value
        if (tx["from"].lower() == USER_WALLET_ADDRESS.lower() and
            tx["to"].lower() == AGENT_ADDRESS.lower() and
            tx["value"] >= REQUIRED_PAYMENT):
            # Optionally wait for a few confirmations
            time.sleep(3)  # give the network a moment
            return True
    except Exception as e:
        print(f"Error checking transaction: {e}")
    return False


def verify_payment_wait_for_transfer(timeout_seconds: int = 60) -> bool:
    """
    Simplified payment check: wait until USER_WALLET_ADDRESS sends enough funds
    to AGENT_ADDRESS. This is useful for hackathons where the user pays after submitting.
    """
    if not w3.is_connected() or not AGENT_ADDRESS or not USER_WALLET_ADDRESS:
        return False

    start_block = w3.eth.block_number
    end_time = time.time() + timeout_seconds

    while time.time() < end_time:
        current_block = w3.eth.block_number
        # Scan new blocks for relevant transactions
        for block_num in range(start_block, current_block + 1):
            block = w3.eth.get_block(block_num, full_transactions=True)
            for tx in block.transactions:
                if (tx["from"].lower() == USER_WALLET_ADDRESS.lower() and
                    tx["to"] and tx["to"].lower() == AGENT_ADDRESS.lower() and
                    tx["value"] >= REQUIRED_PAYMENT):
                    return True
        start_block = current_block + 1
        time.sleep(5)  # wait for new blocks

    return False
