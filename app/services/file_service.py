import hashlib
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from app.services.blockchain_service import BlockchainService
from app.services.ipfs_service import IPFSService
import logging

class FileService:
    def __init__(self):
        self.blockchain_service = BlockchainService()
        self.ipfs_service = IPFSService()
        self.upload_folder = 'uploads'
        
        # Create upload directory if it doesn't exist
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
    
    def calculate_file_hash(self, file_path):
        """Calculate SHA-256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def calculate_data_hash(self, data):
        """Calculate SHA-256 hash of data"""
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True)
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha256(data).hexdigest()
    
    def save_file(self, file):
        """Save uploaded file and return file info"""
        if file and file.filename:
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
            file_path = os.path.join(self.upload_folder, filename)
            
            print(f"DEBUG: Saving file to: {file_path}")
            file.save(file_path)
            
            # Calculate file hash
            file_hash = self.calculate_file_hash(file_path)
            print(f"DEBUG: Calculated file hash: {file_hash}")
            
            # Upload to IPFS
            print(f"DEBUG: Uploading to IPFS...")
            ipfs_hash = self.ipfs_service.upload_file(file_path)
            print(f"DEBUG: IPFS hash: {ipfs_hash}")
            
            if not ipfs_hash:
                print(f"DEBUG: IPFS upload failed, using mock hash")
                ipfs_hash = "QmMockHash123456789"
            
            return {
                'filename': filename,
                'original_filename': file.filename,
                'file_path': file_path,
                'file_hash': file_hash,
                'ipfs_hash': ipfs_hash,
                'file_size': os.path.getsize(file_path),
                'upload_time': datetime.now().isoformat()
            }
        return None
    
    def store_file_on_blockchain(self, file_info, record_type="medical_file"):
        """Store file hash on blockchain"""
        try:
            print(f"DEBUG: File service - Starting blockchain upload")
            print(f"DEBUG: File info: {file_info}")
            print(f"DEBUG: Record type: {record_type}")
            
            # Connect to blockchain
            self.blockchain_service.connect_to_ganache()
            self.blockchain_service.load_contract()
            
            # Store file info on blockchain
            logger = logging.getLogger(__name__)
            
            logger.info("=" * 30)
            logger.info("DEBUG: File service - Starting blockchain upload")
            logger.info("=" * 30)
            logger.info(f"DEBUG: File service - About to call blockchain service")
            logger.info(f"DEBUG: File service - file_hash: '{file_info['file_hash']}'")
            logger.info(f"DEBUG: File service - ipfs_hash: '{file_info['ipfs_hash']}'")
            logger.info(f"DEBUG: File service - filename: '{file_info['filename']}'")
            logger.info(f"DEBUG: File service - record_type: '{record_type}'")
            logger.info(f"DEBUG: File service - file_hash type: {type(file_info['file_hash'])}")
            logger.info(f"DEBUG: File service - ipfs_hash type: {type(file_info['ipfs_hash'])}")
            logger.info(f"DEBUG: File service - filename type: {type(file_info['filename'])}")
            logger.info(f"DEBUG: File service - record_type type: {type(record_type)}")
            logger.info(f"DEBUG: File service - file_hash length: {len(file_info['file_hash']) if file_info['file_hash'] else 0}")
            logger.info(f"DEBUG: File service - ipfs_hash length: {len(file_info['ipfs_hash']) if file_info['ipfs_hash'] else 0}")
            logger.info(f"DEBUG: File service - filename length: {len(file_info['filename']) if file_info['filename'] else 0}")
            logger.info(f"DEBUG: File service - record_type length: {len(record_type) if record_type else 0}")
            logger.info("=" * 30)
            
            blockchain_result = self.blockchain_service.upload_file_to_blockchain(
                file_info['file_hash'],
                file_info['ipfs_hash'],
                file_info['filename'],
                record_type
            )
            
            print(f"DEBUG: Blockchain result: {blockchain_result}")
            
            if blockchain_result['success']:
                return {
                    'success': True,
                    'file_hash': file_info['file_hash'],
                    'transaction_hash': blockchain_result.get('transaction_hash'),
                    'metadata': {
                        'filename': file_info['original_filename'],
                        'file_hash': file_info['file_hash'],
                        'ipfs_hash': file_info['ipfs_hash'],
                        'record_type': record_type,
                        'upload_time': file_info['upload_time'],
                        'file_size': file_info['file_size']
                    }
                }
            else:
                return {
                    'success': False,
                    'error': blockchain_result.get('error', 'Unknown blockchain error')
                }
        except Exception as e:
            print(f"DEBUG: File service exception: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_file_integrity(self, file_path, stored_hash):
        """Verify if a file has been tampered with"""
        try:
            current_hash = self.calculate_file_hash(file_path)
            is_valid = current_hash == stored_hash
            
            return {
                'is_valid': is_valid,
                'current_hash': current_hash,
                'stored_hash': stored_hash,
                'tampered': not is_valid
            }
        except Exception as e:
            return {
                'is_valid': False,
                'error': str(e)
            }
    
    def get_file_audit_trail(self, file_hash):
        """Get blockchain audit trail for a file"""
        try:
            # This would query the blockchain for file history
            # For now, return mock data
            return {
                'file_hash': file_hash,
                'upload_time': datetime.now().isoformat(),
                'blockchain_blocks': [
                    {
                        'block_number': 12345,
                        'timestamp': datetime.now().isoformat(),
                        'transaction_hash': '0x' + '0' * 64,
                        'action': 'file_uploaded'
                    }
                ],
                'verification_history': [
                    {
                        'timestamp': datetime.now().isoformat(),
                        'verified': True,
                        'verifier': 'system'
                    }
                ]
            }
        except Exception as e:
            return {
                'error': str(e)
            }
    
    def create_tampered_file_demo(self, original_file_path):
        """Create a demo of file tampering for testing"""
        try:
            # Read original file
            with open(original_file_path, 'r') as f:
                content = f.read()
            
            # Create tampered version
            tampered_content = content + "\n# TAMPERED: This line was added maliciously\n"
            tampered_file_path = original_file_path.replace('.', '_tampered.')
            
            with open(tampered_file_path, 'w') as f:
                f.write(tampered_content)
            
            # Calculate hashes
            original_hash = self.calculate_file_hash(original_file_path)
            tampered_hash = self.calculate_file_hash(tampered_file_path)
            
            return {
                'original_file': original_file_path,
                'tampered_file': tampered_file_path,
                'original_hash': original_hash,
                'tampered_hash': tampered_hash,
                'hashes_match': original_hash == tampered_hash
            }
        except Exception as e:
            return {
                'error': str(e)
            } 