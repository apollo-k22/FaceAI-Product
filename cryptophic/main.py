import pyaes, pbkdf2, binascii, os, secrets

# AES supports multiple key sizes: 16 (AES128), 24 (AES192), or 32 (AES256).
key_bytes = 32

# Generating 32-byte key and return generated key
def generate_key():
    password = "s3cr3t*c0d3"
    passwordSalt = os.urandom(16)
    key = pbkdf2.PBKDF2(password, passwordSalt).read(32)
    # print(binascii.hexlify(key))
    return key, binascii.hexlify(key)

# Generating 16-byte key and return generated key
def generate_token():
    password = "s3cr3t*c0d3"
    passwordSalt = os.urandom(16)
    key = pbkdf2.PBKDF2(password, passwordSalt).read(16)
    # print(binascii.hexlify(key))
    return key, binascii.hexlify(key)

# Takes as input a 32-byte key and an arbitrary-length plaintext and returns a
# pair (iv, ciphtertext). "iv" stands for initialization vector.
def encrypt(key, plaintext):
    assert len(key) == key_bytes
    iv = secrets.randbits(256)
    aes = pyaes.AESModeOfOperationCTR(key, pyaes.Counter(iv))
    ciphertext = aes.encrypt(plaintext)    
    return (iv, ciphertext)

# Takes as input a 32-byte key, a 16-byte IV, and a ciphertext, and outputs the
# corresponding plaintext.
def decrypt(key, iv, ciphertext):
    assert len(key) == key_bytes
    aes = pyaes.AESModeOfOperationCTR(key, pyaes.Counter(iv))
    plaintext = aes.decrypt(ciphertext)
    return plaintext
