#!/usr/bin/env python3
"""
Simple test for BlockchainService
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Load environment variables
load_dotenv('config.env')

def test_simple():
    print("=== Simple BlockchainService Test ===")
    
    try:
        from services.blockchain_service import BlockchainService
        print("✅ Successfully imported BlockchainService")
        
        # Create instance
        service = BlockchainService()
        print("✅ Successfully created BlockchainService instance")
        
        # Check basic properties
        print(f"  Connected: {service.is_connected}")
        print(f"  Contract: {service.contract is not None}")
        print(f"  Account: {service.account}")
        
        if service.is_connected and service.contract and service.account:
            print("✅ All basic properties are set correctly")
            
            # Try a simple upload
            result = service.upload_file_to_blockchain(
                file_hash="a" * 64,
                ipfs_hash="test_hash",
                filename="test.txt",
                record_type="test"
            )
            
            print(f"📋 Upload result: {result}")
            
        else:
            print("❌ Some basic properties are missing")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple() 