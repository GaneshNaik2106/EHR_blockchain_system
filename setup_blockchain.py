#!/usr/bin/env python3
"""
Script to help set up the blockchain environment for the EHR system
"""

import os
import json
import subprocess
import sys

def check_ganache():
    """Check if Ganache is running"""
    try:
        import requests
        response = requests.get("http://127.0.0.1:7545")
        if response.status_code == 200:
            print("✅ Ganache is running on http://127.0.0.1:7545")
            return True
        else:
            print("❌ Ganache is not responding properly")
            return False
    except:
        print("❌ Ganache is not running")
        return False

def check_truffle():
    """Check if Truffle is installed"""
    try:
        result = subprocess.run(['truffle', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Truffle is installed")
            return True
        else:
            print("❌ Truffle is not installed")
            return False
    except FileNotFoundError:
        print("❌ Truffle is not installed")
        return False

def deploy_contracts():
    """Deploy contracts using Truffle"""
    print("\n🚀 Deploying smart contracts...")
    
    try:
        # Compile contracts
        print("Compiling contracts...")
        result = subprocess.run(['truffle', 'compile'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Compilation failed: {result.stderr}")
            return False
        
        # Migrate contracts
        print("Deploying contracts to Ganache...")
        result = subprocess.run(['truffle', 'migrate', '--network', 'development'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Deployment failed: {result.stderr}")
            return False
        
        print("✅ Contracts deployed successfully!")
        
        # Extract contract address
        try:
            with open('build/contracts/EHRContract.json', 'r') as f:
                contract_data = json.load(f)
                networks = contract_data.get('networks', {})
                if networks:
                    # Get the first network (usually development)
                    network_id = list(networks.keys())[0]
                    contract_address = networks[network_id]['address']
                    print(f"📋 Contract Address: {contract_address}")
                    
                    # Update config.env
                    update_config(contract_address)
                    return True
        except Exception as e:
            print(f"❌ Error extracting contract address: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error during deployment: {e}")
        return False

def update_config(contract_address):
    """Update the config.env file with the contract address"""
    config_file = 'config.env'
    
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            lines = f.readlines()
        
        # Update CONTRACT_ADDRESS
        updated_lines = []
        for line in lines:
            if line.startswith('CONTRACT_ADDRESS='):
                updated_lines.append(f'CONTRACT_ADDRESS={contract_address}\n')
            else:
                updated_lines.append(line)
        
        with open(config_file, 'w') as f:
            f.writelines(updated_lines)
        
        print(f"✅ Updated {config_file} with contract address")
    else:
        print(f"❌ {config_file} not found")

def main():
    print("🔗 EHR Blockchain Setup")
    print("=" * 50)
    
    # Check prerequisites
    print("\n1. Checking prerequisites...")
    ganache_ok = check_ganache()
    truffle_ok = check_truffle()
    
    if not ganache_ok:
        print("\n📋 To start Ganache:")
        print("1. Download Ganache from https://www.trufflesuite.com/ganache")
        print("2. Install and run Ganache")
        print("3. Make sure it's running on http://127.0.0.1:7545")
        print("4. Run this script again")
        return
    
    if not truffle_ok:
        print("\n📋 To install Truffle:")
        print("1. Install Node.js from https://nodejs.org/")
        print("2. Run: npm install -g truffle")
        print("3. Run this script again")
        return
    
    # Deploy contracts
    print("\n2. Deploying smart contracts...")
    if deploy_contracts():
        print("\n✅ Blockchain setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Start your Flask application: python run.py")
        print("2. Visit http://localhost:5002/blockchain to see blockchain status")
        print("3. The blockchain functionality should now be working")
    else:
        print("\n❌ Blockchain setup failed. Please check the errors above.")

if __name__ == '__main__':
    main() 