// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title KavachaTrustRegistry
 * @notice Immutable ZK proof audit trail on Polygon.
 * Stores ONLY proof hashes — never voice, video, or biometric data.
 */
contract KavachaTrustRegistry {

    struct VerificationEvent {
        bytes32 proofHash;
        bytes32 txPayloadHash;
        uint256 timestamp;
        bool verified;
        string ipfsCid;
    }

    mapping(address => VerificationEvent[]) public auditTrail;
    mapping(address => bytes32) public biometricCommitments;
    mapping(address => bool) public isRegistered;

    uint256 public totalVerifications;
    uint256 public totalFraudAttempts;

    event IdentityVerified(address indexed user, bytes32 indexed proofHash, uint256 timestamp);
    event FraudAttemptLogged(address indexed attacker, uint256 timestamp, string reason);
    event CommitmentRegistered(address indexed user, bytes32 commitment);

    function registerCommitment(bytes32 commitment) external {
        require(!isRegistered[msg.sender], "Already registered");
        biometricCommitments[msg.sender] = commitment;
        isRegistered[msg.sender] = true;
        emit CommitmentRegistered(msg.sender, commitment);
    }

    function recordVerification(bytes32 proofHash, bytes32 txPayload, string calldata ipfsCid) external {
        auditTrail[msg.sender].push(VerificationEvent(proofHash, txPayload, block.timestamp, true, ipfsCid));
        totalVerifications++;
        emit IdentityVerified(msg.sender, proofHash, block.timestamp);
    }

    function logFraud(string calldata reason) external {
        totalFraudAttempts++;
        emit FraudAttemptLogged(msg.sender, block.timestamp, reason);
    }

    function getAuditTrail(address user) external view returns (VerificationEvent[] memory) {
        return auditTrail[user];
    }

    function getStats() external view returns (uint256, uint256) {
        return (totalVerifications, totalFraudAttempts);
    }
}
