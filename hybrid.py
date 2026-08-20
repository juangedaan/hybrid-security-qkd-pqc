#!/usr/bin/env python3

import secrets
from dataclasses import dataclass

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from kyber_py.ml_kem import ML_KEM_768
from dilithium_py.ml_dsa import ML_DSA_65

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
    """NIST post-quantum primitives: ML-KEM-768 (Kyber) and ML-DSA-65 (Dilithium)"""
    def __init__(self):
        self.kem_ek, self.kem_dk = ML_KEM_768.keygen()
        self.sig_pk, self.sig_sk = ML_DSA_65.keygen()

    @staticmethod
    def kem_encaps(ek: bytes) -> tuple:
        """Encapsulate against the receiver's public key -> (shared secret, ciphertext)"""
        print("🔐 PQC: ML-KEM-768 key encapsulation...")
        return ML_KEM_768.encaps(ek)

    def kem_decaps(self, ciphertext: bytes) -> bytes:
        """Recover the shared secret with the private key"""
        return ML_KEM_768.decaps(self.kem_dk, ciphertext)

    def sign(self, data: bytes) -> bytes:
        """ML-DSA-65 digital signature"""
        print("✍️ PQC: ML-DSA-65 digital signature...")
        return ML_DSA_65.sign(self.sig_sk, data)

    @staticmethod
    def verify(data: bytes, signature: bytes, pub_key: bytes) -> bool:
        return ML_DSA_65.verify(pub_key, data, signature)

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

    # Phase 1: QKD — Alice and Bob agree on a quantum key via BB84
    qkd_key = QuantumKeyDistribution().generate_key()

    # Phase 2: PQC KEM — Alice encapsulates against Bob's ML-KEM public key
    bob = PostQuantumCryptography()
    alice_secret, ciphertext = PostQuantumCryptography.kem_encaps(bob.kem_ek)
    bob_secret = bob.kem_decaps(ciphertext)

    # Phase 3: Both parties derive the hybrid key independently
    alice_key = combine_keys(qkd_key, alice_secret)
    bob_key = combine_keys(qkd_key, bob_secret)
    assert alice_key == bob_key, "Hybrid key mismatch!"
    print(f"Hybrid key (both parties agree): {alice_key.hex()}")

    # Phase 4: Sign the hybrid key transcript, then verify
    signature = bob.sign(alice_key)
    assert PostQuantumCryptography.verify(alice_key, signature, bob.sig_pk)
    print("   Signature verified ✔")

    return KeyExchangeResult(
        shared_secret=alice_key,
        public_key=bob.kem_ek,
        signature=signature,
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
