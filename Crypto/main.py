import argparse
from key_generator import generate_keypair
from encryptor import encrypt_file
from decryptor import decrypt_file

def main():
    parser = argparse.ArgumentParser(description="文件加密套件")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 生成密钥对
    gen_parser = subparsers.add_parser('genkeys', help="生成RSA密钥对")
    gen_parser.add_argument('--private', default='private.pem', help="私钥保存路径")
    gen_parser.add_argument('--public', default='public.pem', help="公钥保存路径")
    gen_parser.add_argument('--size', type=int, default=2048, help="密钥长度（默认2048）")
    gen_parser.add_argument('--password', help="私钥密码（可选）")

    # 加密文件
    enc_parser = subparsers.add_parser('encrypt', help="加密文件")
    enc_parser.add_argument('-i', '--input', required=True, help="输入文件路径")
    enc_parser.add_argument('-o', '--output', required=True, help="输出文件路径")
    enc_parser.add_argument('-k', '--pubkey', required=True, help="公钥文件路径")

    # 解密文件
    dec_parser = subparsers.add_parser('decrypt', help="解密文件")
    dec_parser.add_argument('-i', '--input', required=True, help="输入文件路径")
    dec_parser.add_argument('-o', '--output', required=True, help="输出文件路径")
    dec_parser.add_argument('-k', '--privkey', required=True, help="私钥文件路径")
    dec_parser.add_argument('-p', '--password', help="私钥密码（可选）")

    args = parser.parse_args()

    if args.command == 'genkeys':
        generate_keypair(
            private_key_path=args.private,
            public_key_path=args.public,
            key_size=args.size,
            password=args.password
        )
    elif args.command == 'encrypt':
        encrypt_file(args.input, args.output, args.pubkey)
    elif args.command == 'decrypt':
        decrypt_file(args.input, args.output, args.privkey, args.password)

if __name__ == "__main__":
    main()