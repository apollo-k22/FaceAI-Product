import pyaes, pbkdf2, binascii, os, secrets
import os
import time
import pyAesCrypt

# AES supports multiple key sizes: 16 (AES128), 24 (AES192), or 32 (AES256).
bufferSize = 64 * 1024
keypath = r".\key.key"

# Generating 32-byte key and return generated key
def generate_key():
    password = "s3cr3t*c0d3"
    passwordSalt = os.urandom(16)
    key = pbkdf2.PBKDF2(password, passwordSalt).read(32)
    print(binascii.hexlify(key))
    return key, binascii.hexlify(key)

# Generating 16-byte key and return generated key
def generate_token():
    password = "s3cr3t*c0d3"
    passwordSalt = os.urandom(16)
    key = pbkdf2.PBKDF2(password, passwordSalt).read(16)
    # print(binascii.hexlify(key))
    return key, binascii.hexlify(key)

def encrypt(folder_path):
    with open(keypath, 'rb') as f:
        key = f.read()
    print(key)

    encfiles = []
    try: 
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                encfiles.append(os.path.join(root, filename))
        for encfile in encfiles:
            try:
                pyAesCrypt.encryptFile(encfile, encfile+".enc", str(key), bufferSize)
                os.remove(encfile)
            except Exception:
                print("Encrypt Error1")
                return False
    except:
        print("Encrypt Error2")
        return False

    return True

def decrypt(folder_path):
    with open(keypath, 'rb') as f:
        key = f.read()
    print(key)

    decfiles = []
    try: 
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                decfiles.append(os.path.join(root, filename))

        for decfile in decfiles:
            try:
                pyAesCrypt.decryptFile(decfile, decfile.replace(".enc",""), str(key), bufferSize)
                os.remove(decfile)
            except Exception:
                print("Decrypt Error1")
                return False
    except:
        print("Decrypt Error2")
        return False

    return True
