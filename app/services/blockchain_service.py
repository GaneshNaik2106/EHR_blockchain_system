import json
import hashlib
from web3 import Web3
from flask import current_app
import os
from dotenv import load_dotenv
from datetime import datetime
from app.services.file_tracker import FileTracker

# Load environment variables
load_dotenv('config.env')

GANACHE_URL = os.getenv("GANACHE_URL", "http://127.0.0.1:7545")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# Load ABI
try:
    with open("build/contracts/EHRContract.json") as f:
        contract_abi = json.load(f)["abi"]
except FileNotFoundError:
    print("Warning: Contract ABI not found. Using mock implementation.")
    contract_abi = []

class BlockchainService:
    def __init__(self):
        self.web3 = None
        self.contract = None
        self.account = None
        self.contract_address = None
        self.contract_abi = None
        self.is_connected = False

        print("DEBUG: Initializing BlockchainService")

        # Try to connect and load contract on initialization
        self.connect_to_ganache()
        if self.is_connected:
            print("DEBUG: Successfully connected to Ganache")
            self.load_contract()
            if self.contract:
                print("DEBUG: Successfully loaded contract")
                self.set_account(0)  # Set first account as default
            else:
                print("DEBUG: Failed to load contract")
        else:
            print("DEBUG: Failed to connect to Ganache")

    def connect_to_ganache(self):
        """Connect to Ganache local blockchain"""
        try:
            if not GANACHE_URL:
                print("GANACHE_URL not configured. Using mock implementation.")
                self.is_connected = False
                return False

            self.web3 = Web3(Web3.HTTPProvider(GANACHE_URL))

            if self.web3.is_connected():
                print(f"Connected to Ganache at {GANACHE_URL}")
                self.is_connected = True
                return True
            else:
                print(f"Failed to connect to Ganache at {GANACHE_URL}")
                self.is_connected = False
                return False
        except Exception as e:
            print(f"Error connecting to Ganache: {e}")
            self.is_connected = False
            return False

    def load_contract(self, contract_address=None, contract_abi_path=None):
        """Load the smart contract"""
        try:
            if not self.is_connected:
                print("Not connected to blockchain. Using mock implementation.")
                return False

            # Use global contract address if not provided
            if not contract_address:
                contract_address = CONTRACT_ADDRESS

            if not contract_address:
                print("CONTRACT_ADDRESS not configured. Using mock implementation.")
                return False

            # Use global ABI if not provided
            if not contract_abi_path and contract_abi:
                self.contract = self.web3.eth.contract(
                    address=contract_address,
                    abi=contract_abi
                )
                self.contract_address = contract_address
                print(f"Loaded contract at {contract_address}")
                return True
            else:
                print("Contract ABI not available. Using mock implementation.")
                return False
        except Exception as e:
            print(f"Error loading contract: {e}")
            return False

    def get_accounts(self):
        """Get available accounts"""
        if self.is_connected and self.web3:
            try:
                accounts = self.web3.eth.accounts
                return [account for account in accounts]
            except Exception as e:
                print(f"Error getting accounts: {e}")
                return []
        else:
            # Mock accounts for testing
            return ["0x1234567890123456789012345678901234567890"]

    def set_account(self, account_index=0):
        """Set the account to use for transactions"""
        accounts = self.get_accounts()
        print(f"DEBUG: Available accounts: {accounts}")
        print(f"DEBUG: Requested account index: {account_index}")

        if accounts and account_index < len(accounts):
            self.account = accounts[account_index]
            print(f"DEBUG: Set account to: {self.account}")
            return self.account
        else:
            print(f"DEBUG: Failed to set account. Available: {len(accounts) if accounts else 0}, Requested: {account_index}")
            return None

    def get_balance(self):
        """Get balance of current account"""
        if self.account and self.is_connected and self.web3:
            try:
                balance_wei = self.web3.eth.get_balance(self.account)
                balance_eth = self.web3.from_wei(balance_wei, 'ether')
                return float(balance_eth)
            except Exception as e:
                print(f"Error getting balance: {e}")
                return 0
        elif self.account:
            return 100.0  # Mock balance
        return 0

    def hash_record(self, record_data):
        """Hash a medical record for blockchain storage"""
        try:
            # Convert record data to a consistent string format
            if isinstance(record_data, dict):
                # Sort keys to ensure consistent ordering
                sorted_data = dict(sorted(record_data.items()))
                record_string = json.dumps(sorted_data, sort_keys=True, default=str)
            else:
                record_string = str(record_data)
            
            # Create SHA-256 hash
            record_hash = hashlib.sha256(record_string.encode('utf-8')).hexdigest()
            return record_hash
        except Exception as e:
            print(f"Error hashing record: {e}")
            return None

    def check_role(self, role_name):
        """Check if current account has a specific role"""
        if self.is_connected and self.contract:
            try:
                if role_name == "admin":
                    has_role = self.contract.functions.isAdmin().call({'from': self.account})
                elif role_name == "doctor":
                    has_role = self.contract.functions.isDoctor(self.account).call()
                else:
                    return False

                return has_role
            except Exception as e:
                print(f"Error checking {role_name} role: {e}")
                return False
        return False

    def upload_file_to_blockchain(self, file_hash, ipfs_hash, filename, record_type):
        """Upload file hash to blockchain"""
        print(f"DEBUG: Attempting to upload file to blockchain")
        print(f"DEBUG: Account: {self.account}")
        print(f"DEBUG: File hash: {file_hash}")
        print(f"DEBUG: IPFS hash: {ipfs_hash}")
        print(f"DEBUG: Filename: {filename}")
        print(f"DEBUG: Record type: {record_type}")

        if self.is_connected and self.contract:
            try:
                # Check if account has required roles
                is_admin = self.check_role("admin")
                is_doctor = self.check_role("doctor")
                print(f"DEBUG: Account roles - Admin: {is_admin}, Doctor: {is_doctor}")

                if not is_admin and not is_doctor:
                    print(f"DEBUG: Account does not have required roles")
                    return {'success': False, 'error': 'Account does not have admin or doctor role'}

                # Validate parameters
                if not file_hash or not ipfs_hash or not filename or not record_type:
                    print(f"DEBUG: Missing required parameters")
                    return {'success': False, 'error': 'Missing required parameters'}

                # Call smart contract function
                print(f"DEBUG: Calling uploadFile with parameters:")
                print(f"  - file_hash: '{file_hash}' (length: {len(file_hash)})")
                print(f"  - ipfs_hash: '{ipfs_hash}' (length: {len(ipfs_hash)})")
                print(f"  - filename: '{filename}' (length: {len(filename)})")
                print(f"  - record_type: '{record_type}' (length: {len(record_type)})")
                
                try:
                    tx = self.contract.functions.uploadFile(
                        file_hash,
                        ipfs_hash,
                        filename,
                        record_type
                    ).transact({'from': self.account})

                    print(f"DEBUG: Transaction successful: {tx.hex()}")

                    return {
                        'success': True,
                        'transaction_hash': tx.hex(),
                        'file_hash': file_hash
                    }
                except Exception as tx_error:
                    print(f"DEBUG: Transaction failed with error: {tx_error}")
                    print(f"DEBUG: Error type: {type(tx_error)}")
                    
                    # Try to get more details about the revert
                    if hasattr(tx_error, 'args') and tx_error.args:
                        print(f"DEBUG: Error args: {tx_error.args}")
                    
                    # Check if it's a revert error
                    if "revert" in str(tx_error).lower():
                        print(f"DEBUG: This is a revert error. Possible causes:")
                        print(f"  - Account doesn't have required role")
                        print(f"  - Invalid parameters")
                        print(f"  - Contract state issue")
                    
                    raise tx_error
                    
            except Exception as e:
                print(f"Error uploading file to blockchain: {e}")
                return {'success': False, 'error': str(e)}
        else:
            # Mock implementation
            print(f"Mock: Uploaded file {filename} with hash {file_hash} to blockchain")
            return {
                'success': True,
                'transaction_hash': '0x' + '0' * 64,
                'file_hash': file_hash
            }

    def verify_file(self, file_hash, current_hash):
        """Verify file integrity against blockchain"""
        print(f"DEBUG: Verifying file hash: {file_hash}")
        print(f"DEBUG: Current hash: {current_hash}")
        
        if self.is_connected and self.contract:
            try:
                # Use the new verifyFileAndLog function for comprehensive verification
                tx = self.contract.functions.verifyFileAndLog(
                    file_hash,
                    current_hash
                ).transact({'from': self.account})
                
                # Get the verification result
                is_valid = self.contract.functions.verifyFile(file_hash, current_hash).call()
                
                return {
                    'success': True,
                    'is_valid': is_valid,
                    'transaction_hash': tx.hex(),
                    'message': 'File verified successfully' if is_valid else 'File verification failed - possible tampering detected'
                }
            except Exception as e:
                print(f"Error verifying file: {e}")
                return {'success': False, 'error': str(e)}
        else:
            # Mock verification
            mock_valid = file_hash == current_hash
            return {
                'success': True,
                'is_valid': mock_valid,
                'transaction_hash': '0x' + '0' * 64,
                'message': 'Mock verification completed'
            }

    def detect_tampering(self, file_hash, current_hash):
        """Detect if a file has been tampered with"""
        print(f"DEBUG: Detecting tampering for file hash: {file_hash}")
        
        if self.is_connected and self.contract:
            try:
                is_tampered, original_hash, current_hash_result = self.contract.functions.detectTampering(
                    file_hash, 
                    current_hash
                ).call()
                
                return {
                    'success': True,
                    'is_tampered': is_tampered,
                    'original_hash': original_hash,
                    'current_hash': current_hash_result,
                    'message': 'Tampering detected' if is_tampered else 'No tampering detected'
                }
            except Exception as e:
                print(f"Error detecting tampering: {e}")
                return {'success': False, 'error': str(e)}
        else:
            # Mock tampering detection
            mock_tampered = file_hash != current_hash
            return {
                'success': True,
                'is_tampered': mock_tampered,
                'original_hash': file_hash,
                'current_hash': current_hash,
                'message': 'Mock tampering detection completed'
            }

    def get_file_info(self, file_hash):
        """Get comprehensive file information from blockchain"""
        print(f"DEBUG: Getting file info for hash: {file_hash}")
        
        if self.is_connected and self.contract:
            try:
                filename, ipfs_hash, upload_time, uploaded_by, is_valid, record_type, verification_count, last_verified, original_hash = self.contract.functions.getFileInfo(file_hash).call()
                
                return {
                    'success': True,
                    'filename': filename,
                    'ipfs_hash': ipfs_hash,
                    'upload_time': upload_time,
                    'uploaded_by': uploaded_by,
                    'is_valid': is_valid,
                    'record_type': record_type,
                    'verification_count': verification_count,
                    'last_verified': last_verified,
                    'original_hash': original_hash
                }
            except Exception as e:
                print(f"Error getting file info: {e}")
                return {'success': False, 'error': str(e)}
        else:
            # Mock file info
            return {
                'success': True,
                'filename': 'mock_file.txt',
                'ipfs_hash': 'QmMockHash123',
                'upload_time': int(datetime.now().timestamp()),
                'uploaded_by': self.account or '0x1234567890123456789012345678901234567890',
                'is_valid': True,
                'record_type': 'medical_file',
                'verification_count': 0,
                'last_verified': 0,
                'original_hash': file_hash
            }

    def get_audit_trail(self, file_hash, limit=10):
        """Get audit trail for a specific file"""
        print(f"DEBUG: Getting audit trail for file hash: {file_hash}")
        
        if self.is_connected and self.contract:
            try:
                audit_entries = self.contract.functions.getRecentAuditEntries(file_hash, limit).call()
                
                formatted_entries = []
                for entry in audit_entries:
                    formatted_entries.append({
                        'timestamp': entry[0],
                        'actor': entry[1],
                        'action': entry[2],
                        'details': entry[3],
                        'success': entry[4]
                    })
                
                return {
                    'success': True,
                    'audit_entries': formatted_entries
                }
            except Exception as e:
                print(f"Error getting audit trail: {e}")
                return {'success': False, 'error': str(e)}
        else:
            # Mock audit trail
            mock_entries = [
                {
                    'timestamp': int(datetime.now().timestamp()),
                    'actor': self.account or '0x1234567890123456789012345678901234567890',
                    'action': 'UPLOAD',
                    'details': 'File uploaded successfully',
                    'success': True
                }
            ]
            return {
                'success': True,
                'audit_entries': mock_entries
            }

    def get_file_statistics(self):
        """Get overall file statistics"""
        print(f"DEBUG: Getting file statistics")
        
        if self.is_connected and self.contract:
            try:
                total_files, valid_files, invalid_files = self.contract.functions.getFileStatistics().call()
                
                return {
                    'success': True,
                    'total_files': total_files,
                    'valid_files': valid_files,
                    'invalid_files': invalid_files
                }
            except Exception as e:
                print(f"Error getting file statistics: {e}")
                return {'success': False, 'error': str(e)}
        else:
            # Mock statistics
            return {
                'success': True,
                'total_files': 5,
                'valid_files': 4,
                'invalid_files': 1
            }

    def get_all_files(self):
        """Get all file hashes from blockchain or local tracker"""
        print(f"DEBUG: Getting all files")
        
        if self.is_connected and self.contract:
            try:
                file_hashes = self.contract.functions.getAllFiles().call()
                
                files_info = []
                for file_hash in file_hashes:
                    file_info = self.get_file_info(file_hash)
                    if file_info['success']:
                        files_info.append({
                            'file_hash': file_hash,
                            **file_info
                        })
                
                return {
                    'success': True,
                    'files': files_info
                }
            except Exception as e:
                print(f"Error getting all files: {e}")
                return {'success': False, 'error': str(e)}
        else:
            # Use local file tracker when blockchain is not connected
            try:
                file_tracker = FileTracker()
                files = file_tracker.get_all_files()
                return {
                    'success': True,
                    'files': files
                }
            except Exception as e:
                print(f"Error getting files from tracker: {e}")
                return {
                    'success': True,
                    'files': []
                }

    def invalidate_file(self, file_hash):
        """Invalidate a file (admin only)"""
        print(f"DEBUG: Invalidating file hash: {file_hash}")
        
        if self.is_connected and self.contract:
            try:
                # Check if account has admin role
                is_admin = self.check_role("admin")
                if not is_admin:
                    return {'success': False, 'error': 'Only admin can invalidate files'}

                tx = self.contract.functions.invalidateFile(file_hash).transact({'from': self.account})
                
                return {
                    'success': True,
                    'transaction_hash': tx.hex(),
                    'message': 'File invalidated successfully'
                }
            except Exception as e:
                print(f"Error invalidating file: {e}")
                return {'success': False, 'error': str(e)}
        else:
            # Mock invalidation
            return {
                'success': True,
                'transaction_hash': '0x' + '0' * 64,
                'message': 'Mock file invalidation completed'
            }