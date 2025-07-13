# EHR Blockchain System

A comprehensive, secure Electronic Health Record (EHR) system built with Flask and Ethereum blockchain technology. This system provides decentralized storage, file integrity verification, tamper detection, and comprehensive audit trails for medical records.

## 🚀 Features

### Core EHR Features
- **Role-Based Access Control**: Admin, Doctor, and Patient roles with appropriate permissions
- **Medical Records Management**: Create, view, and manage patient medical records
- **Consultation Booking**: Patients can book consultations with doctors
- **User Management**: Admin can manage doctors and patients
- **Profile Management**: Users can update their personal information

### Blockchain & Security Features
- **Ethereum Blockchain Integration**: Medical records stored on Ethereum for immutability
- **IPFS Integration**: Large files and documents stored on IPFS for decentralized storage
- **SHA-256 File Hashing**: Cryptographic hashing for data integrity
- **File Integrity Verification**: Real-time verification of uploaded files
- **Tamper Detection System**: Automatic detection of file modifications
- **Comprehensive Audit Trail**: Complete logging of all operations on blockchain
- **File Statistics & Metrics**: Dashboard with system health indicators

### Technical Features
- **Smart Contract Automation**: Automated file hash calculation and storage
- **Real-time Blockchain Status**: Monitor blockchain connection status
- **Modern UI/UX**: Beautiful, responsive interface built with Bootstrap 5
- **Secure Authentication**: Flask-Login with password hashing
- **Database Migration**: Alembic for database schema management

## 🛠 Technology Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLAlchemy with SQLite (configurable for PostgreSQL/MySQL)
- **Authentication**: Flask-Login
- **Database Migration**: Flask-Migrate (Alembic)

### Blockchain & Storage
- **Blockchain**: Ethereum (Ganache for development)
- **Smart Contracts**: Solidity
- **Storage**: IPFS for decentralized file storage
- **Web3**: Python Web3 library for blockchain interaction

### Frontend
- **HTML5/CSS3/JavaScript**
- **Bootstrap 5**: Responsive UI framework
- **Chart.js**: Data visualization

### Development Tools
- **Truffle**: Smart contract development framework
- **Ganache**: Local Ethereum blockchain
- **IPFS Kubo**: IPFS implementation

## 📋 Prerequisites

1. **Python 3.8+**
2. **Node.js 14+** (for Truffle and Ganache)
3. **Ganache** (local Ethereum blockchain)
4. **IPFS Kubo** (for decentralized file storage)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd EHR_Blockchain_system
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Set Up Node.js Dependencies

```bash
# Install Node.js dependencies
npm install

# Install Truffle globally (if not already installed)
npm install -g truffle
```

### 4. Set Up Ganache

1. Download and install [Ganache](https://www.trufflesuite.com/ganache)
2. Start Ganache and create a new workspace
3. Note the RPC URL (usually `http://127.0.0.1:7545`)

### 5. Set Up IPFS

1. Download and install [IPFS Kubo](https://dist.ipfs.tech/#go-ipfs)
2. Initialize IPFS: `ipfs init`
3. Start IPFS daemon: `ipfs daemon`
4. IPFS will be available at `http://127.0.0.1:5001`

### 6. Deploy Smart Contracts

```bash
# Compile smart contracts
npm run compile

# Deploy to local blockchain
npm run migrate
```

Note the deployed contract address and update it in the configuration.

### 7. Configure Environment

Create a `.env` file in the root directory:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///ehr.db
GANACHE_URL=http://127.0.0.1:7545
IPFS_URL=http://127.0.0.1:5001
CONTRACT_ADDRESS=your-deployed-contract-address
```

### 8. Initialize Database

```bash
# Initialize database and create admin user
flask init-db
```

This creates an admin user with:
- Email: `admin@ehr.com`
- Password: `admin123`

### 9. Run the Application

```bash
python run.py
```

The application will be available at `http://localhost:5002`

## 📁 Project Structure

```
EHR_Blockchain_system/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models/                  # Database models
│   │   ├── user.py             # User model
│   │   ├── doctor.py           # Doctor model
│   │   ├── patient.py          # Patient model
│   │   ├── record.py           # Medical record model
│   │   └── consultation.py     # Consultation model
│   ├── routes/                  # Flask routes
│   │   ├── main.py             # Main routes
│   │   ├── auth.py             # Authentication routes
│   │   ├── admin.py            # Admin routes
│   │   ├── doctor.py           # Doctor routes
│   │   ├── patient.py          # Patient routes
│   │   └── files.py            # File management routes
│   ├── services/                # Business logic
│   │   ├── blockchain_service.py    # Blockchain interaction
│   │   ├── ipfs_service.py          # IPFS interaction
│   │   └── file_service.py          # File handling
│   ├── static/                  # Static files
│   │   ├── css/style.css       # Stylesheets
│   │   └── js/main.js          # JavaScript
│   └── templates/               # HTML templates
│       ├── base.html           # Base template
│       ├── auth/               # Authentication templates
│       ├── admin/              # Admin templates
│       ├── doctor/             # Doctor templates
│       ├── patient/            # Patient templates
│       └── files/              # File management templates
├── contracts/                   # Smart contracts
│   ├── EHRContract.sol         # Main EHR contract
│   ├── Roles.sol               # Role management
│   └── Migrations.sol          # Migration contract
├── migrations/                  # Database migrations
├── uploads/                     # File upload directory
├── requirements.txt             # Python dependencies
├── package.json                 # Node.js dependencies
├── truffle-config.js           # Truffle configuration
└── run.py                      # Application entry point
```

## 🔧 Smart Contracts

### EHRContract.sol

The main smart contract providing:

#### Core Functions
- **Doctor Management**: Add, retrieve, and verify doctors
- **Patient Management**: Add, retrieve, and verify patients
- **Medical Records**: Store and manage medical records with IPFS integration

#### Enhanced File Management
- **File Upload**: Store file hashes and metadata on blockchain
- **File Verification**: Verify file integrity using SHA-256 hashing
- **Tamper Detection**: Detect unauthorized file modifications
- **Audit Trail**: Complete logging of all file operations
- **File Statistics**: System-wide file metrics and health indicators

#### Key Structures
```solidity
struct FileRecord {
    string fileHash;
    string ipfsHash;
    string filename;
    uint256 uploadTime;
    address uploadedBy;
    bool isValid;
    string recordType;
    uint256 verificationCount;
    uint256 lastVerified;
    string originalHash;
}

struct AuditEntry {
    uint256 timestamp;
    address actor;
    string action;
    string details;
    bool success;
}
```

### Roles.sol

Library for managing role-based access control with admin, doctor, and patient roles.

## 🎯 Usage

### Admin Features

- **Dashboard**: Overview of doctors, patients, and system statistics
- **Doctor Management**: Add and manage doctor accounts
- **Patient Management**: View and manage patient information
- **File Management**: Monitor file uploads, verifications, and audit trails
- **System Administration**: Monitor blockchain status and system health

### Doctor Features

- **Dashboard**: Overview of consultations and patients
- **Patient Management**: View and manage patient records
- **Medical Records**: Create and update medical records with blockchain storage
- **File Upload**: Upload medical files with automatic hashing and verification
- **Consultations**: Manage patient consultations and schedules

### Patient Features

- **Dashboard**: Overview of medical records and consultations
- **Medical Records**: View personal medical records stored on blockchain
- **File Verification**: Verify integrity of uploaded medical files
- **Consultations**: Book and manage consultations with doctors
- **Profile Management**: Update personal information

## 🔒 Security Features

### Authentication & Authorization
- **Password Hashing**: Secure password storage using Werkzeug
- **Session Management**: Flask-Login for secure sessions
- **Role-Based Access**: Different permissions for admin, doctor, and patient roles

### Data Integrity
- **Blockchain Immutability**: Medical records stored on Ethereum blockchain
- **SHA-256 Hashing**: Cryptographic hashing for file integrity
- **IPFS Security**: Decentralized file storage with content addressing
- **Tamper Detection**: Automatic detection of file modifications

### Audit & Compliance
- **Complete Audit Trail**: All operations logged on blockchain
- **File Verification**: Real-time integrity verification
- **Access Logging**: Track all file access and modifications

## 🧪 Testing

### Run Test Suite

```bash
# Test enhanced features
python test_enhanced_features.py

# Test blockchain service
python test_blockchain_service.py

# Test authentication
python test_auth.py
```

### Test Smart Contracts

```bash
# Run Truffle tests
npm test
```

## 🚀 Deployment

### Development

```bash
python run.py
```

### Production Setup

1. **WSGI Server**: Use Gunicorn or uWSGI
2. **Database**: Configure PostgreSQL or MySQL
3. **Environment Variables**: Set production environment variables
4. **Reverse Proxy**: Set up Nginx as reverse proxy
5. **SSL Certificate**: Configure HTTPS
6. **Blockchain Network**: Deploy to Ethereum mainnet or testnet

### Environment Configuration

```env
# Production environment variables
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:password@localhost/ehr_db
GANACHE_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
IPFS_URL=https://ipfs.infura.io:5001
CONTRACT_ADDRESS=your-deployed-contract-address
FLASK_ENV=production
```

## 📊 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/logout` - User logout

### Admin Routes
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/doctors` - List all doctors
- `POST /admin/add-doctor` - Add new doctor
- `GET /admin/patients` - List all patients

### Doctor Routes
- `GET /doctor/dashboard` - Doctor dashboard
- `GET /doctor/patients` - List patients
- `GET /doctor/patient/<id>` - View patient details
- `POST /doctor/add-record/<patient_id>` - Add medical record
- `GET /doctor/consultations` - List consultations

### Patient Routes
- `GET /patient/dashboard` - Patient dashboard
- `GET /patient/records` - List medical records
- `GET /patient/record/<id>` - View medical record
- `GET /patient/consultations` - List consultations
- `POST /patient/book-consultation` - Book consultation

### File Management Routes
- `GET /files/list` - List all files
- `POST /files/upload` - Upload file
- `POST /files/verify` - Verify file integrity
- `GET /files/statistics` - File statistics
- `GET /files/audit-trail/<file_hash>` - File audit trail
- `POST /files/tamper-demo` - Tamper detection demo

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation in the `/docs` folder
- Review the test files for usage examples

## 🔄 Version History

- **v1.0.0**: Initial release with basic EHR functionality
- **v1.1.0**: Added blockchain integration and IPFS storage
- **v1.2.0**: Enhanced file management with verification and audit trails
- **v1.3.0**: Added tamper detection and comprehensive statistics

---

**Note**: This system is designed for educational and development purposes. For production use in healthcare environments, ensure compliance with relevant healthcare regulations and security standards.
