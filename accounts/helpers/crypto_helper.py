import base64
from cryptography.fernet import Fernet
from ProcureBOApp.settings import SECRET_KEY


# =========================
# Generate Key
# =========================
key = base64.urlsafe_b64encode(
    SECRET_KEY[:32].encode().ljust(32, b'0')
)

cipher = Fernet(key)


# =========================
# Encrypt Text (30 chars)
# =========================
def encrypt_text(text):

    if not text:
        return ""

    encrypted = cipher.encrypt(
        text.encode()
    ).decode()

    # Return only 30 characters
    return encrypted[:30]


# =========================
# Decrypt Text
# =========================
def decrypt_text(encrypted_text):

    if not encrypted_text:
        return ""

    decrypted = cipher.decrypt(
        encrypted_text.encode()
    ).decode()

    return decrypted