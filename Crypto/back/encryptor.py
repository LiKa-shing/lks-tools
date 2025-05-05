from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

def encrypt_file(input_path, output_path, public_key_path):
    """加密文件(自动生成临时AES密钥, 与加密数据合并存储)"""
    # 生成临时AES密钥（使用后立即丢弃）
    aes_key = os.urandom(32)  # AES-256
    iv = os.urandom(16)       # CBC模式初始化向量
    
    # 加载RSA公钥
    with open(public_key_path, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())
    
    # 用RSA加密AES密钥
    encrypted_aes_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    # 用AES加密文件
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    
    with open(input_path, "rb") as f_in, open(output_path, "wb") as f_out:
        # 写入加密元数据（RSA加密的AES密钥 + IV）
        f_out.write(len(encrypted_aes_key).to_bytes(4, 'big'))  # 密钥长度头
        f_out.write(encrypted_aes_key)
        f_out.write(iv)
        
        # 加密并写入数据
        while True:
            chunk = f_in.read(1024 * 1024)  # 1MB分块
            if not chunk:
                break
            # PKCS7填充
            padder = padding.PKCS7(128).padder()
            padded_chunk = padder.update(chunk) + padder.finalize()
            f_out.write(encryptor.update(padded_chunk))
        f_out.write(encryptor.finalize())

# 加密RAR文件
#encrypt_file("secret.rar", "secret.rar.enc", "rsa_public.pem")