# Cryptography and Security
import hashlib
import hmac
import secrets
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import bcrypt
import jwt
import ssl
import socket

def hash_operations():
    """Various hashing operations"""
    data = b"Hello, World!"
    
    # MD5 hash
    md5_hash = hashlib.md5(data).hexdigest()
    
    # SHA-256 hash
    sha256_hash = hashlib.sha256(data).hexdigest()
    
    # HMAC
    secret_key = secrets.token_bytes(32)
    hmac_hash = hmac.new(secret_key, data, hashlib.sha256).hexdigest()
    
    return {
        'md5': md5_hash,
        'sha256': sha256_hash,
        'hmac': hmac_hash
    }

def password_security():
    """Password hashing and verification"""
    password = "secure_password123"
    
    # bcrypt hashing
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    # Verification
    is_valid = bcrypt.checkpw(password.encode('utf-8'), hashed_password)
    
    return {
        'hashed': hashed_password.decode('utf-8'),
        'is_valid': is_valid
    }

def symmetric_encryption():
    """Symmetric encryption using Fernet"""
    # Generate key
    key = Fernet.generate_key()
    cipher = Fernet(key)
    
    # Encrypt data
    message = b"This is a secret message"
    encrypted_message = cipher.encrypt(message)
    
    # Decrypt data
    decrypted_message = cipher.decrypt(encrypted_message)
    
    return {
        'key': key.decode('utf-8'),
        'encrypted': encrypted_message.decode('utf-8'),
        'decrypted': decrypted_message.decode('utf-8')
    }

def asymmetric_encryption():
    """Asymmetric encryption using RSA"""
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    # Get public key
    public_key = private_key.public_key()
    
    # Encrypt message
    message = b"Asymmetric encryption test"
    encrypted = public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    # Decrypt message
    decrypted = private_key.decrypt(
        encrypted,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    return {
        'original': message.decode('utf-8'),
        'decrypted': decrypted.decode('utf-8'),
        'match': message == decrypted
    }

def jwt_operations():
    """JWT token operations"""
    secret_key = "your-secret-key"
    payload = {
        'user_id': 123,
        'username': 'john_doe',
        'exp': 1234567890
    }
    
    # Encode JWT
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    
    # Decode JWT
    try:
        decoded_payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        is_valid = True
    except jwt.InvalidTokenError:
        decoded_payload = None
        is_valid = False
    
    return {
        'token': token,
        'payload': decoded_payload,
        'is_valid': is_valid
    }

def secure_random_generation():
    """Secure random number and string generation"""
    # Secure random bytes
    random_bytes = secrets.token_bytes(16)
    
    # Secure random hex string
    random_hex = secrets.token_hex(16)
    
    # Secure random URL-safe string
    random_url_safe = secrets.token_urlsafe(16)
    
    # Random integer
    random_int = secrets.randbelow(1000)
    
    return {
        'bytes': base64.b64encode(random_bytes).decode('utf-8'),
        'hex': random_hex,
        'url_safe': random_url_safe,
        'integer': random_int
    }

def ssl_certificate_check(hostname, port=443):
    """Check SSL certificate"""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                return {
                    'subject': dict(x[0] for x in cert['subject']),
                    'issuer': dict(x[0] for x in cert['issuer']),
                    'version': cert['version'],
                    'serial_number': cert['serialNumber']
                }
    except Exception as e:
        return {'error': str(e)}

def main():
    print("Running cryptographic operations...")
    
    # Hash operations
    hashes = hash_operations()
    print(f"SHA-256 hash length: {len(hashes['sha256'])}")
    
    # Password security
    password_result = password_security()
    print(f"Password validation: {password_result['is_valid']}")
    
    # Symmetric encryption
    symmetric_result = symmetric_encryption()
    print(f"Symmetric encryption successful: {symmetric_result['decrypted'] == 'This is a secret message'}")
    
    # Asymmetric encryption
    asymmetric_result = asymmetric_encryption()
    print(f"Asymmetric encryption successful: {asymmetric_result['match']}")
    
    # JWT operations
    jwt_result = jwt_operations()
    print(f"JWT validation: {jwt_result['is_valid']}")
    
    # Secure random generation
    random_result = secure_random_generation()
    print(f"Generated random integer: {random_result['integer']}")
    
    # SSL certificate check
    ssl_result = ssl_certificate_check('httpbin.org')
    if 'error' not in ssl_result:
        print(f"SSL certificate subject: {ssl_result['subject'].get('commonName', 'N/A')}")
    else:
        print(f"SSL check failed: {ssl_result['error']}")

if __name__ == "__main__":
    main()