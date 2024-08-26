import hashlib

def calculate_sha1_uncompressed(data):
    return hashlib.sha1(data).hexdigest()

def calculate_sha1_compressed(data):
    return hashlib.sha1(data).hexdigest()