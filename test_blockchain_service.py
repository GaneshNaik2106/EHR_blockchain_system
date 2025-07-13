#!/usr/bin/env python3
"""
Script to test BlockchainService class exactly as used in Flask app
"""

import os
import sys
import hashlib
from dotenv import load_dotenv

# Add the app directory to the path so we can import the service
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Load environment variables
load_dotenv('config.env')

from services.blockchain_service import BlockchainService

def test_blockchain_service():
    print("=== Testing BlockchainService Class ===")
    
    # Create a test file hash (like Flask app does)
    test_content = b"test file content"
    file_hash = hashlib.sha256(test_content).hexdigest()
    
    print(f"🧪 Test parameters:")
    print(f"  file_hash: '{file_hash}' (length: {len(file_hash)})")
    print(f"  ipfs_hash: 'test_ipfs_hash' (length: 14)")
    print(f"  filename: 'test_file.txt' (length: 13)")
    print(f"  record_type: 'medical_file' (length: 12)")
    
    # Create BlockchainService instance (like Flask app does)
    print(f"\n🚀 Creating BlockchainService instance...")
    try:
        blockchain_service = BlockchainService()
        print(f"✅ BlockchainService created successfully")
        
        # Check connection status
        print(f"  Connected: {blockchain_service.is_connected}")
        print(f"  Contract loaded: {blockchain_service.contract is not None}")
        print(f"  Account: {blockchain_service.account}")
        
        if not blockchain_service.is_connected:
            print("❌ BlockchainService is not connected!")
            return
            
        if not blockchain_service.contract:
            print("❌ BlockchainService contract is not loaded!")
            return
            
        if not blockchain_service.account:
            print("❌ BlockchainService account is not set!")
            return
        
        # Call upload method (like Flask app does)
        print(f"\n🚀 Calling upload_file_to_blockchain...")
        result = blockchain_service.upload_file_to_blockchain(
            file_hash=file_hash,
            ipfs_hash="test_ipfs_hash",
            filename="test_file.txt",
            record_type="medical_file"
        )
        
        print(f"📋 Result: {result}")
        
        if result.get('success'):
            print(f"✅ Upload successful!")
            print(f"  Transaction hash: {result.get('transaction_hash')}")
            print(f"  File hash: {result.get('file_hash')}")
        else:
            print(f"❌ Upload failed!")
            print(f"  Error: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_blockchain_service() 