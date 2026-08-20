#!/usr/bin/env python3

import secrets
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA, ECC
from Crypto.Hash import SHA256
from Crypto.Signature import DSS
import time
from dataclasses import dataclass
from typing import Tuple

@dataclass
class KeyExchangeResult:
    shared_secret: bytes
    public_key: bytes
    signature: bytes = None

class QuantumKeyDistribution:
    """Simulate the BB84 QKD protocol over an ideal (noise-free) quantum channel."""
    def __init__(self):
        self.key_length = 256

    def generate_key(self) -> bytes:
        print("🔑 Simulating QKD (BB84): Alice sends qubits, Bob measures...")
        sifted_bits = []
        qubits_sent = 0
        while len(sifted_bits) < self.key_length:
            alice_bit = secrets.randbits(1)
            alice_basis = secrets.randbits(1)   # 0 = rectilinear, 1 = diagonal
            bob_basis = secrets.randbits(1)
            qubits_sent += 1
            # Sifting: keep the bit only when Bob measured in Alice's basis.
            # Ideal channel and no eavesdropper, so Bob reads the bit correctly.
            if alice_basis == bob_basis:
                sifted_bits.append(alice_bit)
        key = bytes(
            int("".join(map(str, sifted_bits[i:i + 8])), 2)
            for i in range(0, self.key_length, 8)
        )
        print(f"   Qubits sent: {qubits_sent}, sifted key: {len(key)*8} bits")
        return key

class PostQuantumCryptography:
    """Simulate PQC primitives"""
    def __init__(self):
        self.rsa_key = RSA.generate(2048)
        self.ecc_key = ECC.generate(curve='P-256')

    def rsa_kem(self, message: bytes) -> Tuple[bytes, bytes]:
        """RSA-based Key Encapsulation Mechanism simulation"""
        print("🔐 PQC: RSA-KEM key encapsulation...")
        cipher = PKCS1_OAEP.new(self.rsa_key.publickey())
        return cipher.encrypt(message), self.rsa_key.publickey().export_key()

    def rsa_kem_decrypt(self, encrypted: bytes) -> bytes:
        """Decrypt RSA-KEM"""
        return PKCS1_OAEP.new(self.rsa_key).decrypt(encrypted)

    def ecc_sign(self, data: bytes) -> bytes:
        """ECC digital signature"""
        print("✍️ PQC: ECC digital signature...")
        h = SHA256.new(data)
        signer = DSS.new(self.ecc_key, 'fips-186-3')
        signature = signer.sign(h)
        return signature

    def ecc_verify(self, data: bytes, signature: bytes, pub_key) -> bool:
        """Verify ECC signature"""
        h = SHA256.new(data)
        verifier = DSS.new(pub_key, 'fips-186-3')
        try:
            verifier.verify(h, signature)
            return True
        except:
            return False

def combine_keys(key1: bytes, key2: bytes) -> bytes:
    """HKDF-like key derivation: hash both keys so all entropy is used"""
    return SHA256.new(key1 + key2).digest()[:16]  # 128-bit key

def encrypt(message: bytes, key: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(message)
    return cipher.nonce + tag + ciphertext

def decrypt(encrypted: bytes, key: bytes) -> bytes:
    nonce = encrypted[:16]
    tag = encrypted[16:32]
    ciphertext = encrypted[32:]
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)

def simulate_hybrid_protocol() -> KeyExchangeResult:
    print("🚀 Starting Hybrid QKD + PQC Protocol Simulation\n")

    # Phase 1: QKD
    qkd = QuantumKeyDistribution()
    qkd_key = qkd.generate_key()

    # Phase 2: PQC Key Exchange
    pqc = PostQuantumCryptography()
    session_key = get_random_bytes(16)
    encrypted_session, pub_key = pqc.rsa_kem(session_key)
    decrypted_session = pqc.rsa_kem_decrypt(encrypted_session)

    # Phase 3: Combine keys
    hybrid_key = combine_keys(qkd_key, decrypted_session)
    print(f"Hybrid key: {hybrid_key.hex()}")

    # Phase 4: Sign the hybrid key, then verify
    signature = pqc.ecc_sign(hybrid_key)
    assert pqc.ecc_verify(hybrid_key, signature, pqc.ecc_key.public_key())
    print("   Signature verified ✔")

    return KeyExchangeResult(
        shared_secret=hybrid_key,
        public_key=pub_key,
        signature=signature
    )

if __name__ == "__main__":
    result = simulate_hybrid_protocol()

    # Demonstrate encryption with hybrid key
    message = b"Highly sensitive quantum-secure message"
    print(f"\n📨 Original message: {message.decode()}")

    encrypted = encrypt(message, result.shared_secret)
    print(f"Encrypted: {encrypted.hex()[:50]}...")

    decrypted = decrypt(encrypted, result.shared_secret)
    print(f"Decrypted: {decrypted.decode()}")

    print("\n✅ Hybrid protocol completed successfully!")
    print("🔒 Message secured with QKD + PQC + AES")
