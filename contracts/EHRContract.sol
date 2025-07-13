// SPDX-License-Identifier: MIT
pragma solidity >=0.4.21;

import "./Roles.sol";

contract EHRContract {
    using Roles for Roles.Role;

    Roles.Role private admin;
    Roles.Role private doctor;
    Roles.Role private patient;

    struct Doctor {
        address id;
        string drHash;
        string specialization;
        string licenseNumber;
    }

    struct Patient {
        address id;
        string patientHash;
        string medicalHistory;
    }

    struct MedicalRecord {
        uint256 recordId;
        address patientId;
        address doctorId;
        string recordHash;
        string ipfsHash;
        uint256 timestamp;
        bool isValid;
    }

    mapping(address => Doctor) public doctors;
    mapping(address => Patient) public patients;
    mapping(uint256 => MedicalRecord) public medicalRecords;
    mapping(address => uint256[]) public patientRecords;

    address[] public doctorIds;
    address[] public patientIds;
    uint256 public recordCounter;

    event DoctorAdded(address indexed doctorId, string drHash);
    event PatientAdded(address indexed patientId, string patientHash);
    event RecordAdded(uint256 indexed recordId, address indexed patientId, address indexed doctorId);
    event RecordUpdated(uint256 indexed recordId);

    constructor() {
        admin.add(msg.sender);
    }

    // Admin functions
    function isAdmin() public view returns (bool) {
        return admin.has(msg.sender);
    }

    function addAdmin(address newAdmin) public {
        require(admin.has(msg.sender), "Only admin can add new admin");
        admin.add(newAdmin);
    }

    // Doctor functions
    function addDoctor(address drId, string memory _drHash, string memory _specialization, string memory _licenseNumber) public {
        require(admin.has(msg.sender), "Only admin can add doctors");

        Doctor storage drInfo = doctors[drId];
        drInfo.id = drId;
        drInfo.drHash = _drHash;
        drInfo.specialization = _specialization;
        drInfo.licenseNumber = _licenseNumber;
        
        doctorIds.push(drId);
        doctor.add(drId);

        emit DoctorAdded(drId, _drHash);
    }

    function getAllDoctors() public view returns (address[] memory) {
        return doctorIds;
    }

    function getDoctor(address _id) public view returns (string memory, string memory, string memory) {
        Doctor storage dr = doctors[_id];
        return (dr.drHash, dr.specialization, dr.licenseNumber);
    }

    function isDoctor(address id) public view returns (bool) {
        return doctor.has(id);
    }

    // Patient functions
    function addPatient(address patientId, string memory _patientHash, string memory _medicalHistory) public {
        require(admin.has(msg.sender) || doctor.has(msg.sender), "Only admin or doctor can add patients");

        Patient storage patientInfo = patients[patientId];
        patientInfo.id = patientId;
        patientInfo.patientHash = _patientHash;
        patientInfo.medicalHistory = _medicalHistory;
        
        patientIds.push(patientId);
        patient.add(patientId);
    }

    function getAllPatients() public view returns (address[] memory) {
        return patientIds;
    }

    function getPatient(address _id) public view returns (string memory, string memory) {
        Patient storage p = patients[_id];
        return (p.patientHash, p.medicalHistory);
    }

    function isPatient(address id) public view returns (bool) {
        return patient.has(id);
    }

    // Medical Record functions
    function addMedicalRecord(address _patientId, address _doctorId, string memory _recordHash, string memory _ipfsHash) public {
        require(doctor.has(msg.sender), "Only doctors can add medical records");
        require(patient.has(_patientId), "Patient must be registered");

        recordCounter++;
        
        MedicalRecord storage record = medicalRecords[recordCounter];
        record.recordId = recordCounter;
        record.patientId = _patientId;
        record.doctorId = _doctorId;
        record.recordHash = _recordHash;
        record.ipfsHash = _ipfsHash;
        record.timestamp = block.timestamp;
        record.isValid = true;

        patientRecords[_patientId].push(recordCounter);

        emit RecordAdded(recordCounter, _patientId, _doctorId);
    }

    function getMedicalRecord(uint256 _recordId) public view returns (
        address patientId,
        address doctorId,
        string memory recordHash,
        string memory ipfsHash,
        uint256 timestamp,
        bool isValid
    ) {
        MedicalRecord storage record = medicalRecords[_recordId];
        return (
            record.patientId,
            record.doctorId,
            record.recordHash,
            record.ipfsHash,
            record.timestamp,
            record.isValid
        );
    }

    function getPatientRecords(address _patientId) public view returns (uint256[] memory) {
        return patientRecords[_patientId];
    }

    function updateMedicalRecord(uint256 _recordId, string memory _newRecordHash, string memory _newIpfsHash) public {
        require(doctor.has(msg.sender), "Only doctors can update medical records");
        
        MedicalRecord storage record = medicalRecords[_recordId];
        require(record.isValid, "Record does not exist or is invalid");
        require(record.doctorId == msg.sender, "Only the original doctor can update the record");

        record.recordHash = _newRecordHash;
        record.ipfsHash = _newIpfsHash;
        record.timestamp = block.timestamp;

        emit RecordUpdated(_recordId);
    }

    function invalidateRecord(uint256 _recordId) public {
        require(admin.has(msg.sender), "Only admin can invalidate records");
        
        MedicalRecord storage record = medicalRecords[_recordId];
        require(record.isValid, "Record is already invalid");

        record.isValid = false;
    }

    // Enhanced File management functions with verification and audit trail
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
        string originalHash; // Store original hash for tamper detection
    }

    struct AuditEntry {
        uint256 timestamp;
        address actor;
        string action;
        string details;
        bool success;
    }

    mapping(string => FileRecord) public fileRecords;
    mapping(address => string[]) public userFiles;
    mapping(string => AuditEntry[]) public fileAuditTrail;
    string[] public allFileHashes;

    event FileUploaded(string indexed fileHash, address indexed uploadedBy, string filename);
    event FileVerified(string indexed fileHash, bool isValid, address indexed verifiedBy);
    event FileTampered(string indexed fileHash, address indexed detectedBy, string originalHash, string currentHash);
    event FileInvalidated(string indexed fileHash, address indexed invalidatedBy);
    event AuditLogCreated(string indexed fileHash, address indexed actor, string action);

    function uploadFile(string memory _fileHash, string memory _ipfsHash, string memory _filename, string memory _recordType) public {
        require(bytes(_fileHash).length > 0, "File hash cannot be empty");
        require(bytes(_ipfsHash).length > 0, "IPFS hash cannot be empty");
        require(bytes(_filename).length > 0, "Filename cannot be empty");
        
        FileRecord storage file = fileRecords[_fileHash];
        file.fileHash = _fileHash;
        file.originalHash = _fileHash; // Store original hash
        file.ipfsHash = _ipfsHash;
        file.filename = _filename;
        file.uploadTime = block.timestamp;
        file.uploadedBy = msg.sender;
        file.isValid = true;
        file.recordType = _recordType;
        file.verificationCount = 0;
        file.lastVerified = 0;
        
        userFiles[msg.sender].push(_fileHash);
        allFileHashes.push(_fileHash);
        
        // Add audit entry
        addAuditEntry(_fileHash, msg.sender, "UPLOAD", "File uploaded successfully", true);
        
        emit FileUploaded(_fileHash, msg.sender, _filename);
    }

    function verifyFile(string memory _fileHash, string memory _currentHash) public view returns (bool) {
        FileRecord storage file = fileRecords[_fileHash];
        require(bytes(file.fileHash).length > 0, "File not found");
        
        return keccak256(abi.encodePacked(_currentHash)) == keccak256(abi.encodePacked(file.fileHash));
    }

    function verifyFileAndLog(string memory _fileHash, string memory _currentHash) public returns (bool) {
        FileRecord storage file = fileRecords[_fileHash];
        require(bytes(file.fileHash).length > 0, "File not found");
        
        bool isValid = keccak256(abi.encodePacked(_currentHash)) == keccak256(abi.encodePacked(file.fileHash));
        
        if (isValid) {
            file.verificationCount++;
            file.lastVerified = block.timestamp;
            addAuditEntry(_fileHash, msg.sender, "VERIFY", "File verification successful", true);
        } else {
            addAuditEntry(_fileHash, msg.sender, "VERIFY", "File verification failed - possible tampering detected", false);
            emit FileTampered(_fileHash, msg.sender, file.originalHash, _currentHash);
        }
        
        emit FileVerified(_fileHash, isValid, msg.sender);
        return isValid;
    }

    function detectTampering(string memory _fileHash, string memory _currentHash) public view returns (bool, string memory, string memory) {
        FileRecord storage file = fileRecords[_fileHash];
        require(bytes(file.fileHash).length > 0, "File not found");
        
        bool isTampered = keccak256(abi.encodePacked(_currentHash)) != keccak256(abi.encodePacked(file.fileHash));
        return (isTampered, file.originalHash, _currentHash);
    }

    function getFileInfo(string memory _fileHash) public view returns (
        string memory filename,
        string memory ipfsHash,
        uint256 uploadTime,
        address uploadedBy,
        bool isValid,
        string memory recordType,
        uint256 verificationCount,
        uint256 lastVerified,
        string memory originalHash
    ) {
        FileRecord storage file = fileRecords[_fileHash];
        return (
            file.filename,
            file.ipfsHash,
            file.uploadTime,
            file.uploadedBy,
            file.isValid,
            file.recordType,
            file.verificationCount,
            file.lastVerified,
            file.originalHash
        );
    }

    function getUserFiles(address _user) public view returns (string[] memory) {
        return userFiles[_user];
    }

    function getAllFiles() public view returns (string[] memory) {
        return allFileHashes;
    }

    function getFileAuditTrail(string memory _fileHash) public view returns (AuditEntry[] memory) {
        return fileAuditTrail[_fileHash];
    }

    function addAuditEntry(string memory _fileHash, address _actor, string memory _action, string memory _details, bool _success) private {
        AuditEntry memory entry = AuditEntry({
            timestamp: block.timestamp,
            actor: _actor,
            action: _action,
            details: _details,
            success: _success
        });
        
        fileAuditTrail[_fileHash].push(entry);
        emit AuditLogCreated(_fileHash, _actor, _action);
    }

    function invalidateFile(string memory _fileHash) public {
        require(admin.has(msg.sender), "Only admin can invalidate files");
        
        FileRecord storage file = fileRecords[_fileHash];
        require(file.isValid, "File is already invalid");
        
        file.isValid = false;
        addAuditEntry(_fileHash, msg.sender, "INVALIDATE", "File invalidated by admin", true);
        
        emit FileInvalidated(_fileHash, msg.sender);
    }

    function getFileStatistics() public view returns (uint256 totalFiles, uint256 validFiles, uint256 invalidFiles) {
        totalFiles = allFileHashes.length;
        validFiles = 0;
        invalidFiles = 0;
        
        for (uint256 i = 0; i < allFileHashes.length; i++) {
            if (fileRecords[allFileHashes[i]].isValid) {
                validFiles++;
            } else {
                invalidFiles++;
            }
        }
    }

    function getRecentAuditEntries(string memory _fileHash, uint256 _limit) public view returns (AuditEntry[] memory) {
        AuditEntry[] storage allEntries = fileAuditTrail[_fileHash];
        uint256 entryCount = allEntries.length;
        
        if (_limit > entryCount) {
            _limit = entryCount;
        }
        
        AuditEntry[] memory recentEntries = new AuditEntry[](_limit);
        
        for (uint256 i = 0; i < _limit; i++) {
            recentEntries[i] = allEntries[entryCount - _limit + i];
        }
        
        return recentEntries;
    }
} 