"""
Cryptography Key Generator Module
=================================
提供非对称(RSA)和对称(AES)密钥的生成功能。
"""
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os

# 非对称加密密钥生成
def generate_rsa_keypair(private_key_path="private_key.pem", 
                        public_key_path="public_key.pem", 
                        key_size=2048,
                        password=None):
    """
    生成RSA密钥对并保存到文件
    :param private_key_path: 私钥保存路径
    :param public_key_path: 公钥保存路径
    :param key_size: 密钥长度(默认2048)
    :param password: 私钥加密密码(None表示不加密)
    :return: (private_key, public_key) 密钥对象
    """
    # 生成私钥
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size
    )
    
    # 提取公钥
    public_key = private_key.public_key()
    
    # 序列化私钥
    encryption_algorithm = serialization.NoEncryption()
    if password:
        encryption_algorithm = serialization.BestAvailableEncryption(password.encode())
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption_algorithm
    )
    
    # 保存私钥
    with open(private_key_path, "wb") as f:
        f.write(private_pem)
    
    # 序列化并保存公钥
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(public_key_path, "wb") as f:
        f.write(public_pem)
    
    return private_key, public_key

# 对称加密密钥生成
def generate_aes_key(key_length=32):
    """
    生成随机AES密钥(默认256位)
    :param key_length: 密钥字节长度(16=128位, 32=256位)
    :return: 字节类型的AES密钥
    """
    if key_length not in [16, 24, 32]:
        raise ValueError("AES密钥长度必须是16/24/32字节(对应128/192/256位)")
    return os.urandom(key_length)
