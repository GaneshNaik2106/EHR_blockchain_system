import json
import hashlib
from web3 import Web3
from flask import current_app
import os
from dotenv import load_dotenv

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
                
                return {
                    'success': True,
                    'transaction_hash': tx.hex(),
                    'file_hash': file_hash
                }
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