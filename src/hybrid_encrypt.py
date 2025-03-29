
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib

from qkd import generate_qkd_key
from pqc import pqc_key_exchange

def derive_hybrid_key(qkd_key, pqc_key):
    combined = qkd_key + pqc_key
    return hashlib.sha256(combined).digest()

def hybrid_encrypt(msg: str, key: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(msg.encode(), AES.block_size))
    return cipher.iv + ct_bytes

def hybrid_decrypt(ciphertext: bytes, key: bytes) -> str:
    iv = ciphertext[:16]
    ct = ciphertext[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct), AES.block_size).decode()

if __name__ == "__main__":
    qkd_key = generate_qkd_key()
    pqc_key = pqc_key_exchange()
    hybrid_key = derive_hybrid_key(qkd_key, pqc_key)

    message = "This is a top secret message."
    encrypted = hybrid_encrypt(message, hybrid_key)
    decrypted = hybrid_decrypt(encrypted, hybrid_key)

    print("Original:", message)
    print("Encrypted (hex):", encrypted.hex())
    print("Decrypted:", decrypted)
