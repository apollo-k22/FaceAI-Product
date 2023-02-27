from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from os import urandom
from os import stat, remove, path

version = "1.0.0"
# default encryption/decryption buffer size - 64KB
bufferSizeDef = 64 * 1024

# maximum password length (number of chars)
maxPassLen = 1024

# AES block size in bytes
AESBlockSize = 16

# password stretching function
def stretch(passw, iv1):    
    # hash the external iv and the password 8192 times
    digest = iv1 + (16 * b"\x00")
    
    for i in range(8192):
        passHash = hashes.Hash(hashes.SHA256(), backend=default_backend())
        passHash.update(digest)
        passHash.update(bytes(passw, "utf_16_le"))
        digest = passHash.finalize()
    
    return digest

# decrypt file function
# arguments:
# infile: ciphertext file path
# outfile: plaintext file path
# passw: encryption password
# bufferSize: optional buffer size, must be a multiple of AES block size (16)
#             using a larger buffer speeds up things when dealing with
#             big files
#             Default is 64KB.
def decryptFile(infile, outfile, passw, bufferSize = bufferSizeDef):
    try:
        with open(infile, "rb") as fIn:
            # check that output file does not exist
            # or that, if exists, is not the same as the input file
            # (i.e.: overwrite if it seems safe)
            if path.isfile(outfile):
                if path.samefile(infile, outfile):
                    raise ValueError("Input and output files "
                                     "are the same.")
            try:
                with open(outfile, "wb") as fOut:
                    # get input file size
                    inputFileSize = stat(infile).st_size
                    try:
                        # decrypt file stream
                        decryptStream(fIn, fOut, passw, bufferSize,
                                      inputFileSize)
                    except ValueError as exd:
                        # should not remove output file here because it is still in use
                        # re-raise exception
                        raise ValueError(str(exd))
            
            except IOError:
                raise ValueError("Unable to write output file.")
            except ValueError as exd:
                # remove output file on error
                remove(outfile)
                # re-raise exception
                raise ValueError(str(exd))
                
    except IOError:
        raise ValueError("Unable to read input file.")
                    

# decrypt stream function
# arguments:
# fIn: input binary stream
# fOut: output binary stream
# passw: encryption password
# bufferSize: decryption buffer size, must be a multiple of AES block size (16)
#             using a larger buffer speeds up things when dealing with
#             long streams
# inputLength: input stream length
def decryptStream(fIn, fOut, passw, bufferSize, inputLength):
    # validate bufferSize
    if bufferSize % AESBlockSize != 0:
        raise ValueError("Buffer size must be a multiple of AES block size")
    
    if len(passw) > maxPassLen:
        raise ValueError("Password is too long.")

    fdata = fIn.read(6)
    # check if file is in AES Crypt format (also min length check)
    if (fdata != bytes("AES256", "utf8") or inputLength < 136):
            raise ValueError("File is corrupted or not an AES256 FaceAI "
                             "file.")
    
    # check if file is in AES Crypt format, version 2
    # (the only one compatible with pyAesCrypt)
    fdata = fIn.read(1)
    if len(fdata) != 1:
        raise ValueError("File is corrupted.")
    
    if fdata != b"\x02":
        raise ValueError("AES256 FaceAI is only compatible with version "
                         "2 of the AES256 file format.")
    
    # skip reserved byte
    fIn.read(1)
    
    # skip all the extensions
    while True:
        fdata = fIn.read(2)
        if len(fdata) != 2:
            raise ValueError("File is corrupted.")
        if fdata == b"\x00\x00":
            break
        fIn.read(int.from_bytes(fdata, byteorder="big"))
        
    # read external iv
    iv1 = fIn.read(16)
    if len(iv1) != 16:
        raise ValueError("File is corrupted.")
    
    # stretch password and iv
    key = stretch(passw, iv1)
    
    # read encrypted main iv and key
    c_iv_key = fIn.read(48)
    if len(c_iv_key) != 48:
        raise ValueError("File is corrupted.")
        
    # read HMAC-SHA256 of the encrypted iv and key
    hmac1 = fIn.read(32)
    if len(hmac1) != 32:
        raise ValueError("File is corrupted.")
    
    # compute actual HMAC-SHA256 of the encrypted iv and key
    hmac1Act = hmac.HMAC(key, hashes.SHA256(),
                         backend=default_backend())
    hmac1Act.update(c_iv_key)
    
    # HMAC check
    if hmac1 != hmac1Act.finalize():
        raise ValueError("Wrong password (or file is corrupted).")
    
    # instantiate AES cipher
    cipher1 = Cipher(algorithms.AES(key), modes.CBC(iv1),
                     backend=default_backend())
    decryptor1 = cipher1.decryptor()
    
    # decrypt main iv and key
    iv_key = decryptor1.update(c_iv_key) + decryptor1.finalize()
    
    # get internal iv and key
    iv0 = iv_key[:16]
    intKey = iv_key[16:]
    
    # instantiate another AES cipher
    cipher0 = Cipher(algorithms.AES(intKey), modes.CBC(iv0),
                     backend=default_backend())
    decryptor0 = cipher0.decryptor()
    
    # instantiate actual HMAC-SHA256 of the ciphertext
    hmac0Act = hmac.HMAC(intKey, hashes.SHA256(),
                         backend=default_backend())

    # decrypt ciphertext, until last block is reached
    while fIn.tell() < inputLength - 32 - 1 - AESBlockSize:
        # read data
        cText = fIn.read(
            min(
                bufferSize,
                inputLength - fIn.tell() - 32 - 1 - AESBlockSize
            )
        )
        # update HMAC
        hmac0Act.update(cText)
        # decrypt data and write it to output file
        fOut.write(decryptor0.update(cText))
        
    # last block reached, remove padding if needed
    
    # read last block
    
    # this is for empty files
    if fIn.tell() != inputLength - 32 - 1:
        cText = fIn.read(AESBlockSize)
        if len(cText) < AESBlockSize:
            raise ValueError("File is corrupted.")
    else:
        cText = bytes()
    
    # update HMAC
    hmac0Act.update(cText)
    
    # read plaintext file size mod 16 lsb positions
    fs16 = fIn.read(1)
    if len(fs16) != 1:
        raise ValueError("File is corrupted.")
    
    # decrypt last block
    pText = decryptor0.update(cText) + decryptor0.finalize()
    
    # remove padding
    toremove = ((16 - fs16[0]) % 16)
    if toremove != 0:
        pText = pText[:-toremove]
        
    # write decrypted data to output file
    fOut.write(pText)
    
    # read HMAC-SHA256 of the encrypted file
    hmac0 = fIn.read(32)
    if len(hmac0) != 32:
        raise ValueError("File is corrupted.")
    
    # HMAC check
    if hmac0 != hmac0Act.finalize():
        raise ValueError("Bad HMAC (file is corrupted).")   
