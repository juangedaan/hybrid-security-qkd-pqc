#!/usr/bin/env python3

import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


def combine_keys(key1: bytes, key2: bytes) -> bytes:
    # simple XOR combine (bitwise)
    return bytes(a ^ b for a, b in zip(key1, key2))


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


if __name__ == "__main__":
    # simulate QKD by generating a random symmetric key
    key_qkd = get_random_bytes(16)
    print(f"QKD key: {key_qkd.hex()}")

    # simulate a PQC step using an RSA key pair (placeholder for lattice/KEM)
    from Crypto.PublicKey import RSA

    rsa_key = RSA.generate(2048)
    # encrypt a random session key with the RSA public key
    session_key = get_random_bytes(16)
    encrypted_session = rsa_key.publickey().encrypt(session_key, None)[0]
    decrypted_session = rsa_key.decrypt(encrypted_session)
    print(f"PQC-derived key: {decrypted_session.hex()}")

    # combine the QKD and PQC keys to form a hybrid key
    hybrid_key = combine_keys(key_qkd, decrypted_session)
    print(f"Hybrid key: {hybrid_key.hex()}")

    # use the hybrid key for symmetric AES encryption
    message = b"Secret message"
    encrypted = encrypt(message, hybrid_key)
    print(f"Encrypted: {encrypted.hex()}")

    decrypted = decrypt(encrypted, hybrid_key)
    print(f"Decrypted: {decrypted}")
