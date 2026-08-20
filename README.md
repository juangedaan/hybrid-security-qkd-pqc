# Hybrid Security QKD + PQC Demo

A comprehensive simulation of hybrid quantum-safe cryptography combining Quantum Key Distribution (QKD) with Post-Quantum Cryptography (PQC). The script demonstrates a complete key exchange protocol with ML-KEM-768 (Kyber) key encapsulation, ML-DSA-65 (Dilithium) signatures, and AES encryption.

```mermaid
sequenceDiagram
    participant Alice
    participant Bob

    Note over Alice,Bob: Phase 1 - QKD (BB84 simulation)
    Alice->>Bob: Qubits in random bases (rectilinear/diagonal)
    Bob->>Alice: Measurement bases used
    Note over Alice,Bob: Sift bits where bases match -> shared 256-bit QKD key

    Note over Alice,Bob: Phase 2 - PQC key encapsulation
    Bob->>Alice: ML-KEM-768 public key
    Note over Alice: Encapsulate -> KEM secret + ciphertext
    Alice->>Bob: KEM ciphertext
    Note over Bob: Decapsulate -> same KEM secret

    Note over Alice,Bob: Phase 3 - Hybrid key derivation
    Note over Alice: hybrid key = HKDF(QKD key, KEM secret)
    Note over Bob: hybrid key = HKDF(QKD key, KEM secret)
    Note over Alice,Bob: Both parties hold the same hybrid key

    Note over Alice,Bob: Phase 4 - Authentication
    Bob->>Alice: ML-DSA-65 signature over hybrid key, plus signing public key
    Note over Alice: Verify signature

    Note over Alice,Bob: Phase 5 - Secure messaging
    Alice->>Bob: Message encrypted with AES-EAX under hybrid key
    Note over Bob: Decrypt and verify tag
```

## 📂 Structure

```
hybrid-security-qkd-pqc/
├── README.md
├── requirements.txt
├── hybrid.py  # Full hybrid protocol simulation with classes and crypto
```

## 🚀 Usage

```bash
python hybrid.py
```

Runs the complete hybrid key exchange — both parties derive the same hybrid key — and demonstrates secure message encryption/decryption.

## 🏗️ Protocol Phases

- **QKD Phase**: Simulates BB84 quantum key distribution (random bases, sifting) over an ideal channel
- **PQC Phase**: ML-KEM-768 (Kyber) for key encapsulation + ML-DSA-65 (Dilithium) for signatures — NIST post-quantum standards, pure-Python via `kyber-py` and `dilithium-py`
- **Hybrid Phase**: Combines the QKD and KEM secrets using HKDF-like derivation
- **Encryption Phase**: AES-EAX symmetric encryption with hybrid key

## 📜 License

MIT License
