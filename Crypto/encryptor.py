# encryptor+sha256
import os
import hashlib
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization

def encrypt_file(
    input_path: str,
    output_path: str,
    public_key_path: str
) -> None:
    """加密文件(自动生成临时AES密钥, 与加密数据合并存储)，并写入源文件SHA256以供校验"""
    # 1. 先计算源文件的 SHA256
    sha256 = hashlib.sha256()
    with open(input_path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            sha256.update(chunk)
    file_hash = sha256.digest()   # 32 字节

    # 2. 生成临时AES密钥和IV
    aes_key = os.urandom(32)      # AES-256
    iv = os.urandom(16)           # CBC模式初始化向量

    # 3. 加载公钥并加密 AES 密钥
    with open(public_key_path, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())
    encrypted_aes_key = public_key.encrypt(
        aes_key,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # 4. 写入头部 metadata + 文件内容
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(algorithms.AES.block_size).padder()

    with open(input_path, "rb") as f_in, open(output_path, "wb") as f_out:
        # 4.1 写入：4字节密钥长度 + 加密后的 AES key + IV + 32字节文件 SHA256
        f_out.write(len(encrypted_aes_key).to_bytes(4, 'big'))
        f_out.write(encrypted_aes_key)
        f_out.write(iv)
        f_out.write(file_hash)

        # 4.2 分块读源文件，加密写出
        while True:
            chunk = f_in.read(1024 * 1024)
            if not chunk:
                break
            padded = padder.update(chunk)
            f_out.write(encryptor.update(padded))
        # 4.3 最后一块填充并 finalize
        final_padded = padder.finalize()
        f_out.write(encryptor.update(final_padded) + encryptor.finalize())
