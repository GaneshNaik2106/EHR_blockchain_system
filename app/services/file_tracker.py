import json
import os
from datetime import datetime

class FileTracker:
    def __init__(self, storage_file='uploaded_files.json'):
        self.storage_file = storage_file
        self.files = self.load_files()
    
    def load_files(self):
        """Load files from storage"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def save_files(self):
        """Save files to storage"""
        with open(self.storage_file, 'w') as f:
            json.dump(self.files, f, indent=2)
    
    def add_file(self, file_hash, filename, ipfs_hash="", record_type="medical_file"):
        """Add a new file to tracking"""
        file_info = {
            'file_hash': file_hash,
            'filename': filename,
            'ipfs_hash': ipfs_hash,
            'record_type': record_type,
            'upload_time': int(datetime.now().timestamp()),
            'is_valid': True,
            'verification_count': 0,
            'last_verified': 0
        }
        
        # Check if file already exists
        for existing_file in self.files:
            if existing_file['file_hash'] == file_hash:
                return False  # File already exists
        
        self.files.append(file_info)
        self.save_files()
        return True
    
    def get_all_files(self):
        """Get all tracked files"""
        return self.files
    
    def get_file_info(self, file_hash):
        """Get info for a specific file"""
        for file_info in self.files:
            if file_info['file_hash'] == file_hash:
                return file_info
        return None
    
    def update_verification_count(self, file_hash):
        """Update verification count for a file"""
        for file_info in self.files:
            if file_info['file_hash'] == file_hash:
                file_info['verification_count'] += 1
                file_info['last_verified'] = int(datetime.now().timestamp())
                self.save_files()
                return True
        return False
    
    def invalidate_file(self, file_hash):
        """Mark a file as invalid"""
        for file_info in self.files:
            if file_info['file_hash'] == file_hash:
                file_info['is_valid'] = False
                self.save_files()
                return True
        return False
    
    def get_statistics(self):
        """Get file statistics"""
        total_files = len(self.files)
        valid_files = sum(1 for f in self.files if f['is_valid'])
        invalid_files = total_files - valid_files
        
        return {
            'total_files': total_files,
            'valid_files': valid_files,
            'invalid_files': invalid_files
        } 