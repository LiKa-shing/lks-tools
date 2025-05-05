from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_keypair(
    private_key_path: str = "private.pem",
    public_key_path: str = "public.pem",
    key_size: int = 2048,
    password: str = None
) -> None:
    """生成RSA密钥对"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size
    )
    
    # 保存私钥
    encryption_algorithm = (
        serialization.BestAvailableEncryption(password.encode())
        if password else serialization.NoEncryption()
    )
    with open(private_key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm
        ))
    
    # 保存公钥
    public_key = private_key.public_key()
    with open(public_key_path, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))