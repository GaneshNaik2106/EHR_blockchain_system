from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import os
import hashlib
import shutil
from datetime import datetime
from app.services.blockchain_service import BlockchainService
from app.services.file_service import FileService
from app.services.file_tracker import FileTracker

files_bp = Blueprint('files', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calculate_file_hash(file_path):
    """Calculate SHA-256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

@files_bp.route('/upload')
def upload_form():
    return render_template('files/upload.html')

@files_bp.route('/upload', methods=['POST'])
def upload_file():
    print("DEBUG: File upload started")
    
    if 'file' not in request.files:
        print("DEBUG: No file in request")
        flash('No file selected', 'error')
        return redirect(url_for('files.upload_form'))
    
    file = request.files['file']
    if file.filename == '':
        print("DEBUG: No filename")
        flash('No file selected', 'error')
        return redirect(url_for('files.upload_form'))
    
    if file and allowed_file(file.filename):
        print(f"DEBUG: Processing file: {file.filename}")
        
        # Create upload folder if it doesn't exist
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        print(f"DEBUG: File saved to: {filepath}")
        
        # Calculate file hash
        file_hash = calculate_file_hash(filepath)
        print(f"DEBUG: File hash: {file_hash}")
        
        # Try to store on blockchain
        try:
            blockchain_service = BlockchainService()
            result = blockchain_service.upload_file_to_blockchain(
                file_hash=file_hash,
                ipfs_hash="test_ipfs_hash",  # Placeholder
                filename=filename,
                record_type="medical_file"
            )
            print(f"DEBUG: Blockchain result: {result}")
            
            if result.get('success'):
                flash('File uploaded successfully!', 'success')
            else:
                flash(f'File saved but blockchain storage failed: {result.get("error", "Unknown error")}', 'warning')
                
        except Exception as e:
            print(f"DEBUG: Blockchain error: {e}")
            flash(f'File saved but blockchain storage failed: {str(e)}', 'warning')
        
        # Always save to local tracker for display purposes
        try:
            file_tracker = FileTracker()
            tracker_result = file_tracker.add_file(
                file_hash=file_hash,
                filename=filename,
                ipfs_hash="test_ipfs_hash",
                record_type="medical_file"
            )
            if tracker_result:
                print(f"DEBUG: File added to local tracker")
            else:
                print(f"DEBUG: File already exists in local tracker")
        except Exception as e:
            print(f"DEBUG: Error adding to local tracker: {e}")
        
        return redirect(url_for('files.upload_form'))
    
    flash('Invalid file type', 'error')
    return redirect(url_for('files.upload_form'))

@files_bp.route('/files')
def file_list():
    blockchain_service = BlockchainService()
    result = blockchain_service.get_all_files()
    
    if result.get('success'):
        files = result.get('files', [])
    else:
        files = []
        flash(f'Error loading files: {result.get("error", "Unknown error")}', 'error')
    
    return render_template('files/list.html', files=files)

@files_bp.route('/verify')
def verify_page():
    # Get list of uploaded files for selection
    blockchain_service = BlockchainService()
    files_result = blockchain_service.get_all_files()
    
    if files_result.get('success'):
        uploaded_files = files_result.get('files', [])
    else:
        # Use local file tracker as fallback
        file_tracker = FileTracker()
        uploaded_files = file_tracker.get_all_files()
    
    return render_template('files/verify.html', uploaded_files=uploaded_files)

@files_bp.route('/verify', methods=['POST'])
def verify_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file selected'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    # Get the stored hash from the form
    stored_hash = request.form.get('stored_hash', '')
    if not stored_hash:
        return jsonify({'success': False, 'error': 'No stored hash provided'})
    
    if file and allowed_file(file.filename):
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, f"temp_{filename}")
        file.save(temp_path)
        
        # Calculate current hash
        current_hash = calculate_file_hash(temp_path)
        
        # Verify file using the stored hash
        blockchain_service = BlockchainService()
        verification_result = blockchain_service.verify_file(stored_hash, current_hash)
        
        # Add current hash to result for display
        verification_result['current_hash'] = current_hash
        verification_result['stored_hash'] = stored_hash
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return jsonify(verification_result)
    
    return jsonify({'success': False, 'error': 'Invalid file type'})

@files_bp.route('/tamper-demo')
def tamper_demo():
    return render_template('files/tamper_demo.html')

@files_bp.route('/tamper-demo', methods=['POST'])
def create_tampered_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file selected'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    if file and allowed_file(file.filename):
        # Save original file
        filename = secure_filename(file.filename)
        original_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(original_path)
        
        # Calculate original hash
        original_hash = calculate_file_hash(original_path)
        
        # Create tampered version
        tampered_filename = f"tampered_{filename}"
        tampered_path = os.path.join(UPLOAD_FOLDER, tampered_filename)
        
        # Copy file and modify it
        shutil.copy2(original_path, tampered_path)
        
        # Add some content to tamper with the file
        with open(tampered_path, 'a') as f:
            f.write("\n\nTAMPERED CONTENT ADDED FOR DEMONSTRATION\n")
        
        # Calculate tampered hash
        tampered_hash = calculate_file_hash(tampered_path)
        
        # Upload original to blockchain
        blockchain_service = BlockchainService()
        upload_result = blockchain_service.upload_file_to_blockchain(
            file_hash=original_hash,
            ipfs_hash="test_ipfs_hash",
            filename=filename,
            record_type="medical_file"
        )
        
        # Also save to local tracker
        try:
            file_tracker = FileTracker()
            file_tracker.add_file(
                file_hash=original_hash,
                filename=filename,
                ipfs_hash="test_ipfs_hash",
                record_type="medical_file"
            )
        except Exception as e:
            print(f"DEBUG: Error adding to local tracker in tamper demo: {e}")
        
        if upload_result.get('success'):
            # Test verification with original file
            original_verification = blockchain_service.verify_file(original_hash, original_hash)
            
            # Test verification with tampered file
            tampered_verification = blockchain_service.verify_file(original_hash, tampered_hash)
            
            # Detect tampering
            tampering_detection = blockchain_service.detect_tampering(original_hash, tampered_hash)
            
            return jsonify({
                'success': True,
                'original_file': {
                    'filename': filename,
                    'hash': original_hash,
                    'verification': original_verification
                },
                'tampered_file': {
                    'filename': tampered_filename,
                    'hash': tampered_hash,
                    'verification': tampered_verification
                },
                'tampering_detection': tampering_detection
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to upload original file to blockchain'})
    
    return jsonify({'success': False, 'error': 'Invalid file type'})

@files_bp.route('/file/<file_hash>')
def file_details(file_hash):
    blockchain_service = BlockchainService()
    
    # Get file info from blockchain or local tracker
    if blockchain_service.is_connected and blockchain_service.contract:
        file_info = blockchain_service.get_file_info(file_hash)
        audit_trail = blockchain_service.get_audit_trail(file_hash)
    else:
        # Use local file tracker
        file_tracker = FileTracker()
        file_data = file_tracker.get_file_info(file_hash)
        
        if file_data:
            file_info = {
                'success': True,
                'filename': file_data['filename'],
                'ipfs_hash': file_data['ipfs_hash'],
                'upload_time': file_data['upload_time'],
                'uploaded_by': 'Local Storage',
                'is_valid': file_data['is_valid'],
                'record_type': file_data['record_type'],
                'verification_count': file_data['verification_count'],
                'last_verified': file_data['last_verified'],
                'original_hash': file_data['file_hash']
            }
            audit_trail = {
                'success': True,
                'audit_entries': [
                    {
                        'timestamp': file_data['upload_time'],
                        'actor': 'Local Storage',
                        'action': 'UPLOAD',
                        'details': 'File uploaded to local storage',
                        'success': True
                    }
                ]
            }
        else:
            flash('File not found', 'error')
            return redirect(url_for('files.file_list'))
    
    return render_template('files/details.html', 
                         file_info=file_info, 
                         audit_trail=audit_trail)

@files_bp.route('/audit-trail/<file_hash>')
def audit_trail(file_hash):
    blockchain_service = BlockchainService()
    
    if blockchain_service.is_connected and blockchain_service.contract:
        result = blockchain_service.get_audit_trail(file_hash, limit=50)
    else:
        # Use local file tracker
        file_tracker = FileTracker()
        file_data = file_tracker.get_file_info(file_hash)
        
        if file_data:
            result = {
                'success': True,
                'audit_entries': [
                    {
                        'timestamp': file_data['upload_time'],
                        'actor': 'Local Storage',
                        'action': 'UPLOAD',
                        'details': 'File uploaded to local storage',
                        'success': True
                    }
                ]
            }
        else:
            result = {'success': False, 'error': 'File not found'}
    
    if result.get('success'):
        return render_template('files/audit_trail.html', 
                             file_hash=file_hash,
                             audit_entries=result.get('audit_entries', []))
    else:
        flash(f'Error loading audit trail: {result.get("error", "Unknown error")}', 'error')
        return redirect(url_for('files.file_list'))

@files_bp.route('/statistics')
def statistics():
    blockchain_service = BlockchainService()
    stats = blockchain_service.get_file_statistics()
    
    if stats.get('success'):
        return render_template('files/statistics.html', statistics=stats)
    else:
        flash(f'Error loading statistics: {stats.get("error", "Unknown error")}', 'error')
        return redirect(url_for('files.file_list'))

@files_bp.route('/invalidate/<file_hash>', methods=['POST'])
def invalidate_file(file_hash):
    blockchain_service = BlockchainService()
    result = blockchain_service.invalidate_file(file_hash)
    
    if result.get('success'):
        flash('File invalidated successfully', 'success')
    else:
        flash(f'Error invalidating file: {result.get("error", "Unknown error")}', 'error')
    
    return redirect(url_for('files.file_details', file_hash=file_hash))

@files_bp.route('/api/verify', methods=['POST'])
def api_verify_file():
    """API endpoint for file verification"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'})
    
    file = request.files['file']
    file_hash = request.form.get('file_hash', '')
    
    if not file_hash:
        return jsonify({'success': False, 'error': 'File hash not provided'})
    
    # Save file temporarily
    temp_path = os.path.join(UPLOAD_FOLDER, f"temp_verify_{file.filename}")
    file.save(temp_path)
    
    # Calculate current hash
    current_hash = calculate_file_hash(temp_path)
    
    # Verify file
    blockchain_service = BlockchainService()
    result = blockchain_service.verify_file(file_hash, current_hash)
    
    # Clean up
    if os.path.exists(temp_path):
        os.remove(temp_path)
    
    return jsonify(result)

@files_bp.route('/api/detect-tampering', methods=['POST'])
def api_detect_tampering():
    """API endpoint for tampering detection"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'})
    
    file = request.files['file']
    file_hash = request.form.get('file_hash', '')
    
    if not file_hash:
        return jsonify({'success': False, 'error': 'File hash not provided'})
    
    # Save file temporarily
    temp_path = os.path.join(UPLOAD_FOLDER, f"temp_tamper_{file.filename}")
    file.save(temp_path)
    
    # Calculate current hash
    current_hash = calculate_file_hash(temp_path)
    
    # Detect tampering
    blockchain_service = BlockchainService()
    result = blockchain_service.detect_tampering(file_hash, current_hash)
    
    # Clean up
    if os.path.exists(temp_path):
        os.remove(temp_path)
    
    return jsonify(result) 