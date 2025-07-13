#!/usr/bin/env python3
"""
Script to test contract with Flask app parameters
"""

import os
import json
import hashlib
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

GANACHE_URL = os.getenv("GANACHE_URL", "http://127.0.0.1:7545")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

def test_flask_parameters():
    print("=== Testing with Flask App Parameters ===")
    
    # Connect to Ganache
    try:
        web3 = Web3(Web3.HTTPProvider(GANACHE_URL))
        if not web3.is_connected():
            print(f"❌ Failed to connect to Ganache at {GANACHE_URL}")
            return
        print(f"✅ Connected to Ganache at {GANACHE_URL}")
    except Exception as e:
        print(f"❌ Error connecting to Ganache: {e}")
        return
    
    # Load contract
    try:
        with open("build/contracts/EHRContract.json") as f:
            contract_abi = json.load(f)["abi"]
        
        contract = web3.eth.contract(
            address=CONTRACT_ADDRESS,
            abi=contract_abi
        )
        print(f"✅ Loaded contract at {CONTRACT_ADDRESS}")
    except Exception as e:
        print(f"❌ Error loading contract: {e}")
        return
    
    # Get account
    account = web3.eth.accounts[0]
    print(f"📋 Using account: {account}")
    
    # Test with Flask app parameters
    test_file_hash = "a" * 64  # 64 character hex string (like SHA256)
    test_ipfs_hash = "test_ipfs_hash"  # Exactly what Flask app uses
    test_filename = "test_file.txt"
    test_record_type = "medical_file"
    
    print(f"\n🧪 Flask app parameters:")
    print(f"  file_hash: '{test_file_hash}' (length: {len(test_file_hash)})")
    print(f"  ipfs_hash: '{test_ipfs_hash}' (length: {len(test_ipfs_hash)})")
    print(f"  filename: '{test_filename}' (length: {len(test_filename)})")
    print(f"  record_type: '{test_record_type}' (length: {len(test_record_type)})")
    
    # Check account role first
    try:
        is_admin = contract.functions.isAdmin().call({'from': account})
        is_doctor = contract.functions.isDoctor(account).call()
        print(f"\n🔍 Account roles:")
        print(f"  Admin: {'✅ Yes' if is_admin else '❌ No'}")
        print(f"  Doctor: {'✅ Yes' if is_doctor else '❌ No'}")
        
        if not is_admin and not is_doctor:
            print("❌ Account has no required roles!")
            return
    except Exception as e:
        print(f"❌ Error checking roles: {e}")
        return
    
    # Try to call uploadFile with Flask parameters
    print(f"\n🚀 Attempting to call uploadFile with Flask parameters...")
    try:
        tx = contract.functions.uploadFile(
            test_file_hash,
            test_ipfs_hash,
            test_filename,
            test_record_type
        ).transact({'from': account})
        
        print(f"✅ Upload successful! Transaction: {tx.hex()}")
        
        # Wait for transaction receipt
        receipt = web3.eth.wait_for_transaction_receipt(tx)
        print(f"✅ Transaction confirmed in block {receipt.blockNumber}")
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        print(f"Error type: {type(e)}")
        
        # Try to get more details
        if hasattr(e, 'args') and e.args:
            print(f"Error args: {e.args}")
        
        # Check if it's a revert
        if "revert" in str(e).lower():
            print("\n🔍 This is a revert error. Let's try with different IPFS hash lengths:")
            
            # Test with different IPFS hash lengths
            test_hashes = [
                "QmTestHash123456789012345678901234567890123456789012345678901234567890",  # 70 chars
                "QmTestHash12345678901234567890123456789012345678901234567890123456789",   # 69 chars
                "QmTestHash1234567890123456789012345678901234567890123456789012345678",    # 68 chars
                "QmTestHash123456789012345678901234567890123456789012345678901234567",     # 67 chars
                "QmTestHash12345678901234567890123456789012345678901234567890123456",      # 66 chars
                "QmTestHash1234567890123456789012345678901234567890123456789012345",       # 65 chars
                "QmTestHash123456789012345678901234567890123456789012345678901234",        # 64 chars
                "QmTestHash12345678901234567890123456789012345678901234567890123",         # 63 chars
                "QmTestHash1234567890123456789012345678901234567890123456789012",          # 62 chars
                "QmTestHash123456789012345678901234567890123456789012345678901",           # 61 chars
                "QmTestHash12345678901234567890123456789012345678901234567890",            # 60 chars
            ]
            
            for i, test_hash in enumerate(test_hashes):
                print(f"\n🧪 Testing with IPFS hash length {len(test_hash)}: '{test_hash}'")
                try:
                    tx = contract.functions.uploadFile(
                        test_file_hash,
                        test_hash,
                        test_filename,
                        test_record_type
                    ).transact({'from': account})
                    print(f"✅ Success with length {len(test_hash)}! Transaction: {tx.hex()}")
                    break
                except Exception as e2:
                    print(f"❌ Failed with length {len(test_hash)}: {e2}")

if __name__ == "__main__":
    test_flask_parameters() 