from app.services.blockchain_service import BlockchainService

def test_blockchain():
    service = BlockchainService()
    print("Connected:", service.is_connected)
    accounts = service.get_accounts()
    print("Accounts:", accounts)
    if service.contract:
        try:
            doctors = service.get_all_doctors()
            print("Doctors from blockchain:", doctors)
        except Exception as e:
            print("Error calling contract:", e)
    else:
        print("Contract not loaded.")

if __name__ == "__main__":
    test_blockchain()