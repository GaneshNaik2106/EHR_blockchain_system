from flask import Blueprint, render_template, redirect, url_for, jsonify
from flask_login import current_user
from app.services.blockchain_service import BlockchainService

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('main/home.html')

@main_bp.route('/dashboard')
def dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif current_user.role == 'doctor':
        return redirect(url_for('doctor.dashboard'))
    elif current_user.role == 'patient':
        return redirect(url_for('patient.dashboard'))
    
    return redirect(url_for('main.home'))

@main_bp.route('/blockchain-status')
def blockchain_status():
    """Get blockchain connection status"""
    blockchain_service = BlockchainService()
    
    # Try to connect to blockchain
    connected = blockchain_service.connect_to_ganache()
    
    if connected:
        # Try to load contract
        contract_loaded = blockchain_service.load_contract()
        accounts = blockchain_service.get_accounts()
        
        if accounts:
            blockchain_service.set_account(0)
            balance = blockchain_service.get_balance()
        else:
            balance = 0
            
        status = {
            'connected': True,
            'contract_loaded': contract_loaded,
            'accounts_count': len(accounts),
            'current_account': blockchain_service.account,
            'balance': balance,
            'ganache_url': blockchain_service.web3.provider.endpoint_uri if blockchain_service.web3 else None
        }
    else:
        status = {
            'connected': False,
            'contract_loaded': False,
            'accounts_count': 0,
            'current_account': None,
            'balance': 0,
            'ganache_url': None,
            'error': 'Failed to connect to Ganache'
        }
    
    return jsonify(status)

@main_bp.route('/blockchain')
def blockchain_page():
    """Display blockchain status page"""
    return render_template('main/blockchain_status.html') 