# hash_utils.py
import hashlib
import gzip

def calculate_sha1_hashes(data, compressed_data):
    sha1_uncompressed = hashlib.sha1(data.encode()).hexdigest()
    sha1_compressed = hashlib.sha1(compressed_data).hexdigest()
    return sha1_uncompressed, sha1_compressed