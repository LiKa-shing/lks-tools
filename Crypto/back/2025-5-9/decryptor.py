from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization
import hashlib

def decrypt_file(
    input_path: str,
    output_path: str,
    private_key_path: str,
    password: str = None
) -> None:
    """解密文件(动态提取AES密钥)"""
    # 1. 打开输入文件，读取 header
    with open(input_path, "rb") as f_in:
        key_len = int.from_bytes(f_in.read(4), 'big')     # 4字节密钥长度
        encrypted_aes_key = f_in.read(key_len)            # RSA 加密后的 AES key
        iv = f_in.read(16)                                # 16字节 IV
        orig_hash = f_in.read(32)   # 读取加密时写入的源文件 SHA256

        # 2. 加载私钥
        with open(private_key_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=password.encode() if password else None
            )

        # 3. 解密出 AES_key
        aes_key = private_key.decrypt(
            encrypted_aes_key,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # 4. 构造 AES-CBC 解密器 和 PKCS7 去填充器
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()

        # 5. 分块解密并去填充，写入明文
        sha256 = hashlib.sha256()
        with open(output_path, "wb") as f_out:
            # 5.1 先对所有 decryptor.update() 的输出进行 unpadder.update()
            while True:
                chunk = f_in.read(1024 * 1024)
                if not chunk:
                    break
                decrypted = decryptor.update(chunk)
                # 解密后可能还包括填充字节，送给 unpadder
                f_out.write(unpadder.update(decrypted))
                sha256.update(unpadder.update(decrypted))

            # 5.2 finalize 解密器，处理残留的最后一块
            decrypted_final = decryptor.finalize()
            # 5.3 把最后一块也送给 unpadder，然后 finalize 去填充
            data = unpadder.update(decrypted_final)
            data += unpadder.finalize()
            f_out.write(data)
            sha256.update(data)

        if sha256.digest() != orig_hash:
            raise ValueError("文件校验失败：SHA256 不匹配！解密出的内容可能被篡改或损坏。")
