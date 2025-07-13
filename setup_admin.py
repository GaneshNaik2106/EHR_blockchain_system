#!/usr/bin/env python3
"""
Script to set up initial admin role for the current account
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.blockchain_service import BlockchainService

def setup_admin():
    """Set up admin role for the current account"""
    print("Setting up admin role...")
    
    # Initialize blockchain service
    blockchain_service = BlockchainService()
    
    if not blockchain_service.is_connected:
        print("ERROR: Not connected to blockchain")
        return False
    
    if not blockchain_service.account:
        print("ERROR: No account set")
        return False
    
    print(f"Current account: {blockchain_service.account}")
    
    # Check if account already has admin role
    is_admin = blockchain_service.check_role("admin")
    print(f"Current account has admin role: {is_admin}")
    
    if is_admin:
        print("Account already has admin role. No action needed.")
        return True
    
    # Try to add admin role (this might fail if no admin exists yet)
    print("Attempting to add admin role...")
    result = blockchain_service.add_admin_role(blockchain_service.account)
    
    if result['success']:
        print(f"Successfully added admin role. Transaction: {result['transaction_hash']}")
        return True
    else:
        print(f"Failed to add admin role: {result['error']}")
        
        # If this is the first admin, we need to use a different approach
        print("This might be the first admin. Checking contract owner...")
        
        try:
            # Try to get the contract owner (deployer)
            owner = blockchain_service.contract.functions.owner().call()
            print(f"Contract owner: {owner}")
            
            if owner == blockchain_service.account:
                print("Current account is the contract owner. Trying to add admin directly...")
                # Try to call addAdmin directly
                tx = blockchain_service.contract.functions.addAdmin(blockchain_service.account).transact({
                    'from': blockchain_service.account
                })
                print(f"Successfully added admin role. Transaction: {tx.hex()}")
                return True
            else:
                print(f"Contract owner is {owner}, not current account")
                return False
                
        except Exception as e:
            print(f"Error checking contract owner: {e}")
            return False

if __name__ == "__main__":
    load_dotenv('config.env')
    
    success = setup_admin()
    if success:
        print("Admin setup completed successfully!")
    else:
        print("Admin setup failed!")
        sys.exit(1) 