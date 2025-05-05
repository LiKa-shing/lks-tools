import argparse
from cryptography.hazmat.primitives import serialization, hashes, padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
import sys

# --------------------------
# 核心加密/解密函数
# --------------------------

def encrypt_file(input_path, output_path, public_key_path):
    """加密文件"""
    try:
        # 生成临时AES密钥
        aes_key = os.urandom(32)
        iv = os.urandom(16)

        # 加载RSA公钥
        with open(public_key_path, "rb") as f:
            public_key = serialization.load_pem_public_key(f.read())

        # 加密AES密钥
        encrypted_aes_key = public_key.encrypt(
            aes_key,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # 加密数据
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(128).padder()

        with open(input_path, "rb") as f_in, open(output_path, "wb") as f_out:
            # 写入元数据
            f_out.write(len(encrypted_aes_key).to_bytes(4, 'big'))
            f_out.write(encrypted_aes_key)
            f_out.write(iv)

            # 加密并写入数据
            while True:
                chunk = f_in.read(1024 * 1024)  # 1MB chunks
                if not chunk:
                    break
                padded_chunk = padder.update(chunk)
                f_out.write(encryptor.update(padded_chunk))
            
            # 处理最后一块
            final_padded = padder.finalize()
            f_out.write(encryptor.update(final_padded))
            f_out.write(encryptor.finalize())

        print(f"加密成功：{input_path} -> {output_path}")

    except Exception as e:
        print(f"加密失败：{str(e)}")
        sys.exit(1)

def decrypt_file(input_path, output_path, private_key_path, password=None):
    """解密文件"""
    try:
        with open(input_path, "rb") as f_in:
            # 读取元数据
            key_len = int.from_bytes(f_in.read(4), 'big')
            encrypted_aes_key = f_in.read(key_len)
            iv = f_in.read(16)

            # 加载RSA私钥
            with open(private_key_path, "rb") as f:
                private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=password.encode() if password else None
                )

            # 解密AES密钥
            aes_key = private_key.decrypt(
                encrypted_aes_key,
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            # 解密数据
            cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
            decryptor = cipher.decryptor()
            unpadder = padding.PKCS7(128).unpadder()

            with open(output_path, "wb") as f_out:
                while True:
                    chunk = f_in.read(1024 * 1024)
                    if not chunk:
                        break
                    f_out.write(decryptor.update(chunk))
                
                # 处理最后一块
                final_data = decryptor.finalize()
                unpadded_data = unpadder.update(final_data) + unpadder.finalize()
                f_out.write(unpadded_data)

        print(f"解密成功：{input_path} -> {output_path}")

    except Exception as e:
        print(f"解密失败：{str(e)}")
        sys.exit(1)

# --------------------------
# 命令行接口
# --------------------------

def main():
    parser = argparse.ArgumentParser(description="文件加密/解密工具")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 加密命令
    encrypt_parser = subparsers.add_parser('encrypt', help="加密文件")
    encrypt_parser.add_argument('-i', '--input', required=True, help="输入文件路径")
    encrypt_parser.add_argument('-o', '--output', required=True, help="输出文件路径")
    encrypt_parser.add_argument('-k', '--public-key', required=True, help="RSA公钥路径")

    # 解密命令
    decrypt_parser = subparsers.add_parser('decrypt', help="解密文件")
    decrypt_parser.add_argument('-i', '--input', required=True, help="输入文件路径")
    decrypt_parser.add_argument('-o', '--output', required=True, help="输出文件路径")
    decrypt_parser.add_argument('-k', '--private-key', required=True, help="RSA私钥路径")
    decrypt_parser.add_argument('-p', '--password', help="私钥密码（可选）")

    args = parser.parse_args()

    if args.command == 'encrypt':
        encrypt_file(args.input, args.output, args.public_key)
    elif args.command == 'decrypt':
        decrypt_file(args.input, args.output, args.private_key, args.password)

if __name__ == "__main__":
    main()