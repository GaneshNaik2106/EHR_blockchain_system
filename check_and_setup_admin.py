#!/usr/bin/env python3
"""
Script to check and setup admin role for the current account
"""

import os
import json
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

GANACHE_URL = os.getenv("GANACHE_URL", "http://127.0.0.1:7545")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

def main():
    print("=== Admin Role Check and Setup ===")
    
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
    
    # Get accounts
    accounts = web3.eth.accounts
    print(f"📋 Available accounts: {len(accounts)}")
    for i, account in enumerate(accounts):
        balance = web3.from_wei(web3.eth.get_balance(account), 'ether')
        print(f"  {i}: {account} (Balance: {balance} ETH)")
    
    # Check first account's role
    account = accounts[0]
    print(f"\n🔍 Checking role for account: {account}")
    
    try:
        is_admin = contract.functions.isAdmin().call({'from': account})
        is_doctor = contract.functions.isDoctor(account).call()
        
        print(f"  Admin role: {'✅ Yes' if is_admin else '❌ No'}")
        print(f"  Doctor role: {'✅ Yes' if is_doctor else '❌ No'}")
        
        if not is_admin and not is_doctor:
            print("\n⚠️  Account has no roles. Setting up admin role...")
            
            # Try to set admin role
            try:
                tx = contract.functions.addAdmin(account).transact({'from': account})
                print(f"✅ Admin role assigned! Transaction: {tx.hex()}")
                
                # Verify the role was set
                is_admin_after = contract.functions.isAdmin().call({'from': account})
                print(f"  Admin role after setup: {'✅ Yes' if is_admin_after else '❌ No'}")
                
            except Exception as e:
                print(f"❌ Failed to set admin role: {e}")
                print("This might be because the contract doesn't have an addAdmin function")
                print("or the account doesn't have permission to call it.")
        
    except Exception as e:
        print(f"❌ Error checking roles: {e}")

if __name__ == "__main__":
    main() 