# decryptor+sha256
import hashlib
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization

def decrypt_file(
    input_path: str,
    output_path: str,
    private_key_path: str,
    password: str = None
) -> None:
    """解密文件（提取AES密钥、校验SHA256后输出）"""
    with open(input_path, "rb") as f_in:
        # 1. 读取 header
        key_len = int.from_bytes(f_in.read(4), 'big')    # 4字节密钥长度
        encrypted_aes_key = f_in.read(key_len)           # RSA 加密后的 AES key
        iv = f_in.read(16)                               # 16字节 IV
        orig_hash = f_in.read(32)   # 读取加密时写入的源文件 SHA256

        # 2. 加载私钥并解密出 AES key
        with open(private_key_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=password.encode() if password else None
            )
        aes_key = private_key.decrypt(
            encrypted_aes_key,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # 3. 构造解密器和去填充器
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()

        # 4. 流式解密并校验 SHA256
        sha256 = hashlib.sha256()
        with open(output_path, "wb") as f_out:
            # 4.1 读取并解密所有块
            while True:
                chunk = f_in.read(1024 * 1024)
                if not chunk:
                    break
                decrypted = decryptor.update(chunk)
                plain = unpadder.update(decrypted)
                f_out.write(plain)
                sha256.update(plain)

            # 4.2 finalize 解密器 & 去填充器
            decrypted_final = decryptor.finalize()
            data = unpadder.update(decrypted_final) + unpadder.finalize()
            f_out.write(data)
            sha256.update(data)

        # 5. 校验 SHA256
        if sha256.digest() != orig_hash:
            raise ValueError("文件校验失败：SHA256 不匹配！解密出的内容可能被篡改或损坏。")
