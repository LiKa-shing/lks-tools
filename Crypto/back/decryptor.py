def decrypt_file(input_path, output_path, private_key_path, password=None):
    """解密文件(动态提取AES密钥)"""
    with open(input_path, "rb") as f_in:
        # 读取元数据
        key_len = int.from_bytes(f_in.read(4), 'big')  # 读取密钥长度头
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
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # 用AES解密数据
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        
        with open(output_path, "wb") as f_out:
            while True:
                chunk = f_in.read(1024 * 1024)
                if not chunk:
                    break
                f_out.write(decryptor.update(chunk))
            # 处理填充
            final_data = decryptor.finalize()
            unpadder = padding.PKCS7(128).unpadder()
            f_out.write(unpadder.update(final_data) + unpadder.finalize())

# 如果私钥有密码则传入
#decrypt_file("secret.rar.enc", "decrypted.rar", "rsa_private.pem", password="your_privkey_pass")