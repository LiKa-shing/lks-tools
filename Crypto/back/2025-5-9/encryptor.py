from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization
import os
import hashlib

def encrypt_file(
    input_path: str,
    output_path: str,
    public_key_path: str
) -> None:
    """加密文件(自动生成临时AES密钥, 与加密数据合并存储)"""
    # 计算源文件的 SHA256, 供后续校验
    sha256 = hashlib.sha256()
    with open(input_path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            sha256.update(chunk)
    file_hash = sha256.digest()   # 32 字节

    # 生成临时AES密钥（使用后立即丢弃）
    aes_key = os.urandom(32)  # AES-256
    iv = os.urandom(16) # CBC模式初始化向量
    
    # 加载公钥
    with open(public_key_path, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())
    
    # 加密AES密钥
    encrypted_aes_key = public_key.encrypt(
        aes_key,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    # 加密数据
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    
    with open(input_path, "rb") as f_in, open(output_path, "wb") as f_out:
        # 写入加密元数据（加密的AES密钥 + IV）
        f_out.write(len(encrypted_aes_key).to_bytes(4, 'big')) #密钥长度头
        f_out.write(encrypted_aes_key)
        f_out.write(iv)
        f_out.write(file_hash)
        # 加密并写入数据
        while True:
            chunk = f_in.read(1024 * 1024)  # 1MB分块
            if not chunk:
                break
            padded_chunk = padder.update(chunk)
            f_out.write(encryptor.update(padded_chunk))
        
        final_padded = padder.finalize()
        f_out.write(encryptor.update(final_padded) + encryptor.finalize())